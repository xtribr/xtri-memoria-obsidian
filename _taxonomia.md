---
type: Note
---
# Taxonomia de disciplinas — alinhada com `SIMULADOS 2026 xtri`

Esta é a nomenclatura canônica usada no campo `disciplina` de cada questão.

## Linguagens, Códigos e suas Tecnologias (LC)
- **Português** — interpretação, gramática, gêneros textuais, argumentação, variedades linguísticas
- **Literatura** — texto literário, escolas literárias, patrimônio literário nacional
- **Arte** — produção artística, manifestações culturais, diversidade estética
- **Educação Física** — manifestações corporais, cultura de movimento, esporte e saúde
- **Inglês** — LEM Inglês (idioma escolhido pelo aluno)
- **Espanhol** — LEM Espanhol (idioma escolhido pelo aluno)

## Ciências Humanas e suas Tecnologias (CH)
- **Filosofia** — ética, política, epistemologia, filosofia clássica/moderna/contemporânea
- **Geografia** — espaço, território, climatologia, geopolítica, urbanização, agropecuária
- **História** — Brasil colonial/império/república, ditadura, civilizações, história geral
- **Sociologia** — instituições sociais, movimentos sociais, cidadania, cultura, trabalho

## Ciências da Natureza e suas Tecnologias (CN)
- **Biologia** — ecossistemas, genética, evolução, fisiologia, saúde
- **Física** — mecânica, termodinâmica, eletromagnetismo, ondas, eletricidade
- **Química** — orgânica, inorgânica, físico-química, ambiental

## Matemática e suas Tecnologias (MT)

Disciplina única; sub-temas:
- **Aritmética** — números, operações, contagem
- **Álgebra** — equações, sistemas, expressões algébricas
- **Geometria** (genérico — quando plana/espacial não é distinguível pela habilidade)
- **Geometria Plana** — figuras planas, áreas
- **Geometria Espacial** — sólidos, volumes (3D)
- **Geometria Analítica** — pontos, retas, cônicas em plano cartesiano
- **Funções** — gráficos cartesianos, modelagem
- **Proporcionalidade** — razão, proporção direta/inversa
- **Unidades de medida** — escalas, grandezas
- **Estatística** — média, mediana, gráficos, tabelas
- **Probabilidade** — eventos, combinatória

## Confiança de classificação

Cada questão tem `disciplina_confianca` no frontmatter:
- **alta** — derivada de campo determinístico (idioma, área única) ou habilidade INEP cuja label aponta inequivocamente
- **media** — habilidade INEP indica probabilidade > 70% mas existe alternativa
- **indeterminada** — não dá pra inferir sem ler o enunciado (precisa OCR); `disciplina_candidatos` lista as opções viáveis

> Origem do mapping habilidade → disciplina: leitura curada das 120 labels da Matriz INEP em 2026-05-17.
