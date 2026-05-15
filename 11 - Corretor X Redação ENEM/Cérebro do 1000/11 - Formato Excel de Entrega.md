# Formato Excel de Entrega

Status: ativo

Arquivo: [Template - Entrega Excel Corretor X.xlsx](templates/Template%20-%20Entrega%20Excel%20Corretor%20X.xlsx)

## Decisão

A entrega operacional da correção será em Excel, com uma linha consolidada por redação na aba `Devolutiva`.

Cada redação deve gerar uma linha com notas, comentários, sugestões, anulação, tangenciamento, teto aplicado e confiança geral.

## Abas do modelo

## Resumo

Aba analítica para coordenação e time pedagógico, com uma linha por redação e KPIs extraídos dos JSONs das competências.

Colunas:

- `id_redacao`;
- `data_correcao`;
- `aluno_escola`;
- `tema`;
- `nota_final`;
- `nivel_proficiencia`;
- `nota_c1`;
- `nota_c2`;
- `nota_c3`;
- `nota_c4`;
- `nota_c5`;
- `total_desvios_c1`;
- `reincidencia_c1`;
- `abordagem_tema_c2`;
- `qtd_repertorios`;
- `qtd_repertorios_bolso`;
- `projeto_texto_c3`;
- `autoria_c3`;
- `diversidade_coesiva_c4`;
- `total_elementos_c5`;
- `articulacao_proposta_c5`;
- `respeita_dh_c5`;
- `confianca_geral`;
- `custo_tokens_total`;
- `tempo_processamento_s`.

Níveis de proficiência:

- `Insuficiente`: nota final menor que 500;
- `Regular`: 500 a 699;
- `Bom`: 700 a 849;
- `Excelente`: 850 a 1000.

## Devolutiva

Aba principal para aluno, professor ou operação pedagógica.

Colunas:

- `id_redacao`;
- `data_correcao`;
- `aluno_nome`;
- `aluno_escola`;
- `tema`;
- `status_tema`;
- `anulada`;
- `motivos_anulacao`;
- `tangenciamento`;
- `nota_c1`;
- `nota_c2`;
- `nota_c3`;
- `nota_c4`;
- `nota_c5`;
- `nota_final`;
- `teto_aplicado_c3`;
- `teto_aplicado_c5`;
- `comentario_c1`;
- `comentario_c2`;
- `comentario_c3`;
- `comentario_c4`;
- `comentario_c5`;
- `sugestao_c1`;
- `sugestao_c2`;
- `sugestao_c3`;
- `sugestao_c4`;
- `sugestao_c5`;
- `confianca_geral`;
- `alertas`.

## Calibração

Resumo automático por competência. A estrutura antiga do template ainda será substituída na próxima revisão de abas auxiliares, pois a `Devolutiva` agora é consolidada por redação.

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
