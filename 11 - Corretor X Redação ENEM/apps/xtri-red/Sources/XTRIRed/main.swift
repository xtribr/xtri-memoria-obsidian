import AppKit
import Security
import SwiftUI

private let defaultVaultPath = "/Volumes/KINGSTON 2/apps/apps/corretor de redação/corretor x/11 - Corretor X Redação ENEM"

@main
struct XTRIRedApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
                .frame(minWidth: 1120, minHeight: 720)
        }
        .windowStyle(.titleBar)
    }
}

struct EssayCase: Identifiable, Hashable, Sendable {
    let id: String
    let caseID: String
    let directoryName: String
    let title: String
    let theme: String
    let statusOCR: String
    let textPreview: String
    let entryURL: URL
    let exportURL: URL
    let hasExport: Bool
}

struct BrainPrompt: Identifiable, Hashable {
    let id: String
    let title: String
    let path: String
    let preview: String
}

struct ProcessResult: Sendable {
    let exitCode: Int32
    let output: String
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
    @Published var prompts: [BrainPrompt] = []
    @Published var selectedCaseID: EssayCase.ID?
    @Published var apiKey = ""
    @Published var keychainStatus = "Chave não salva."
    @Published var hasSavedAPIKey = false
    @Published var isEditingAPIKey = false
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
        prompts = loadPrompts(vaultURL: vaultURL)
        if let selectedCaseID, loadedCases.contains(where: { $0.id == selectedCaseID }) {
            self.selectedCaseID = selectedCaseID
        } else {
            selectedCaseID = loadedCases.first?.id
        }
        log = "Vault carregado: \(loadedCases.count) caso(s), \(prompts.count) prompt(s)."
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
                    studentID: "Aluno \(selectedCase.caseID.replacingOccurrences(of: "CASO-", with: ""))",
                    apiKey: key,
                    dryRun: dryRun
                )
            }.value
            isRunning = false
            log = result.output.isEmpty ? "Processo finalizado com código \(result.exitCode)." : result.output
            refresh()
        }
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
        let theme = readText(url.appendingPathComponent("tema.txt"))
        let statusOCR = readText(url.appendingPathComponent("status-ocr.txt"))
        let essayText = readText(url.appendingPathComponent("redacao.txt"))
        let preview = essayText.isEmpty ? "Sem transcrição encontrada." : essayText
        let exportURL = exportsURL.appendingPathComponent("\(caseID).xlsx")

        return EssayCase(
            id: directoryName,
            caseID: caseID,
            directoryName: directoryName,
            title: "\(caseID) - \(theme.isEmpty ? "Tema não informado" : theme)",
            theme: theme,
            statusOCR: statusOCR,
            textPreview: preview,
            entryURL: url,
            exportURL: exportURL,
            hasExport: FileManager.default.fileExists(atPath: exportURL.path)
        )
    }
    .sorted { $0.caseID < $1.caseID }
}

private func loadPrompts(vaultURL: URL) -> [BrainPrompt] {
    let promptsURL = vaultURL.appendingPathComponent("app-config/prompts")
    let files = (try? FileManager.default.contentsOfDirectory(
        at: promptsURL,
        includingPropertiesForKeys: nil,
        options: [.skipsHiddenFiles]
    )) ?? []

    return files
        .filter { $0.pathExtension.lowercased() == "md" }
        .sorted { $0.lastPathComponent < $1.lastPathComponent }
        .map { url in
            let text = readText(url)
            let firstLine = text.split(separator: "\n", maxSplits: 1).first.map(String.init) ?? url.deletingPathExtension().lastPathComponent
            return BrainPrompt(
                id: url.lastPathComponent,
                title: firstLine.replacingOccurrences(of: "# ", with: ""),
                path: url.path,
                preview: text
            )
        }
}

private func readText(_ url: URL) -> String {
    (try? String(contentsOf: url, encoding: .utf8))?
        .trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
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
                            Text(item.hasExport ? "Excel gerado" : "Sem Excel")
                                .font(.caption2)
                                .foregroundStyle(item.hasExport ? .green : .orange)
                        }
                        .tag(item.id)
                    }
                }

                Section("Cérebro") {
                    ForEach(model.prompts) { prompt in
                        VStack(alignment: .leading, spacing: 3) {
                            Text(prompt.id.replacingOccurrences(of: ".md", with: "").uppercased())
                                .font(.headline)
                            Text(prompt.title)
                                .font(.caption)
                                .foregroundStyle(.secondary)
                        }
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
                HSplitView {
                    casePanel(item)
                        .frame(minWidth: 420)
                    brainPanel
                        .frame(minWidth: 360)
                }
                Divider()
                logPanel
            }
            .padding()
        } else {
            ContentUnavailableView("Nenhum caso encontrado", systemImage: "doc.text.magnifyingglass", description: Text("Crie uma pasta em entradas/caso-001 com tema.txt, redacao.txt e status-ocr.txt."))
        }
    }

    private func header(for item: EssayCase) -> some View {
        HStack(alignment: .top) {
            VStack(alignment: .leading, spacing: 6) {
                Text(item.caseID)
                    .font(.largeTitle.weight(.semibold))
                Text(item.theme.isEmpty ? "Tema não informado" : item.theme)
                    .font(.title3)
                    .foregroundStyle(.secondary)
            }
            Spacer()
            VStack(alignment: .trailing, spacing: 8) {
                apiKeyPanel
                HStack {
                    Button("Dry-run") {
                        model.runSelectedCase(dryRun: true)
                    }
                    Button("Corrigir") {
                        model.runSelectedCase(dryRun: false)
                    }
                    .disabled(!model.apiKeyAvailable || model.isRunning)
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
            Label(item.statusOCR.isEmpty ? "Status de transcrição não informado" : item.statusOCR, systemImage: "text.viewfinder")
                .font(.callout)
                .foregroundStyle(.secondary)

            Text("Redação")
                .font(.headline)
            ScrollView {
                Text(item.textPreview)
                    .font(.system(.body, design: .serif))
                    .lineSpacing(4)
                    .textSelection(.enabled)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(12)
            }
            .background(Color(nsColor: .textBackgroundColor))
            .clipShape(RoundedRectangle(cornerRadius: 8))
        }
    }

    private var brainPanel: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("Cérebro Obsidian")
                .font(.headline)
            Text("Prompts e rubricas carregados de app-config/prompts.")
                .font(.caption)
                .foregroundStyle(.secondary)

            ScrollView {
                LazyVStack(alignment: .leading, spacing: 12) {
                    ForEach(model.prompts) { prompt in
                        VStack(alignment: .leading, spacing: 6) {
                            Text(prompt.title)
                                .font(.subheadline.weight(.semibold))
                            Text(prompt.preview)
                                .font(.caption)
                                .foregroundStyle(.secondary)
                                .lineLimit(8)
                                .textSelection(.enabled)
                        }
                        .padding(10)
                        .background(Color(nsColor: .controlBackgroundColor))
                        .clipShape(RoundedRectangle(cornerRadius: 8))
                    }
                }
            }
        }
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
