# Estratégia Sabiá para Correção

Status: proposta

## Objetivo

Usar Sabiá como motor de linguagem em português brasileiro para gerar correções pedagógicas, mas com controle metodológico do Corretor X.

## Premissa

Sabiá-3 é relevante para contexto brasileiro e português, mas a própria nota técnica registrada na wiki aponta cuidado com tarefas multi-etapas. Por isso, a correção não deve ser uma única chamada livre.

## Arquitetura recomendada

1. OCR ou entrada textual.
2. Normalização da redação.
3. Checagem de anulação e baixa confiança.
4. Avaliação separada por competência.
5. Extração de evidências textuais.
6. Revisão crítica da pontuação.
7. Geração da devolutiva final.
8. Registro em [[03 - Banco de Casos Corrigidos]].
9. Comparação com validação humana em [[05 - Calibração por Competência]].

## Papel ideal do Sabiá

- Explicar erros em português natural.
- Transformar rubrica em devolutiva compreensível.
- Gerar sugestões de reescrita sem substituir autoria.
- Adaptar tom para aluno, professor ou coordenação.
- Produzir relatório final no padrão XTRI.

## Travas obrigatórias

- Não corrigir sem tema completo quando a Competência II depender do tema.
- Não inventar texto motivador.
- Não inventar erro.
- Não citar trecho que não esteja na redação.
- Não entregar nota sem evidência por competência.
- Não ocultar baixa confiança.
- Não gerar intervenção pronta como resposta final do aluno; oferecer estrutura orientadora.

## Formato de devolutiva XTRI

1. Resultado executivo.
2. Tema e status da transcrição.
3. Nota total estimada.
4. Tabela C1-C5.
5. Comentário por competência.
6. Evidência textual curta.
7. Erro principal, quando houver.
8. Como melhorar.
9. Três prioridades de reescrita.
10. Alertas de baixa confiança.
11. Registro para calibração.

## Benchmark mínimo antes de produção

- Corrigir pelo menos 20 redações reais autorizadas.
- Comparar notas por competência com correção humana.
- Medir diferença média por competência.
- Identificar competências em que o modelo é generoso ou rigoroso demais.
- Atualizar [[06 - Decisões de Aprendizado]] somente com padrões recorrentes.

## Conexões

- [[09 - Benchmark REVI Devolutiva]]
- [[07 - Pipeline OCR]]
- [[01 - Rubrica Mestra ENEM]]
- [[04 - Erros do Corretor X]]
- [[06 - Decisões de Aprendizado]]
