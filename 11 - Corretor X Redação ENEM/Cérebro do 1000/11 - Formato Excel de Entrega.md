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

Aba granular para auditoria pedagógica e treinamento de futuros corretores, com múltiplas linhas por redação. Cada linha registra um apontamento extraído dos JSONs das competências.

Colunas:

- `id_redacao`;
- `competencia`;
- `tipo_apontamento`;
- `subtipo`;
- `trecho_evidencia`;
- `gravidade`;
- `classificacao`;
- `justificativa`.

Tipos de apontamento:

- `desvio`: desvios de C1, com subtipo gramatical e gravidade;
- `repertorio`: repertórios de C2, com `subtipo` normalizado a partir da referência e classificação `produtivo`, `bolso` ou `nao_legitimado`;
- `inadequacao_coesiva`: problemas de C4, como `conector_sem_relacao`, `empilhamento`, `repeticao_inadequada` ou `paragrafo_isolado`;
- `elemento_proposta`: elementos de C5, com subtipo `agente`, `acao`, `meio`, `efeito` ou `detalhamento`.

Para C5, o script registra os cinco elementos esperados. Quando um elemento não for identificado, `trecho_evidencia` fica vazio e `justificativa` recebe `{subtipo} ausente`.

Exemplos de linhas:

- `red_001 | C1 | desvio | concordancia | "as crenças do africano foram" | media | |`;
- `red_001 | C2 | repertorio | utopia_more | "Utopia, de Thomas More" | | bolso | citação sem contextualização`;
- `red_001 | C2 | repertorio | djamila_ribeiro | "Pequeno Manual Antirracista" | | produtivo | obra explicada e articulada à tese`;
- `red_001 | C4 | inadequacao_coesiva | conector_sem_relacao | "portanto, vale ressaltar" | | | "portanto" sem relação conclusiva`;
- `red_001 | C5 | elemento_proposta | agente | "Ministério da Educação" | | | agente identificado`.

## Auditoria

Aba técnica com uma linha por chamada ao Sabiá, usada para rastreabilidade, reprocessamento e depuração das respostas do modelo.

Colunas:

- `id_chamada`;
- `id_redacao`;
- `timestamp`;
- `etapa`;
- `modelo`;
- `prompt_versao`;
- `prompt_hash`;
- `json_resposta_bruto`;
- `validacao_pydantic_ok`;
- `erros_pydantic`;
- `tempo_resposta_s`;
- `tokens_input`;
- `tokens_output`;
- `custo_estimado_usd`.

Regras:

- `etapa` usa `gate`, `c1`, `c2`, `c3`, `c4` ou `c5`;
- `prompt_hash` é o SHA-256 dos primeiros 500 caracteres do prompt enviado;
- `json_resposta_bruto` guarda o JSON completo extraído da resposta do Sabiá;
- `tokens_input`, `tokens_output` e `custo_estimado_usd` só são preenchidos se a API devolver esses metadados na resposta.

## Listas

Aba auxiliar com valores permitidos para competência, nota, confiança, OCR e validação.

## Regra de uso

`nota_oficial_ou_validada` só deve ser preenchida quando houver nota oficial, correção humana ou validação explícita. Sem essa coluna, a linha serve como devolutiva, mas ainda não calibra o modelo.

## Conexões

- [[03 - Banco de Casos Corrigidos]]
- [[05 - Calibração por Competência]]
- [[10 - Estratégia Sabiá para Correção]]
- [[08 - Política de Dados dos Casos]]
