import AppKit
import Security
import SwiftUI
import UniformTypeIdentifiers
import Vision

private let defaultVaultPath = "/Volumes/KINGSTON 2/apps/apps/corretor de redação/corretor x/11 - Corretor X Redação ENEM"

@main
struct XTRIRedApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
                .frame(minWidth: 980, minHeight: 680)
        }
        .windowStyle(.titleBar)
    }
}

struct EssayCase: Identifiable, Hashable, Sendable {
    let id: String
    let caseID: String
    let directoryName: String
    let studentName: String
    let title: String
    let theme: String
    let statusOCR: String
    let entryURL: URL
    let exportURL: URL
    let hasExport: Bool
    let hasTranscription: Bool
    let isReadyForCorrection: Bool
    let canRunOCR: Bool
}

struct ProcessResult: Sendable {
    let exitCode: Int32
    let output: String
}

struct ImportSummary: Sendable {
    let created: Int
    let readyForCorrection: Int
    let pendingOCR: Int
    let skipped: Int
    let firstCaseDirectory: String?
    let lastCaseID: String?

    var logMessage: String {
        var lines = [
            "Importação concluída.",
            "Casos criados: \(created)",
            "Prontos para correção: \(readyForCorrection)",
            "Aguardando OCR/revisão: \(pendingOCR)",
            "Arquivos ignorados: \(skipped)"
        ]
        if let lastCaseID {
            lines.append("Último caso: \(lastCaseID)")
        }
        return lines.joined(separator: "\n")
    }
}

struct OCRResult: Sendable {
    let caseID: String
    let characterCount: Int
    let lineCount: Int
    let status: String
    let readyForCorrection: Bool

    var logMessage: String {
        [
            "OCR concluído para \(caseID).",
            "Caracteres extraídos: \(characterCount)",
            "Linhas detectadas: \(lineCount)",
            "Status: \(status)",
            readyForCorrection ? "Pronto para correção." : "Revisão da transcrição obrigatória antes da correção."
        ].joined(separator: "\n")
    }
}

struct PaddleOCRPayload: Decodable {
    let ok: Bool
    let engine: String?
    let text: String
    let characterCount: Int
    let lineCount: Int
    let avgScore: Double?
    let status: String?
    let error: String?

    enum CodingKeys: String, CodingKey {
        case ok
        case engine
        case text
        case characterCount = "character_count"
        case lineCount = "line_count"
        case avgScore = "avg_score"
        case status
        case error
    }
}

enum KeychainError: LocalizedError {
    case unexpectedStatus(OSStatus)
    case invalidData

    var errorDescription: String? {
        switch self {
        case .unexpectedStatus(let status):
            return "Keychain retornou status \(status)."
        case .invalidData:
            return "A chave salva no Keychain não pôde ser lida como texto."
        }
    }
}

enum KeychainStore {
    private static let service = "online.xtri.red"
    private static let apiKeyAccount = "SABIA_API_KEY"

    static func readAPIKey() throws -> String? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: apiKeyAccount,
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne
        ]

        var item: CFTypeRef?
        let status = SecItemCopyMatching(query as CFDictionary, &item)
        if status == errSecItemNotFound {
            return nil
        }
        guard status == errSecSuccess else {
            throw KeychainError.unexpectedStatus(status)
        }
        guard
            let data = item as? Data,
            let value = String(data: data, encoding: .utf8)
        else {
            throw KeychainError.invalidData
        }
        return value
    }

    static func saveAPIKey(_ value: String) throws {
        let data = Data(value.utf8)
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: apiKeyAccount
        ]
        let attributes: [String: Any] = [
            kSecValueData as String: data
        ]

        let updateStatus = SecItemUpdate(query as CFDictionary, attributes as CFDictionary)
        if updateStatus == errSecSuccess {
            return
        }
        if updateStatus != errSecItemNotFound {
            throw KeychainError.unexpectedStatus(updateStatus)
        }

        var addQuery = query
        addQuery[kSecValueData as String] = data
        let addStatus = SecItemAdd(addQuery as CFDictionary, nil)
        guard addStatus == errSecSuccess else {
            throw KeychainError.unexpectedStatus(addStatus)
        }
    }

    static func deleteAPIKey() throws {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: apiKeyAccount
        ]
        let status = SecItemDelete(query as CFDictionary)
        guard status == errSecSuccess || status == errSecItemNotFound else {
            throw KeychainError.unexpectedStatus(status)
        }
    }
}

@MainActor
final class AppModel: ObservableObject {
    @Published var vaultPath = defaultVaultPath
    @Published var cases: [EssayCase] = []
    @Published var selectedCaseID: EssayCase.ID? {
        didSet {
            syncTranscriptionDraft()
        }
    }
    @Published var apiKey = ""
    @Published var keychainStatus = "Chave não salva."
    @Published var hasSavedAPIKey = false
    @Published var isEditingAPIKey = false
    @Published var transcriptionDraft = ""
    @Published var log = "Pronto."
    @Published var isRunning = false

    var vaultURL: URL {
        URL(fileURLWithPath: vaultPath)
    }

    var selectedCase: EssayCase? {
        cases.first { $0.id == selectedCaseID } ?? cases.first
    }

    var apiKeyAvailable: Bool {
        !apiKey.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty ||
            ProcessInfo.processInfo.environment["SABIA_API_KEY"]?.isEmpty == false
    }

    init() {
        loadAPIKeyFromKeychain(silent: true)
        refresh()
    }

    func refresh() {
        let loadedCases = loadCases(vaultURL: vaultURL)
        cases = loadedCases
        if let selectedCaseID, loadedCases.contains(where: { $0.id == selectedCaseID }) {
            self.selectedCaseID = selectedCaseID
        } else {
            selectedCaseID = loadedCases.first?.id
        }
        syncTranscriptionDraft()
        log = "Vault carregado: \(loadedCases.count) caso(s)."
    }

    func chooseVault() {
        let panel = NSOpenPanel()
        panel.title = "Selecionar vault do XTRI-RED"
        panel.canChooseFiles = false
        panel.canChooseDirectories = true
        panel.allowsMultipleSelection = false
        panel.directoryURL = vaultURL
        if panel.runModal() == .OK, let url = panel.url {
            vaultPath = url.path
            refresh()
        }
    }

    func importFolder() {
        guard let theme = askForImportTheme() else { return }

        let panel = NSOpenPanel()
        panel.title = "Importar pasta de redações"
        panel.message = "Escolha uma pasta com um arquivo por aluno."
        panel.canChooseFiles = false
        panel.canChooseDirectories = true
        panel.allowsMultipleSelection = false

        guard panel.runModal() == .OK, let sourceURL = panel.url else { return }

        let vaultURL = self.vaultURL
        isRunning = true
        log = "Importando pasta e rodando OCR quando houver imagem..."
        Task {
            let result = await Task.detached {
                Result {
                    try CaseImporter.importFolder(sourceURL: sourceURL, vaultURL: vaultURL, theme: theme)
                }
            }.value
            isRunning = false
            switch result {
            case .success(let summary):
                refresh()
                if let firstCaseDirectory = summary.firstCaseDirectory {
                    selectedCaseID = firstCaseDirectory
                }
                log = summary.logMessage
            case .failure(let error):
                log = "Falha ao importar pasta: \(error.localizedDescription)"
            }
        }
    }

    func importFiles() {
        guard let theme = askForImportTheme() else { return }

        let panel = NSOpenPanel()
        panel.title = "Importar redação"
        panel.message = "Escolha um ou mais arquivos. Cada arquivo vira um caso."
        panel.canChooseFiles = true
        panel.canChooseDirectories = false
        panel.allowsMultipleSelection = true
        panel.allowedContentTypes = [.plainText, .pdf, .jpeg, .png, .heic, .tiff]

        guard panel.runModal() == .OK, !panel.urls.isEmpty else { return }

        let urls = panel.urls
        let vaultURL = self.vaultURL
        isRunning = true
        log = "Importando arquivo(s) e rodando OCR quando houver imagem..."
        Task {
            let result = await Task.detached {
                Result {
                    try CaseImporter.importFiles(urls, vaultURL: vaultURL, theme: theme)
                }
            }.value
            isRunning = false
            switch result {
            case .success(let summary):
                refresh()
                if let firstCaseDirectory = summary.firstCaseDirectory {
                    selectedCaseID = firstCaseDirectory
                }
                log = summary.logMessage
            case .failure(let error):
                log = "Falha ao importar arquivo: \(error.localizedDescription)"
            }
        }
    }

    private func askForImportTheme() -> String? {
        let alert = NSAlert()
        alert.messageText = "Tema oficial do lote"
        alert.informativeText = "Informe o tema comum das redações. Se deixar vazio, o caso será marcado como tema ausente."
        alert.addButton(withTitle: "Importar")
        alert.addButton(withTitle: "Cancelar")

        let textField = NSTextField(frame: NSRect(x: 0, y: 0, width: 520, height: 24))
        textField.placeholderString = "Ex.: Perspectivas acerca do envelhecimento na sociedade brasileira"
        alert.accessoryView = textField

        let response = alert.runModal()
        guard response == .alertFirstButtonReturn else { return nil }
        return textField.stringValue.trimmingCharacters(in: .whitespacesAndNewlines)
    }

    func saveAPIKeyToKeychain() {
        let trimmedKey = apiKey.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmedKey.isEmpty else {
            keychainStatus = "Digite a chave antes de salvar."
            return
        }

        do {
            try KeychainStore.saveAPIKey(trimmedKey)
            apiKey = trimmedKey
            hasSavedAPIKey = true
            isEditingAPIKey = false
            keychainStatus = "Chave salva no Keychain."
            log = "SABIA_API_KEY salva no Keychain do macOS."
        } catch {
            keychainStatus = "Falha ao salvar chave."
            log = error.localizedDescription
        }
    }

    func loadAPIKeyFromKeychain(silent: Bool = false) {
        do {
            if let savedKey = try KeychainStore.readAPIKey(), !savedKey.isEmpty {
                apiKey = savedKey
                hasSavedAPIKey = true
                isEditingAPIKey = false
                keychainStatus = "Chave carregada do Keychain."
                if !silent {
                    log = "SABIA_API_KEY carregada do Keychain."
                }
            } else {
                hasSavedAPIKey = false
                isEditingAPIKey = true
                keychainStatus = "Chave não salva."
                if !silent {
                    log = "Nenhuma chave encontrada no Keychain."
                }
            }
        } catch {
            hasSavedAPIKey = false
            isEditingAPIKey = true
            keychainStatus = "Falha ao carregar chave."
            if !silent {
                log = error.localizedDescription
            }
        }
    }

    func deleteAPIKeyFromKeychain() {
        do {
            try KeychainStore.deleteAPIKey()
            apiKey = ""
            hasSavedAPIKey = false
            isEditingAPIKey = true
            keychainStatus = "Chave apagada do Keychain."
            log = "SABIA_API_KEY apagada do Keychain."
        } catch {
            keychainStatus = "Falha ao apagar chave."
            log = error.localizedDescription
        }
    }

    func runSelectedCase(dryRun: Bool) {
        guard let selectedCase else {
            log = "Nenhum caso selecionado."
            return
        }
        guard selectedCase.isReadyForCorrection else {
            log = "\(selectedCase.caseID) ainda precisa de transcrição revisada. Corrija o texto no painel e clique em Salvar transcrição antes de corrigir."
            return
        }
        if !dryRun, !apiKeyAvailable {
            log = "Defina SABIA_API_KEY no campo seguro ou no ambiente antes de corrigir."
            return
        }

        isRunning = true
        log = dryRun ? "Validando \(selectedCase.caseID)..." : "Corrigindo \(selectedCase.caseID) com Sabiá..."

        let vaultURL = self.vaultURL
        let key = apiKey

        Task {
            let result = await Task.detached {
                ProcessRunner.runCase(
                    vaultURL: vaultURL,
                    caseDirectory: selectedCase.directoryName,
                    caseID: selectedCase.caseID,
                    studentID: selectedCase.studentName,
                    apiKey: key,
                    dryRun: dryRun
                )
            }.value
            isRunning = false
            log = result.output.isEmpty ? "Processo finalizado com código \(result.exitCode)." : result.output
            refresh()
        }
    }

    func runOCRForSelectedCase() {
        guard let selectedCase else {
            log = "Nenhum caso selecionado."
            return
        }
        guard selectedCase.canRunOCR else {
            log = "\(selectedCase.caseID) não tem imagem original compatível para OCR."
            return
        }

        let caseURL = selectedCase.entryURL
        let caseID = selectedCase.caseID
        isRunning = true
        log = "Rodando OCR em \(caseID)..."

        Task {
            let result = await Task.detached {
                Result {
                    try CaseImporter.runOCRForCase(caseURL: caseURL, caseID: caseID)
                }
            }.value
            isRunning = false
            switch result {
            case .success(let ocrResult):
                refresh()
                selectedCaseID = selectedCase.id
                log = ocrResult.logMessage
            case .failure(let error):
                refresh()
                selectedCaseID = selectedCase.id
                log = "Falha no OCR de \(caseID): \(error.localizedDescription)"
            }
        }
    }

    func saveTranscriptionForSelectedCase() {
        guard let selectedCase else {
            log = "Nenhum caso selecionado."
            return
        }

        let text = transcriptionDraft.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !text.isEmpty else {
            log = "\(selectedCase.caseID) está sem transcrição útil."
            return
        }

        do {
            try text.write(
                to: selectedCase.entryURL.appendingPathComponent("redacao.txt"),
                atomically: true,
                encoding: .utf8
            )
            try "ok: transcricao revisada manualmente no XTRI-RED; pronta para correcao.".write(
                to: selectedCase.entryURL.appendingPathComponent("status-ocr.txt"),
                atomically: true,
                encoding: .utf8
            )
            let currentID = selectedCase.id
            refresh()
            selectedCaseID = currentID
            transcriptionDraft = text
            log = "Transcrição salva para \(selectedCase.caseID). Caso liberado para correção."
        } catch {
            log = "Falha ao salvar transcrição: \(error.localizedDescription)"
        }
    }

    func openOriginalForSelectedCase() {
        guard let selectedCase else { return }
        guard let imageURL = originalImageURL(in: selectedCase.entryURL) else {
            log = "\(selectedCase.caseID) não tem imagem original compatível."
            return
        }
        NSWorkspace.shared.open(imageURL)
    }

    func syncTranscriptionDraft() {
        guard let selectedCase else {
            transcriptionDraft = ""
            return
        }
        transcriptionDraft = readText(selectedCase.entryURL.appendingPathComponent("redacao.txt"))
    }

    func openExport() {
        guard let selectedCase else { return }
        NSWorkspace.shared.open(selectedCase.exportURL)
    }

    func revealVault() {
        NSWorkspace.shared.activateFileViewerSelecting([vaultURL])
    }
}

enum ProcessRunner {
    static func runCase(
        vaultURL: URL,
        caseDirectory: String,
        caseID: String,
        studentID: String,
        apiKey: String,
        dryRun: Bool
    ) -> ProcessResult {
        let script = vaultURL.appendingPathComponent("scripts/run_caso_sabia.sh")
        let process = Process()
        process.executableURL = URL(fileURLWithPath: "/bin/bash")
        process.arguments = [script.path, caseDirectory, caseID, studentID]
        process.currentDirectoryURL = vaultURL

        var environment = ProcessInfo.processInfo.environment
        if dryRun {
            environment["CORRETOR_X_DRY_RUN"] = "1"
        }
        if !apiKey.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
            environment["SABIA_API_KEY"] = apiKey
        }
        process.environment = environment

        let outputPipe = Pipe()
        let errorPipe = Pipe()
        process.standardOutput = outputPipe
        process.standardError = errorPipe

        do {
            try process.run()
            process.waitUntilExit()
        } catch {
            return ProcessResult(exitCode: 1, output: "Falha ao iniciar runner: \(error.localizedDescription)")
        }

        let output = String(data: outputPipe.fileHandleForReading.readDataToEndOfFile(), encoding: .utf8) ?? ""
        let error = String(data: errorPipe.fileHandleForReading.readDataToEndOfFile(), encoding: .utf8) ?? ""
        return ProcessResult(exitCode: process.terminationStatus, output: [output, error].filter { !$0.isEmpty }.joined(separator: "\n"))
    }
}

enum CaseImporter {
    private static let textExtensions: Set<String> = ["txt"]
    private static let imageExtensions: Set<String> = ["jpg", "jpeg", "png", "heic", "tif", "tiff"]
    private static let copyOnlyExtensions: Set<String> = ["pdf"]

    enum ImportError: LocalizedError {
        case cannotReadImage(URL)
        case cannotCreateCGImage(URL)
        case noCompatibleImage(URL)

        var errorDescription: String? {
            switch self {
            case .cannotReadImage(let url):
                return "Não foi possível ler a imagem: \(url.lastPathComponent)."
            case .cannotCreateCGImage(let url):
                return "Não foi possível preparar a imagem para OCR: \(url.lastPathComponent)."
            case .noCompatibleImage(let url):
                return "Nenhuma imagem original compatível encontrada em \(url.lastPathComponent)."
            }
        }
    }

    static func importFolder(sourceURL: URL, vaultURL: URL, theme: String) throws -> ImportSummary {
        let fileManager = FileManager.default
        let urls = try fileManager.contentsOfDirectory(
            at: sourceURL,
            includingPropertiesForKeys: [.isDirectoryKey],
            options: [.skipsHiddenFiles]
        )
        let files = urls.filter { url in
            let values = try? url.resourceValues(forKeys: [.isDirectoryKey])
            return values?.isDirectory != true
        }
        return try importFiles(files, vaultURL: vaultURL, theme: theme)
    }

    static func importFiles(_ files: [URL], vaultURL: URL, theme: String) throws -> ImportSummary {
        let fileManager = FileManager.default
        let entriesURL = vaultURL.appendingPathComponent("entradas")
        try fileManager.createDirectory(at: entriesURL, withIntermediateDirectories: true)

        var nextNumber = nextCaseNumber(entriesURL: entriesURL)
        var created = 0
        var readyForCorrection = 0
        var pendingOCR = 0
        var skipped = 0
        var createdDirectories: [String] = []
        var lastCaseID: String?

        for sourceURL in files.sorted(by: { $0.lastPathComponent.localizedStandardCompare($1.lastPathComponent) == .orderedAscending }) {
            let fileExtension = sourceURL.pathExtension.lowercased()
            let isTextFile = textExtensions.contains(fileExtension)
            let isImageFile = imageExtensions.contains(fileExtension)
            let isCopyOnlyFile = copyOnlyExtensions.contains(fileExtension)

            guard isTextFile || isImageFile || isCopyOnlyFile else {
                skipped += 1
                continue
            }

            let caseID = String(format: "CASO-%03d", nextNumber)
            let directoryName = caseID.lowercased()
            let caseURL = entriesURL.appendingPathComponent(directoryName, isDirectory: true)
            nextNumber += 1

            try fileManager.createDirectory(at: caseURL, withIntermediateDirectories: true)

            let studentName = normalizedStudentName(from: sourceURL, fallback: "Aluno \(caseID.replacingOccurrences(of: "CASO-", with: ""))")
            let themeStatus = theme.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty ? "ausente" : "verificado"
            let originalName = "original.\(fileExtension.isEmpty ? "arquivo" : fileExtension)"
            let originalURL = caseURL.appendingPathComponent(originalName)

            try fileManager.copyItem(at: sourceURL, to: originalURL)
            try write(theme, to: caseURL.appendingPathComponent("tema.txt"))
            try write(themeStatus, to: caseURL.appendingPathComponent("status-tema.txt"))
            try write(studentName, to: caseURL.appendingPathComponent("aluno-nome.txt"))
            try write(
                [
                    "arquivo_original=\(sourceURL.lastPathComponent)",
                    "tipo_importacao=\(importType(isTextFile: isTextFile, isImageFile: isImageFile))",
                    "criado_em=\(ISO8601DateFormatter().string(from: Date()))"
                ].joined(separator: "\n"),
                to: caseURL.appendingPathComponent("metadados-importacao.txt")
            )

            if isTextFile {
                let essayText = try readImportedText(sourceURL).trimmingCharacters(in: .whitespacesAndNewlines)
                try write(essayText, to: caseURL.appendingPathComponent("redacao.txt"))
                if essayText.isEmpty {
                    try write("revisao_humana: arquivo .txt importado sem transcricao util.", to: caseURL.appendingPathComponent("status-ocr.txt"))
                    pendingOCR += 1
                } else {
                    try write("ok: transcricao importada de arquivo .txt; sem OCR automatico.", to: caseURL.appendingPathComponent("status-ocr.txt"))
                    readyForCorrection += 1
                }
            } else if isImageFile {
                let ocrResult = try runImageOCR(originalURL: originalURL, caseURL: caseURL, caseID: caseID)
                if ocrResult.readyForCorrection {
                    readyForCorrection += 1
                } else {
                    pendingOCR += 1
                }
            } else {
                try write("", to: caseURL.appendingPathComponent("redacao.txt"))
                try write("aguardando_ocr: PDF importado; OCR automatico de PDF ainda nao disponivel.", to: caseURL.appendingPathComponent("status-ocr.txt"))
                pendingOCR += 1
            }

            created += 1
            createdDirectories.append(directoryName)
            lastCaseID = caseID
        }

        return ImportSummary(
            created: created,
            readyForCorrection: readyForCorrection,
            pendingOCR: pendingOCR,
            skipped: skipped,
            firstCaseDirectory: createdDirectories.first,
            lastCaseID: lastCaseID
        )
    }

    static func runOCRForCase(caseURL: URL, caseID: String) throws -> OCRResult {
        let originals = try FileManager.default.contentsOfDirectory(
            at: caseURL,
            includingPropertiesForKeys: [.isRegularFileKey],
            options: [.skipsHiddenFiles]
        )
        guard let imageURL = originals.first(where: { url in
            url.lastPathComponent.lowercased().hasPrefix("original.")
                && imageExtensions.contains(url.pathExtension.lowercased())
        }) else {
            throw ImportError.noCompatibleImage(caseURL)
        }
        return try runImageOCR(originalURL: imageURL, caseURL: caseURL, caseID: caseID)
    }

    private static func nextCaseNumber(entriesURL: URL) -> Int {
        let directories = (try? FileManager.default.contentsOfDirectory(
            at: entriesURL,
            includingPropertiesForKeys: [.isDirectoryKey],
            options: [.skipsHiddenFiles]
        )) ?? []

        let numbers = directories.compactMap { url -> Int? in
            let values = try? url.resourceValues(forKeys: [.isDirectoryKey])
            guard values?.isDirectory == true else { return nil }
            let name = url.lastPathComponent.lowercased()
            guard name.hasPrefix("caso-") else { return nil }
            return Int(name.dropFirst(5))
        }

        return (numbers.max() ?? 0) + 1
    }

    private static func normalizedStudentName(from url: URL, fallback: String) -> String {
        let rawName = url.deletingPathExtension().lastPathComponent
            .replacingOccurrences(of: "_", with: " ")
            .replacingOccurrences(of: "-", with: " ")
        let normalized = rawName
            .split(whereSeparator: { $0.isWhitespace })
            .joined(separator: " ")
            .trimmingCharacters(in: .whitespacesAndNewlines)
        return normalized.isEmpty ? fallback : normalized
    }

    private static func readImportedText(_ url: URL) throws -> String {
        if let text = try? String(contentsOf: url, encoding: .utf8) {
            return text
        }
        return try String(contentsOf: url, encoding: .isoLatin1)
    }

    private static func importType(isTextFile: Bool, isImageFile: Bool) -> String {
        if isTextFile {
            return "texto"
        }
        if isImageFile {
            return "imagem_ocr_automatico"
        }
        return "pdf_ocr_pendente"
    }

    private static func runImageOCR(originalURL: URL, caseURL: URL, caseID: String) throws -> OCRResult {
        if let paddleResult = try? runPaddleOCR(originalURL: originalURL, caseURL: caseURL),
           paddleResult.ok,
           paddleResult.characterCount >= 500,
           !paddleResult.text.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
            let status = paddleResult.status ?? "parcial: OCR automatico por PaddleOCR; revisar transcricao antes de corrigir."
            try write(paddleResult.text, to: caseURL.appendingPathComponent("redacao.txt"))
            try write(paddleResult.text, to: caseURL.appendingPathComponent("redacao-paddleocr.txt"))
            try write(status, to: caseURL.appendingPathComponent("status-ocr.txt"))
            try write(paddleOCRMetadata(paddleResult), to: caseURL.appendingPathComponent("ocr-paddle.json"))
            return OCRResult(
                caseID: caseID,
                characterCount: paddleResult.characterCount,
                lineCount: paddleResult.lineCount,
                status: status,
                readyForCorrection: isCorrectionReady(essayText: paddleResult.text, statusOCR: status)
            )
        }

        let text = try recognizeText(in: originalURL).trimmingCharacters(in: .whitespacesAndNewlines)
        let lines = text
            .split(whereSeparator: \.isNewline)
            .map { String($0).trimmingCharacters(in: .whitespacesAndNewlines) }
            .filter { !$0.isEmpty }
        let status: String

        if text.isEmpty {
            status = "ocr_degradado: OCR automatico nao extraiu texto util; revisar imagem manualmente."
            try write("", to: caseURL.appendingPathComponent("redacao.txt"))
        } else {
            status = "parcial: OCR automatico por Apple Vision; revisar transcricao antes de corrigir."
            try write(text, to: caseURL.appendingPathComponent("redacao.txt"))
        }

        try write(status, to: caseURL.appendingPathComponent("status-ocr.txt"))
        try write(text, to: caseURL.appendingPathComponent("redacao-apple-vision.txt"))

        return OCRResult(
            caseID: caseID,
            characterCount: text.count,
            lineCount: lines.count,
            status: status,
            readyForCorrection: isCorrectionReady(essayText: text, statusOCR: status)
        )
    }

    private static func runPaddleOCR(originalURL: URL, caseURL: URL) throws -> PaddleOCRPayload? {
        let vaultURL = caseURL.deletingLastPathComponent().deletingLastPathComponent()
        let projectRoot = vaultURL.deletingLastPathComponent().deletingLastPathComponent()
        let pythonURL = projectRoot.appendingPathComponent(".venv/bin/python")
        let scriptURL = vaultURL.appendingPathComponent("scripts/ocr_paddle.py")

        guard FileManager.default.isExecutableFile(atPath: pythonURL.path),
              FileManager.default.fileExists(atPath: scriptURL.path) else {
            return nil
        }

        let process = Process()
        process.executableURL = pythonURL
        process.arguments = [scriptURL.path, "--image", originalURL.path]
        process.currentDirectoryURL = vaultURL

        var environment = ProcessInfo.processInfo.environment
        environment["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"
        process.environment = environment

        let outputPipe = Pipe()
        process.standardOutput = outputPipe
        process.standardError = FileHandle.nullDevice

        try process.run()
        process.waitUntilExit()

        let output = outputPipe.fileHandleForReading.readDataToEndOfFile()
        guard !output.isEmpty else { return nil }

        return try JSONDecoder().decode(PaddleOCRPayload.self, from: output)
    }

    private static func paddleOCRMetadata(_ payload: PaddleOCRPayload) throws -> String {
        let data = try JSONEncoder().encode([
            "engine": payload.engine ?? "paddleocr",
            "character_count": "\(payload.characterCount)",
            "line_count": "\(payload.lineCount)",
            "avg_score": payload.avgScore.map { "\($0)" } ?? "",
            "status": payload.status ?? "",
            "error": payload.error ?? "",
        ])
        return String(data: data, encoding: .utf8) ?? "{}"
    }

    private static func recognizeText(in imageURL: URL) throws -> String {
        guard let image = NSImage(contentsOf: imageURL) else {
            throw ImportError.cannotReadImage(imageURL)
        }
        var rect = CGRect(origin: .zero, size: image.size)
        guard let cgImage = image.cgImage(forProposedRect: &rect, context: nil, hints: nil) else {
            throw ImportError.cannotCreateCGImage(imageURL)
        }

        let request = VNRecognizeTextRequest()
        request.recognitionLevel = .accurate
        request.recognitionLanguages = ["pt-BR", "en-US"]
        request.usesLanguageCorrection = true

        let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
        try handler.perform([request])

        let observations = (request.results ?? []).sorted { lhs, rhs in
            let verticalDelta = abs(lhs.boundingBox.minY - rhs.boundingBox.minY)
            if verticalDelta > 0.01 {
                return lhs.boundingBox.minY > rhs.boundingBox.minY
            }
            return lhs.boundingBox.minX < rhs.boundingBox.minX
        }

        return observations
            .compactMap { $0.topCandidates(1).first?.string.trimmingCharacters(in: .whitespacesAndNewlines) }
            .filter { !$0.isEmpty }
            .joined(separator: "\n")
    }

    private static func write(_ text: String, to url: URL) throws {
        try text.write(to: url, atomically: true, encoding: .utf8)
    }
}

private func loadCases(vaultURL: URL) -> [EssayCase] {
    let entriesURL = vaultURL.appendingPathComponent("entradas")
    let exportsURL = vaultURL.appendingPathComponent("Cérebro do 1000/casos/exports")
    let directories = (try? FileManager.default.contentsOfDirectory(
        at: entriesURL,
        includingPropertiesForKeys: [.isDirectoryKey],
        options: [.skipsHiddenFiles]
    )) ?? []

    return directories.compactMap { url in
        let resourceValues = try? url.resourceValues(forKeys: [.isDirectoryKey])
        guard resourceValues?.isDirectory == true else { return nil }

        let directoryName = url.lastPathComponent
        let caseID = directoryName.uppercased()
        let defaultStudentName = "Aluno \(caseID.replacingOccurrences(of: "CASO-", with: ""))"
        let importedStudentName = readText(url.appendingPathComponent("aluno-nome.txt"))
        let studentName = importedStudentName.isEmpty
            ? defaultStudentName
            : importedStudentName
        let theme = readText(url.appendingPathComponent("tema.txt"))
        let statusOCR = readText(url.appendingPathComponent("status-ocr.txt"))
        let essayText = readText(url.appendingPathComponent("redacao.txt"))
        let exportURL = exportsURL.appendingPathComponent("\(caseID).xlsx")
        let canRunOCR = originalImageURL(in: url) != nil
        let hasTranscription = !essayText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty

        return EssayCase(
            id: directoryName,
            caseID: caseID,
            directoryName: directoryName,
            studentName: studentName,
            title: "\(caseID) - \(theme.isEmpty ? "Tema não informado" : theme)",
            theme: theme,
            statusOCR: statusOCR,
            entryURL: url,
            exportURL: exportURL,
            hasExport: FileManager.default.fileExists(atPath: exportURL.path),
            hasTranscription: hasTranscription,
            isReadyForCorrection: isCorrectionReady(essayText: essayText, statusOCR: statusOCR),
            canRunOCR: canRunOCR
        )
    }
    .sorted { $0.caseID < $1.caseID }
}

private func readText(_ url: URL) -> String {
    (try? String(contentsOf: url, encoding: .utf8))?
        .trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
}

private func isCorrectionReady(essayText: String, statusOCR: String) -> Bool {
    guard !essayText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else { return false }

    let status = statusOCR
        .trimmingCharacters(in: .whitespacesAndNewlines)
        .lowercased()

    if status.hasPrefix("ok:") {
        return true
    }

    let blockedStatusPrefixes = [
        "aguardando_ocr",
        "ocr_degradado",
        "parcial",
        "revisao_humana"
    ]
    if blockedStatusPrefixes.contains(where: { status.hasPrefix($0) }) {
        return false
    }
    if status.contains("revisar") || status.contains("pendente") {
        return false
    }

    return true
}

private func originalImageURL(in caseURL: URL) -> URL? {
    let imageExtensions: Set<String> = ["jpg", "jpeg", "png", "heic", "tif", "tiff"]
    let files = (try? FileManager.default.contentsOfDirectory(
        at: caseURL,
        includingPropertiesForKeys: [.isRegularFileKey],
        options: [.skipsHiddenFiles]
    )) ?? []
    return files.first { url in
        url.lastPathComponent.lowercased().hasPrefix("original.")
            && imageExtensions.contains(url.pathExtension.lowercased())
    }
}

struct ContentView: View {
    @StateObject private var model = AppModel()

    var body: some View {
        NavigationSplitView {
            sidebar
        } detail: {
            detail
        }
        .toolbar {
            ToolbarItemGroup {
                Button("Importar Pasta") {
                    model.importFolder()
                }
                Button("Importar Arquivo") {
                    model.importFiles()
                }
                Button("Atualizar") {
                    model.refresh()
                }
                Button("Abrir Vault") {
                    model.revealVault()
                }
            }
        }
    }

    private var sidebar: some View {
        VStack(alignment: .leading, spacing: 12) {
            VStack(alignment: .leading, spacing: 6) {
                Text("Vault Obsidian")
                    .font(.caption)
                    .foregroundStyle(.secondary)
                HStack {
                    TextField("Caminho do vault", text: $model.vaultPath)
                        .textFieldStyle(.roundedBorder)
                    Button("Escolher") {
                        model.chooseVault()
                    }
                }
            }
            .padding([.horizontal, .top])

            VStack(alignment: .leading, spacing: 6) {
                Text("Importação")
                    .font(.caption)
                    .foregroundStyle(.secondary)
                HStack {
                    Button("Pasta") {
                        model.importFolder()
                    }
                    Button("Arquivos") {
                        model.importFiles()
                    }
                }
                .buttonStyle(.bordered)
                Text("Uma pasta pode ter centenas de arquivos, um por aluno.")
                    .font(.caption2)
                    .foregroundStyle(.secondary)
                    .fixedSize(horizontal: false, vertical: true)
            }
            .padding(.horizontal)

            List(selection: $model.selectedCaseID) {
                Section("Casos") {
                    ForEach(model.cases) { item in
                        VStack(alignment: .leading, spacing: 4) {
                            Text(item.caseID)
                                .font(.headline)
                            Text(item.theme.isEmpty ? "Tema não informado" : item.theme)
                                .font(.caption)
                                .foregroundStyle(.secondary)
                                .lineLimit(2)
                            Text(caseStatusLabel(item))
                                .font(.caption2)
                                .foregroundStyle(caseStatusColor(item))
                        }
                        .tag(item.id)
                    }
                }
            }
        }
        .navigationTitle("XTRI-RED")
    }

    @ViewBuilder
    private var detail: some View {
        if let item = model.selectedCase {
            VStack(alignment: .leading, spacing: 14) {
                header(for: item)
                Divider()
                casePanel(item)
                Divider()
                logPanel
            }
            .padding()
        } else {
            ContentUnavailableView("Nenhum caso encontrado", systemImage: "doc.text.magnifyingglass", description: Text("Use Importar Pasta ou crie uma pasta em entradas/caso-001 com tema.txt, redacao.txt e status-ocr.txt."))
        }
    }

    private func header(for item: EssayCase) -> some View {
        HStack(alignment: .top) {
            VStack(alignment: .leading, spacing: 6) {
                Text(item.caseID)
                    .font(.largeTitle.weight(.semibold))
                Text(item.studentName)
                    .font(.headline)
                    .foregroundStyle(.secondary)
                Text(item.theme.isEmpty ? "Tema não informado" : item.theme)
                    .font(.title3)
                    .foregroundStyle(.secondary)
            }
            Spacer()
            VStack(alignment: .trailing, spacing: 8) {
                apiKeyPanel
                HStack {
                    if item.canRunOCR {
                        Button(item.isReadyForCorrection ? "Reprocessar OCR" : "Rodar OCR") {
                            model.runOCRForSelectedCase()
                        }
                        .disabled(model.isRunning)
                    }
                    Button("Dry-run") {
                        model.runSelectedCase(dryRun: true)
                    }
                    .disabled(model.isRunning || !item.isReadyForCorrection)
                    Button("Corrigir") {
                        model.runSelectedCase(dryRun: false)
                    }
                    .disabled(!model.apiKeyAvailable || model.isRunning || !item.isReadyForCorrection)
                    Button("Abrir Excel") {
                        model.openExport()
                    }
                    .disabled(!item.hasExport)
                }
            }
        }
    }

    @ViewBuilder
    private var apiKeyPanel: some View {
        if model.hasSavedAPIKey && !model.isEditingAPIKey {
            VStack(alignment: .trailing, spacing: 6) {
                HStack(spacing: 10) {
                    Image(systemName: "checkmark.seal.fill")
                        .font(.title3)
                        .foregroundStyle(.green)
                    VStack(alignment: .trailing, spacing: 2) {
                        Text("Sabiá conectado")
                            .font(.headline)
                        Text("Chave salva no Keychain")
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                }
                .padding(.horizontal, 12)
                .padding(.vertical, 9)
                .frame(width: 320, alignment: .trailing)
                .background(Color.green.opacity(0.10))
                .clipShape(RoundedRectangle(cornerRadius: 10))

                HStack(spacing: 8) {
                    Button("Trocar chave") {
                        model.isEditingAPIKey = true
                    }
                    Button("Apagar") {
                        model.deleteAPIKeyFromKeychain()
                    }
                }

                Text(model.keychainStatus)
                    .font(.caption)
                    .foregroundStyle(.green)
            }
        } else {
            VStack(alignment: .trailing, spacing: 6) {
                SecureField("SABIA_API_KEY", text: $model.apiKey)
                    .textFieldStyle(.roundedBorder)
                    .frame(width: 320)

                HStack(spacing: 8) {
                    Button("Salvar") {
                        model.saveAPIKeyToKeychain()
                    }
                    Button("Carregar") {
                        model.loadAPIKeyFromKeychain()
                    }
                    Button("Apagar") {
                        model.deleteAPIKeyFromKeychain()
                    }
                    .disabled(!model.hasSavedAPIKey)
                }

                Text(model.keychainStatus)
                    .font(.caption)
                    .foregroundStyle(model.hasSavedAPIKey ? .green : .secondary)
            }
        }
    }

    private func casePanel(_ item: EssayCase) -> some View {
        VStack(alignment: .leading, spacing: 10) {
            Label(item.studentName, systemImage: "person.crop.circle")
                .font(.callout)
                .foregroundStyle(.secondary)
            Label(item.statusOCR.isEmpty ? "Status de transcrição não informado" : item.statusOCR, systemImage: "text.viewfinder")
                .font(.callout)
                .foregroundStyle(.secondary)

            HStack {
                Text("Transcrição")
                    .font(.headline)
                Spacer()
                if item.canRunOCR {
                    Button("Abrir imagem") {
                        model.openOriginalForSelectedCase()
                    }
                }
                Button("Salvar transcrição") {
                    model.saveTranscriptionForSelectedCase()
                }
                .disabled(model.isRunning || model.transcriptionDraft.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
            }

            TextEditor(text: $model.transcriptionDraft)
                .font(.system(.body, design: .serif))
                .scrollContentBackground(.hidden)
                .padding(8)
                .background(Color(nsColor: .textBackgroundColor))
                .clipShape(RoundedRectangle(cornerRadius: 8))
        }
    }

    private func caseStatusLabel(_ item: EssayCase) -> String {
        if item.hasExport {
            return "Excel gerado"
        }
        if item.isReadyForCorrection {
            return "Pronto para corrigir"
        }
        if item.hasTranscription {
            return "Revisar transcrição"
        }
        return "Aguardando OCR"
    }

    private func caseStatusColor(_ item: EssayCase) -> Color {
        if item.hasExport {
            return .green
        }
        if item.isReadyForCorrection {
            return .blue
        }
        return .orange
    }

    private var logPanel: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Execução")
                .font(.headline)
            ScrollView {
                Text(model.log)
                    .font(.system(.caption, design: .monospaced))
                    .textSelection(.enabled)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(10)
            }
            .frame(height: 120)
            .background(Color(nsColor: .controlBackgroundColor))
            .clipShape(RoundedRectangle(cornerRadius: 8))
        }
    }
}
