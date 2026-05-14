# Política de Dados dos Casos

Status: ativo

## Objetivo

Evitar exposição indevida de redações reais, dados pessoais e arquivos originais de alunos.

## Regra padrão

Arquivos brutos de entrada não devem ser versionados no Git. Eles ficam em pastas locais ignoradas:

- `entradas/`
- `Cérebro do 1000/casos/originais/`
- `Cérebro do 1000/casos/transcricoes-privadas/`

## Quando um caso pode ser versionado

Um caso em Markdown só pode ser versionado quando:

- não tiver nome completo, matrícula, CPF, escola, telefone, e-mail ou outra identificação direta;
- o texto tiver autorização explícita para uso pedagógico; ou
- o caso estiver anonimizado o suficiente para estudo interno.

## Como anonimizar

- Trocar nome do aluno por `Aluno 001`, `Aluno 002` etc.
- Remover escola, turma, cidade pequena ou qualquer pista direta quando não for necessária à correção.
- Manter o tema, a redação e a análise pedagógica.
- Registrar limitações da anonimização no próprio caso.

## Conexões

- [[03 - Banco de Casos Corrigidos]]
- [[07 - Pipeline OCR]]
- [[Caso 001 - Primeira Redação]]
