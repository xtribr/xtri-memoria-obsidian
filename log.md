# log

Registro cronológico append-only da LLM Wiki da XTRI.

Use o padrão:

```text
## [AAAA-MM-DD] tipo | título
```

## [2026-05-12] setup | Estrutura inicial da memória XTRI

Criadas pastas principais do vault, notas institucionais, notas de stack, glossário ENEM/TRI/SISU, fontes oficiais, projetos ativos, decisões e templates.

Notas principais:

- [[Memória XTRI - Índice]]
- [[XTRI - Visão Geral]]
- [[Regras Operacionais do Codex na XTRI]]
- [[Stack Oficial da XTRI]]

## [2026-05-12] ingest | Inventário Supabase da XTRI

Inventariados 7 projetos Supabase da organização `eazfgctzojzsbojaxgdo` via CLI, registrando apenas metadados seguros.

Notas principais:

- [[Supabase - Inventário de Projetos]]
- [[Supabase - Projeto qgqliquusdkkwnfuzdwi]]
- [[Supabase - banco de questões]]

## [2026-05-12] ingest | Acervo PDFS TRI ARTIGOS

Catalogados 18 PDFs sobre TRI, ENEM, psicometria, IA, PLN, aprendizagem e dashboards. Criado índice na pasta de fontes e nota de acervo no vault principal.

Notas principais:

- [[Acervo de Artigos TRI e ENEM]]
- [[Síntese - Artigos TRI e ENEM para XTRI]]

## [2026-05-12] ingest | Resumos dos artigos TRI e ENEM

Criados 18 resumos de artigos com foco em pontos úteis para a XTRI e conexões com projetos, Supabase e requisitos de produto.

Nota principal:

- [[Síntese - Artigos TRI e ENEM para XTRI]]

## [2026-05-12] analysis | Requisitos do Banco de Questões XTRI

Transformada a síntese dos artigos em requisitos técnicos para o banco de questões, incluindo item, alternativas, aplicação, caderno, posição, suporte visual, desempenho, psicometria, IA e governança.

Notas principais:

- [[Requisitos - Banco de Questões XTRI]]
- [[Checklist - Auditoria do Schema Banco de Questões]]

## [2026-05-12] audit | Schema real do Supabase banco de questões

Auditado o schema exposto do projeto `fbykcqcssykopvcrsfoo` sem exportar dados reais. Identificadas tabelas, views, buckets, Edge Functions, lacunas e riscos.

Notas principais:

- [[Auditoria - Schema Real Banco de Questões]]
- [[Checklist - Auditoria do Schema Banco de Questões]]

Bloqueio:

- RLS, policies, triggers e funções SQL internas exigem `SUPABASE_DB_PASSWORD`.

## [2026-05-12] ingest | API Própria de Questões XTRI

Registrada a API própria `https://api.questoes.xtri.online/api/docs/` como ativo crítico. Mapeado OpenAPI público com endpoints, filtros e schemas principais.

Nota principal:

- [[API Própria - Questões XTRI]]

## [2026-05-12] setup | Instanciação do padrão LLM Wiki

Criados arquivos operacionais para transformar o vault em uma LLM Wiki persistente: schema para agentes, índice operacional, log cronológico, SOP e templates.

Arquivos principais:

- [[AGENTS]]
- [[index]]
- [[log]]
- [[LLM Wiki - Operação da Memória XTRI]]

## [2026-05-12] planning | Backlog do Banco de Questões

Criado backlog priorizado a partir das lacunas de [[Auditoria - Schema Real Banco de Questões]], [[API Própria - Questões XTRI]] e [[Requisitos - Banco de Questões XTRI]].

Nota principal:

- [[Backlog - Banco de Questões]]

Próximas ações:

- Criar [[Roadmap - Banco de Questões]].
- Auditar respostas reais controladas da [[API Própria - Questões XTRI]].

## [2026-05-12] audit | Respostas reais controladas da API Própria de Questões

Auditadas chamadas pequenas da [[API Própria - Questões XTRI]] sem varrer a base: anos, provas, questões paginadas, habilidades, detalhe por ID, detalhe por ano/slug, filtros e CORS.

Nota principal:

- [[Auditoria - API Própria Questões XTRI]]

Achados principais:

- API funcional e paginada.
- `correctAlternative` e `isCorrect` expostos publicamente.
- CORS não liberou `https://xtri.online` nos testes.
- Questões recentes podem ter `skill` e `param_b` nulos.

## [2026-05-12] manutenção | Índices, status e mapa operacional

Criadas notas estruturais para melhorar navegação e governança da wiki: índices por pasta crítica, convenções de status/evidência e mapa operacional de projetos.

Notas criadas:

- [[Índice - Produtos e Projetos]]
- [[Mapa Operacional de Projetos XTRI]]
- [[Índice - Dados e Fontes]]
- [[Índice - ENEM, TRI e SISU]]
- [[Convenções de Status e Evidência]]

Observação:

- O volume `/Volumes/KINGSTON` não estava montado durante a revisão; caminhos locais de projetos foram marcados como pendentes de confirmação, não como fatos verificados.

## [2026-05-13] ingest | Padrão de mapeamento de simulados ENEM Dia 1

Registrado padrão operacional validado para mapeamento do Dia 1 de simulados ENEM em planilha da XTRI, incluindo estrutura de colunas, contagem esperada, duplicação por idioma nas questões 1-5 e convenção de tópicos curtos.

Nota principal:

- [[Padrão - Mapeamento de Simulados ENEM Dia 1]]

## [2026-05-14] ingest | Corretor X Redação ENEM

Criado vault/classe de conteúdo HTML para o Corretor X de redação ENEM, com base na cartilha oficial do participante 2025 e nas cartilhas Redação a Mil disponíveis no diretório de trabalho.

Ativo principal:

- [Corretor X Redação ENEM](11%20-%20Corretor%20X%20Reda%C3%A7%C3%A3o%20ENEM/index.html)

Fontes brutas:

- `11 - Corretor X Redação ENEM/fontes/pdfs/`

Observações:

- O HTML registra sínteses, padrões e protocolo; não republica transcrições integrais das redações nota 1000.
- A cartilha oficial do Inep permanece como autoridade normativa; as cartilhas nota 1000 são referência de padrões, não regra oficial.

## [2026-05-15] change | XTRI-RED com recuperação de validação Sabiá

Registrada a atualização operacional do XTRI-RED/Corretor X para respostas do Sabiá que falham nos schemas Pydantic.

Notas principais:

- [[12 - Integração Sabiá]]
- [[13 - XTRI-RED App Mac]]

Mudanças registradas:

- O script `scripts/corrigir_com_sabia.py` aplica `re_prompt_com_erro`, `fallback_modelo_maior` e, se necessário, `marcar_revisao_humana`.
- Tentativas inválidas entram na aba `Auditoria` quando uma tentativa posterior recupera a chamada.
- Se a validação não for recuperada, o Excel não é gerado e o caso recebe um arquivo `*.revisao-humana.txt`.
- O bundle local `apps/xtri-red/dist/XTRI-RED.app` foi recompilado e verificado com assinatura ad-hoc em 2026-05-15.

## [2026-05-15] feature | Upload lógico de redações no XTRI-RED

Implementada importação local no XTRI-RED para lote e arquivos avulsos.

Nota principal:

- [[13 - XTRI-RED App Mac]]

Comportamento registrado:

- `Importar Pasta` cria um caso por arquivo encontrado na pasta selecionada.
- `Importar Arquivo` aceita um ou mais arquivos selecionados manualmente.
- Arquivos `.txt` viram casos prontos para correção, com `redacao.txt` preenchido.
- PDFs e imagens são preservados como `original.ext`, marcados como `aguardando_ocr` e bloqueados para correção até haver transcrição.

## [2026-05-15] fix | OCR local para imagens no XTRI-RED

Adicionado OCR local com Apple Vision para imagens importadas pelo XTRI-RED.

Nota principal:

- [[13 - XTRI-RED App Mac]]

Comportamento registrado:

- Imagens `.jpg`, `.jpeg`, `.png`, `.heic`, `.tif` e `.tiff` passam por OCR no momento da importação.
- Casos antigos com imagem original compatível podem usar o botão `Rodar OCR`.
- A transcrição de manuscrito recebe `status-ocr.txt = parcial` para indicar necessidade de revisão antes de correção pedagógica.
- PDFs permanecem como OCR pendente nesta etapa.

## [2026-05-15] change | Interface operacional limpa no XTRI-RED

Removida a exposição de prompts/rubricas da tela principal do XTRI-RED.

Nota principal:

- [[13 - XTRI-RED App Mac]]

Decisão:

- O Obsidian continua sendo o cérebro metodológico.
- A interface do app passa a priorizar operação: importar, selecionar caso, revisar transcrição, rodar OCR/correção e abrir Excel.

## [2026-05-15] change | PaddleOCR como OCR preferencial em imagens

Integrado PaddleOCR como tentativa preferencial para OCR de imagens no XTRI-RED.

Nota principal:

- [[13 - XTRI-RED App Mac]]

Arquivos:

- `scripts/ocr_paddle.py`
- `scripts/requirements-ocr.txt`

Comportamento:

- O app tenta PaddleOCR com `lang=pt` quando o `.venv` possui `paddlepaddle` e `paddleocr`.
- Se PaddleOCR falhar, o app mantém fallback automático para Apple Vision.
- A transcrição gerada por PaddleOCR também é salva em `redacao-paddleocr.txt` e metadados em `ocr-paddle.json`.

## [2026-05-15] fix | Bloqueio de correção com OCR parcial

Após validação real no CASO-003, o OCR manuscrito com PaddleOCR foi considerado insuficiente para correção automática.

Nota principal:

- [[13 - XTRI-RED App Mac]]

Decisão:

- OCR de imagem manuscrita passa a ser tratado como rascunho de transcrição.
- Status `parcial`, `ocr_degradado`, `aguardando_ocr` e `revisao_humana` bloqueiam `Dry-run` e `Corrigir`.
- O app agora permite abrir a imagem original, editar a transcrição e liberar o caso apenas ao salvar a transcrição revisada com status `ok`.

## [2026-05-15] change | OpenAI Vision como camada opcional de transcrição

Adicionada camada opcional de OCR por visão antes do PaddleOCR no XTRI-RED.

Nota principal:

- [[13 - XTRI-RED App Mac]]

Arquivos:

- `scripts/ocr_openai_vision.py`

Comportamento:

- Se `OPENAI_API_KEY` estiver disponível no Keychain ou no ambiente, o app tenta transcrição literal por OpenAI Vision.
- A transcrição é salva em `redacao-openai-vision.txt` e os metadados em `ocr-openai-vision.json`.
- Mesmo quando a transcrição vem preenchida, o status permanece `parcial` e a correção continua bloqueada até revisão humana.

## [2026-05-15] change | GPT-5.2 como padrão da transcrição OpenAI Vision

Após teste local no CASO-003, `gpt-5.2` produziu transcrição manuscrita mais limpa que `gpt-5.1`.

Decisão:

- `scripts/ocr_openai_vision.py` passa a usar `gpt-5.2` como padrão.
- `OPENAI_VISION_MODEL` continua disponível para teste controlado de outros modelos.
- A saída permanece com status `parcial`, exigindo revisão humana antes de correção.

## [2026-05-15] change | Prompt literal de OCR preserva parágrafos

Atualizado o prompt da camada OpenAI Vision para transcrição literal de redações manuscritas.

Regras adicionadas:

- preservar acentos quando visíveis e não inserir acentos ausentes;
- preservar hífens de quebra de linha;
- preservar quebras de linha internas e separação de parágrafos;
- marcar palavras incertas com motivo de incerteza;
- reforçar que a transcrição não pode corrigir, normalizar ou completar o texto do aluno.

## [2026-05-15] change | OCR Seguro com auditoria visual

Implementado fluxo de OCR Seguro para escala.

Comportamento:

- primeira chamada OpenAI Vision faz transcrição literal;
- segunda chamada audita a transcrição contra a imagem original;
- o script calcula similaridade entre leitura inicial e leitura validada;
- a saída registra `confidence`, `similarity`, `safe_for_correction`, divergências e trechos críticos;
- apenas casos com confiança alta, similaridade mínima, parágrafos suficientes e sem trechos críticos recebem `status ok`;
- casos inseguros ficam `parcial` e seguem para fila de revisão ou reenvio de imagem.
