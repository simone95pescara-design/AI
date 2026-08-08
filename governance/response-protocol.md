# Response Protocol

## Obiettivo

Rendere osservabile l'applicazione della governance senza trasformare ogni risposta in un verbale rigido.

## Regola generale

La risposta resta naturale per default. Le sezioni strutturate devono comparire solo quando sono pertinenti.

## Indicatori standard

Usare etichette equivalenti a queste quando necessario:

- `ASSUMPTION` — ipotesi rilevante usata nel ragionamento;
- `CONFLICT` — fonti, requisiti o decisioni incompatibili;
- `RISK` — rischio materiale individuato;
- `BLOCKER` — elemento che impedisce di procedere correttamente;
- `DECISION REQUIRED` — serve approvazione umana;
- `CHANGED` — elementi effettivamente modificati;
- `VERIFIED` — verifiche realmente eseguite;
- `NOT VERIFIED` — verifica non eseguita o non possibile, con motivo;
- `RECORDED` — conoscenza persistita nel repository;
- `NEXT` — prossimo passo quando il lavoro resta aperto.

## Evidenza

Quando l'agente dichiara `CHANGED`, `VERIFIED` o `RECORDED`, deve indicare evidenza verificabile quando disponibile.

Esempi:

- file/path modificati;
- identificativo della decisione o requisito;
- test o check eseguiti;
- commit o altra baseline identificabile.

## Persistenza

Quando una conferma genera nuova conoscenza progettuale significativa, la risposta deve indicare dove è stata registrata.

Esempio:

`RECORDED — ADR-012 → docs/decisions/ADR-012.md`

## Verifica

L'agente non deve usare `VERIFIED` se la verifica non è stata realmente eseguita.

Se non è possibile verificare:

`NOT VERIFIED — <motivo>`

## Decisioni

Quando una modifica supera l'autorità disponibile, rendere esplicito almeno:

- `DECISION REQUIRED`;
- cosa deve essere deciso;
- impatto principale;
- elementi interessati;
- raccomandazione, se disponibile.

## Proporzionalità

Non mostrare sezioni vuote o irrilevanti. Una risposta semplice può restare semplice.
