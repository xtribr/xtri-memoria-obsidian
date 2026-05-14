# Calibração por Competência

Status: ativo

## Objetivo

Comparar a nota estimada pelo Corretor X com a nota validada em cada competência.

## Métrica simples

Para cada caso:

- diferença C1 = nota estimada C1 - nota validada C1;
- diferença C2 = nota estimada C2 - nota validada C2;
- diferença C3 = nota estimada C3 - nota validada C3;
- diferença C4 = nota estimada C4 - nota validada C4;
- diferença C5 = nota estimada C5 - nota validada C5.

## Interpretação

- Diferença positiva: corretor foi generoso demais.
- Diferença negativa: corretor foi rigoroso demais.
- Diferença zero: alinhado.
- Diferença de 80 pontos ou mais: erro crítico de calibração.

## Saída esperada

Cada erro recorrente deve gerar:

- ajuste em [[Prompt Operacional]];
- ajuste em [[Protocolo de Correção]];
- registro em [[06 - Decisões de Aprendizado]].

## Planilha operacional

A calibração deve ser acompanhada no [Template - Entrega Excel Corretor X.xlsx](templates/Template%20-%20Entrega%20Excel%20Corretor%20X.xlsx), conforme [[11 - Formato Excel de Entrega]].

## Conexões

- [[03 - Banco de Casos Corrigidos]]
- [[04 - Erros do Corretor X]]
- [[01 - Rubrica Mestra ENEM]]
- [[11 - Formato Excel de Entrega]]
