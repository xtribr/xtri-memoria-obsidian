# Padrão - Mapeamento de Simulados ENEM Dia 1

## Objetivo

Padronizar o mapeamento operacional do Dia 1 de simulados no formato ENEM para uso em planilhas da XTRI.

## Origem

- Conversa operacional com Professor Xandão em 2026-05-13.
- Aplicação real no arquivo `APEIRON 1/Mapa_D1_Apeiron_2026_RAIO-X.xlsx`.

## Status

`validado`

## Estrutura da planilha

Colunas exatas:

- `NR da questão`
- `Gabarito oficial`
- `Matéria + Assunto`

## Escopo do Dia 1

- Incluir `LC` e `CH`.
- Duplicar as questões `1-5` por idioma.
- Total esperado: `95` linhas.

Distribuição:

- `1 Inglês` a `5 Inglês`
- `1 Espanhol` a `5 Espanhol`
- `6` a `45`
- `46` a `90`

## Regras de preenchimento

- O gabarito oficial deve vir do gabarito comentado oficial do simulado.
- O campo `Matéria + Assunto` deve usar tópico curto.
- Não usar descrições longas do tipo `compreensão do papel social da arte e a análise de contextos históricos culturais`.
- Preferir o padrão `Matéria - tópico curto`.
- Em literatura, usar `gênero - autor - período/escola - tópico curto`.
- Em línguas estrangeiras e gêneros textuais, usar `gênero/objeto - tópico curto`.
- Se a taxonomia do material-base não encaixar bem, usar mapeamento semântico curto em vez de rótulo artificial.

## Formato recomendado

Exemplos válidos:

- `Artes - identidade`
- `Artes - idade contemporânea`
- `Geografia - geopolítica`
- `Sociologia - mídia`
- `História do Brasil - Segundo Reinado`
- `Crônica - Hilda Hilst - Contemporânea - polifonia`
- `Poema - Manuel Bandeira - Modernismo - fazer poético`
- `Romance - Júlia Lopes de Almeida - Realismo - obsessão pelo êxito`

## Restrições

- Não inventar gabarito.
- Não inventar autor quando o PDF não informar.
- Não repetir o mesmo rótulo em sequência quando as habilidades cobradas forem diferentes.
- Não deixar tópico genérico demais quando a questão exigir recorte mais preciso.

## Nota relacionada

- [[Regras Operacionais do Codex na XTRI]]
