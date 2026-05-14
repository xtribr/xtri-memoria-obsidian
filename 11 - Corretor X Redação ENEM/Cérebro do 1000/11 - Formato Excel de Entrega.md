# Formato Excel de Entrega

Status: ativo

Arquivo: [Template - Entrega Excel Corretor X.xlsx](templates/Template%20-%20Entrega%20Excel%20Corretor%20X.xlsx)

## Decisão

A entrega operacional da correção será em Excel, com uma linha por competência.

Cada redação deve gerar cinco linhas:

- C1;
- C2;
- C3;
- C4;
- C5.

## Abas do modelo

## Resumo

Explica o fluxo de preenchimento e o significado dos campos.

## Devolutiva

Aba principal para aluno, professor ou operação pedagógica.

Colunas:

- `id_redacao`;
- `aluno_id`;
- `tema`;
- `competencia`;
- `nota_corretor_x`;
- `comentario_do_erro`;
- `evidencia_no_texto`;
- `sugestao_de_melhoria`;
- `nota_oficial_ou_validada`;
- `fonte_nota`;
- `diferenca`;
- `nivel_confianca`;
- `status_ocr`;
- `status_validacao`.

## Calibração

Resumo automático por competência:

- casos validados;
- diferença média;
- erro absoluto médio;
- contagem de generosidade;
- contagem de rigor excessivo.

## Listas

Aba auxiliar com valores permitidos para competência, nota, confiança, OCR e validação.

## Regra de uso

`nota_oficial_ou_validada` só deve ser preenchida quando houver nota oficial, correção humana ou validação explícita. Sem essa coluna, a linha serve como devolutiva, mas ainda não calibra o modelo.

## Conexões

- [[03 - Banco de Casos Corrigidos]]
- [[05 - Calibração por Competência]]
- [[10 - Estratégia Sabiá para Correção]]
- [[08 - Política de Dados dos Casos]]
