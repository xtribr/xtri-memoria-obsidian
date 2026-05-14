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

## Pré-requisito local

O script usa `openpyxl` para preencher o Excel:

```bash
python3 -m pip install -r scripts/requirements.txt
```

## Preparação do Caso 001

Criar arquivos locais ignorados pelo Git:

```bash
mkdir -p entradas/caso-001
```

Arquivos esperados:

- `entradas/caso-001/tema.txt`
- `entradas/caso-001/redacao.txt`

Se a redação vier por imagem ou PDF escaneado, seguir [[07 - Pipeline OCR]] antes de rodar a correção.

## Comando de teste sem API

```bash
python3 scripts/corrigir_com_sabia.py \
  --tema-file entradas/caso-001/tema.txt \
  --redacao-file entradas/caso-001/redacao.txt \
  --case-id CASO-001 \
  --aluno-id "Aluno 001" \
  --dry-run
```

## Comando de correção real

```bash
python3 scripts/corrigir_com_sabia.py \
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
