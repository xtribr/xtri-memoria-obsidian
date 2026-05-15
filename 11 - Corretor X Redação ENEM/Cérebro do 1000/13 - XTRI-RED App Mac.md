# XTRI-RED App Mac

Status: app macOS local empacotável

## Objetivo

Operar correções em lote no macOS usando o vault do Obsidian como cérebro metodológico. O nome do app é **XTRI-RED**.

## Papel do app

- Importar uma pasta com um arquivo por aluno.
- Importar um ou mais arquivos avulsos.
- Listar casos em `entradas/caso-*`.
- Mostrar tema, status de transcrição e prévia da redação.
- Ler prompts/rubricas em `app-config/prompts`.
- Executar dry-run e correção real via `scripts/run_caso_sabia.sh`.
- Abrir o Excel gerado em `Cérebro do 1000/casos/exports`.

## Interface Operacional

Status em 2026-05-15: a tela principal foi simplificada para operação de correções. Prompts e rubricas não aparecem mais na barra lateral nem no painel direito; continuam no vault como cérebro metodológico e são consumidos pelo motor de correção.

A tela principal fica organizada em:

- vault e importação;
- lista de casos;
- dados da redação selecionada;
- ações de OCR, dry-run, correção e abertura do Excel;
- log de execução.

## Upload Lógico

Status em 2026-05-15: o app possui importação local para lote e arquivos avulsos.

Fluxo recomendado para 500 redações:

1. Organizar uma pasta com um arquivo por aluno.
2. Clicar em `Importar Pasta` na barra superior ou em `Pasta` na seção `Importação` da barra lateral.
3. Informar o tema oficial comum do lote.
4. O XTRI-RED cria automaticamente `entradas/caso-*`.

Arquivos `.txt` entram como transcrição pronta para correção. Imagens `.jpg`, `.jpeg`, `.png`, `.heic`, `.tif` e `.tiff` tentam OCR Seguro com OpenAI Vision quando `OPENAI_API_KEY` está disponível; se não houver chave ou a chamada falhar, o app usa PaddleOCR (`lang=pt`) quando instalado no `.venv`; se necessário, cai para Apple Vision. O OCR Seguro faz transcrição literal e auditoria visual independente. Só confiança alta, boa similaridade e ausência de trechos críticos geram `status-ocr.txt = ok`; os demais casos ficam `parcial`. PDFs são copiados para o caso como `original.pdf`, mas continuam com `status-ocr.txt = aguardando_ocr` até existir texto em `redacao.txt`.

Casos de imagem podem ser processados ou reprocessados pelo botão `Rodar OCR`/`Reprocessar OCR`, exibido quando o caso tem `original.ext` compatível.

Arquivos operacionais:

- `scripts/ocr_paddle.py`
- `scripts/requirements-ocr.txt`

Estrutura criada por arquivo:

```text
entradas/caso-001/
  aluno-nome.txt
  tema.txt
  status-tema.txt
  status-ocr.txt
  redacao-literal.txt
  redacao.txt
  original.ext
  transcricao-fonte.txt
  transcricao-literal-validada.txt
  metadados-importacao.txt
```

## Atualização de Validação Sabiá

Status em 2026-05-15: o XTRI-RED usa o runner `scripts/run_caso_sabia.sh`, que chama `scripts/corrigir_com_sabia.py`. Portanto, a política de recuperação do Sabiá já entra no app sem lógica duplicada em Swift.

Fluxo aplicado pelo motor:

- `re_prompt_com_erro`: envia o erro Pydantic e o JSON rejeitado para o Sabiá corrigir a estrutura.
- `fallback_modelo_maior`: tenta novamente com o modelo configurado em `SABIA_FALLBACK_MODEL` ou `--fallback-model`.
- `marcar_revisao_humana`: bloqueia a geração do Excel e cria `*.revisao-humana.txt` quando a resposta continua inválida.

O bundle local foi recompilado em 2026-05-15:

- `apps/xtri-red/dist/XTRI-RED.app`

Validação feita:

- build release Swift;
- assinatura ad-hoc;
- `codesign --verify --deep --strict` com caminho absoluto.

## Papel do Obsidian

O Obsidian continua sendo a fonte de governança:

- rubricas;
- prompts por competência;
- banco de casos;
- decisões de calibração;
- registro de limitações e validações humanas.

## Local do app

- `apps/xtri-red`

## Rodar

```bash
cd "/Volumes/KINGSTON 2/apps/apps/corretor de redação/corretor x/11 - Corretor X Redação ENEM/apps/xtri-red"
swift run XTRI-RED
```

## Gerar app oficial local

```bash
cd "/Volumes/KINGSTON 2/apps/apps/corretor de redação/corretor x/11 - Corretor X Redação ENEM/apps/xtri-red"
./package_app.sh
open "dist/XTRI-RED.app"
```

O bundle local fica em `apps/xtri-red/dist/XTRI-RED.app`.

Observação: esta etapa cria um app clicável assinado ad-hoc para uso local. Distribuição fora deste Mac ainda exige assinatura com certificado Apple Developer e notarização.

## Revisão de Transcrição

Regra operacional atual: OCR de imagem manuscrita só libera correção automaticamente quando passa no OCR Seguro.

O OpenAI Vision pode preencher `redacao.txt` com transcrição validada. Se o status for `ok`, o lote pode seguir para correção. Se o status for `parcial`, `ocr_degradado`, `aguardando_ocr` ou `revisao_humana`, o app mantém `Corrigir` bloqueado.

Regra de fonte da correção:

- `redacao-literal.txt` é a transcrição forense usada para correção.
- `redacao.txt` é rascunho/compatibilidade e pode conter OCR parcial.
- `scripts/run_caso_sabia.sh` prefere `redacao-literal.txt` e bloqueia status diferente de `ok:`.
- Override só para auditoria manual: `CORRETOR_X_ALLOW_UNSAFE_OCR=1`.

Fluxo correto:

1. abrir a imagem original no app;
2. revisar ou refazer a transcrição no editor;
3. clicar em `Salvar transcrição`;
4. corrigir apenas depois do status `ok`.

Camadas de OCR:

1. OCR Seguro com OpenAI Vision `gpt-5.2`, se `OPENAI_API_KEY` estiver no Keychain ou no ambiente;
2. PaddleOCR local, se instalado no `.venv`;
3. Apple Vision local como fallback.

O modelo da primeira camada pode ser sobrescrito por `OPENAI_VISION_MODEL`.

Prompt da camada OpenAI Vision:

- transcrição literal de português brasileiro;
- preservação de acentos conforme visíveis no manuscrito;
- preservação de erros reais do aluno;
- preservação de hífens de quebra de linha quando escritos;
- preservação de parágrafos com linha em branco entre blocos;
- marcação de palavras/trechos ilegíveis ou duvidosos.
- auditoria da transcrição inicial contra a imagem;
- cálculo de `confidence`, `similarity` e `safe_for_correction`.

Arquivos de auditoria:

- `redacao-openai-vision.txt`
- `redacao-openai-vision-inicial.txt`
- `ocr-openai-vision.json`
- `redacao-paddleocr.txt`
- `ocr-paddle.json`
- `redacao-apple-vision.txt`

## Regra de segurança

A chave `SABIA_API_KEY` não deve ser hardcoded nem salva no Git.

O app salva a chave no Keychain do macOS quando o usuário clica em `Salvar`. Em novas aberturas, o XTRI-RED carrega essa chave automaticamente e a passa ao runner apenas em variável de ambiente do processo.

Quando a chave está salva, a interface mostra `Sabiá conectado` e oculta o campo da chave. O campo volta a aparecer apenas ao clicar em `Trocar chave` ou após apagar o registro.

Também é possível apagar a chave pelo botão `Apagar` na interface.

Os runners de terminal usam o mesmo registro do Keychain:

- service: `online.xtri.red`;
- account: `SABIA_API_KEY`.

Assim, depois de salvar a chave uma vez no app, `scripts/run_caso_sabia.sh` também consegue corrigir sem `export SABIA_API_KEY`.

## Conexões

- [[12 - Integração Sabiá]]
- [[03 - Banco de Casos Corrigidos]]
- [[05 - Calibração por Competência]]
