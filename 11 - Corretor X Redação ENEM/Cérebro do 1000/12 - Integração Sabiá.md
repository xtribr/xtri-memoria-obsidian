# Integração Sabiá

Status: ativo

## Objetivo

Usar o modelo `sabia-4` para gerar a primeira correção estruturada do Corretor X e preencher o Excel de entrega.

## Arquivo operacional

- [scripts/corrigir_com_sabia.py](../scripts/corrigir_com_sabia.py)

## Segurança da chave

Nunca salvar a chave da Maritaca/Sabiá no vault, no Git ou em arquivo `.env` versionado.

Forma recomendada: abrir o XTRI-RED, colar a chave no campo `SABIA_API_KEY` e clicar em `Salvar`. A chave fica no Keychain do macOS e passa a ser usada automaticamente pelo app e pelos runners de terminal.

O registro usado no Keychain é:

- service: `online.xtri.red`;
- account: `SABIA_API_KEY`.

Alternativa temporária: usar variável de ambiente apenas na sessão atual do terminal.

```bash
export SABIA_API_KEY="sua_chave_aqui"
```

## Ambiente virtual local

O ambiente virtual principal fica na raiz do projeto:

```bash
cd "/Volumes/KINGSTON 2/apps/apps/corretor de redação"
.venv/bin/python -m pip install -r "corretor x/11 - Corretor X Redação ENEM/scripts/requirements.txt"
```

## Preparação do Caso 001

Criar arquivos locais ignorados pelo Git:

```bash
cd "/Volumes/KINGSTON 2/apps/apps/corretor de redação/corretor x/11 - Corretor X Redação ENEM"
mkdir -p entradas/caso-001
```

Arquivos esperados:

- `entradas/caso-001/tema.txt`
- `entradas/caso-001/redacao.txt`

Se a redação vier por imagem ou PDF escaneado, seguir [[07 - Pipeline OCR]] antes de rodar a correção.

## Comando de teste sem API

```bash
../../.venv/bin/python scripts/corrigir_com_sabia.py \
  --tema-file entradas/caso-001/tema.txt \
  --redacao-file entradas/caso-001/redacao.txt \
  --case-id CASO-001 \
  --aluno-id "Aluno 001" \
  --dry-run
```

## Comando de correção real

Atalho recomendado, funciona a partir de qualquer diretório:

```bash
export SABIA_API_KEY="sua_chave_aqui"
"/Volumes/KINGSTON 2/apps/apps/corretor de redação/corretor x/11 - Corretor X Redação ENEM/scripts/run_caso001_sabia.sh"
```

Para testar caminhos sem chamar a API:

```bash
CORRETOR_X_DRY_RUN=1 "/Volumes/KINGSTON 2/apps/apps/corretor de redação/corretor x/11 - Corretor X Redação ENEM/scripts/run_caso001_sabia.sh"
```

## Rodar qualquer caso

Use o runner genérico com o diretório do caso, o ID do caso e o identificador anonimizado do aluno:

```bash
export SABIA_API_KEY="sua_chave_aqui"
"/Volumes/KINGSTON 2/apps/apps/corretor de redação/corretor x/11 - Corretor X Redação ENEM/scripts/run_caso_sabia.sh" caso-002 CASO-002 "Aluno 002"
```

Para validar sem API:

```bash
CORRETOR_X_DRY_RUN=1 "/Volumes/KINGSTON 2/apps/apps/corretor de redação/corretor x/11 - Corretor X Redação ENEM/scripts/run_caso_sabia.sh" caso-002 CASO-002 "Aluno 002"
```

Comando manual, caso esteja dentro da pasta `11 - Corretor X Redação ENEM`:

```bash
../../.venv/bin/python scripts/corrigir_com_sabia.py \
  --tema-file entradas/caso-001/tema.txt \
  --redacao-file entradas/caso-001/redacao.txt \
  --case-id CASO-001 \
  --aluno-id "Aluno 001" \
  --out-xlsx "Cérebro do 1000/casos/exports/CASO-001.xlsx"
```

## Como funciona

O script faz uma chamada 0 antes das competências para verificar anulação total pela Cartilha ENEM 2025.

Se a chamada 0 retornar `anulado = true`, o script não executa C1-C5 e preenche o Excel com nota 0 nas cinco competências, registrando o motivo e a evidência da anulação.

Se a chamada 0 retornar `anulado = false`, o script faz uma chamada separada para cada competência:

- C1;
- C2;
- C3;
- C4;
- C5.

Cada chamada deve retornar JSON com:

- `competencia`;
- `nota_corretor_x`;
- `comentario_do_erro`;
- `evidencia_no_texto`;
- `sugestao_de_melhoria`;
- `nivel_confianca`.

O prompt-base usado pelo script inclui gates de anulação antes da nota, regra de tangenciamento para C3 e C5, ordem de autoridade metodológica e instrução para escolher a faixa inferior em caso de dúvida entre duas notas.

Campos opcionais por caso:

- `status-tema.txt`: `verificado`, `inferido` ou `ausente`;
- `status-anulacao.txt`: `nenhuma` ou uma condição de anulação;
- `tangenciamento-c2.txt`: `true`, `1` ou `sim` para limitar C3 e C5 a 40 pontos.
- `num-linhas.txt`: número de linhas manuscritas estimadas, quando houver contagem humana.

Se `status-tema.txt` não existir, o script infere o status do tema a partir de `tema.txt`. Se `num-linhas.txt` não existir, o script estima a quantidade de linhas pela transcrição, usando quebras de linha e volume de palavras para evitar falso `texto_insuficiente` em transcrições digitadas por parágrafo. Quando houver contagem humana das linhas manuscritas, preferir `num-linhas.txt`.

Depois, o script preenche o [Template - Entrega Excel Corretor X.xlsx](templates/Template%20-%20Entrega%20Excel%20Corretor%20X.xlsx).

## Próximo controle

Depois da correção, preencher `nota_oficial_ou_validada` quando houver revisão humana. A aba `Calibração` calculará a diferença por competência.

## Conexões

- [[10 - Estratégia Sabiá para Correção]]
- [[11 - Formato Excel de Entrega]]
- [[Caso 001 - Primeira Redação]]
- [[05 - Calibração por Competência]]
