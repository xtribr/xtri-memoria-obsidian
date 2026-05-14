# Integração Sabiá

Status: ativo

## Objetivo

Usar o modelo `sabia-4` para gerar a primeira correção estruturada do Corretor X e preencher o Excel de entrega.

## Arquivo operacional

- [scripts/corrigir_com_sabia.py](../scripts/corrigir_com_sabia.py)

## Segurança da chave

Nunca salvar a chave da Maritaca/Sabiá no vault, no Git ou em arquivo `.env` versionado.

Use variável de ambiente:

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

O script faz uma chamada separada para cada competência:

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

Depois, o script preenche o [Template - Entrega Excel Corretor X.xlsx](templates/Template%20-%20Entrega%20Excel%20Corretor%20X.xlsx).

## Próximo controle

Depois da correção, preencher `nota_oficial_ou_validada` quando houver revisão humana. A aba `Calibração` calculará a diferença por competência.

## Conexões

- [[10 - Estratégia Sabiá para Correção]]
- [[11 - Formato Excel de Entrega]]
- [[Caso 001 - Primeira Redação]]
- [[05 - Calibração por Competência]]
