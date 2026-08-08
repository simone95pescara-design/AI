# Knowledge Policy

## Principio

Il repository è la memoria persistente e autorevole del progetto. Le conversazioni con gli agenti sono memoria di lavoro temporanea.

## Persistenza delle conferme

Ogni informazione progettuale significativa esplicitamente confermata deve essere registrata nel repository nella posizione appropriata.

Non è necessario salvare ogni messaggio o ragionamento. Deve essere persistito ciò che modifica lo stato di conoscenza del progetto o è necessario per ricostruirlo correttamente.

## Classificazione

Quando rilevante, la conoscenza deve essere distinguibile come:

- `FACT` — fatto verificato;
- `REQUIREMENT` — requisito;
- `CONSTRAINT` — vincolo;
- `ASSUMPTION` — ipotesi non verificata;
- `PROPOSAL` — proposta non approvata;
- `DECISION` — decisione confermata;
- `ISSUE` — problema già presente;
- `RISK` — evento futuro/incerto con impatto potenziale;
- `UNKNOWN` — informazione non nota;
- `SUPERSEDED` — sostituita da informazione successiva;
- `DEPRECATED` — non più valida per uso corrente.

## Regole epistemiche

- Non presentare un'assunzione come fatto.
- Non trasformare una proposta in decisione senza approvazione o delega esplicita.
- L'assenza di un'informazione nelle fonti consultate non prova automaticamente che non esista.
- La forza della conclusione non deve superare quella delle evidenze.
- Le informazioni sensibili al tempo devono essere valutate per freshness.
- Informazioni `SUPERSEDED` o `DEPRECATED` non possono costituire la baseline corrente.

## Provenance minima

Per informazioni esterne significative, conservare quando utile:

- source;
- data di verifica;
- versione/riferimento;
- livello di evidenza;
- eventuale validità temporale.

## Livelli di evidenza

- `E0` — unsupported;
- `E1` — inferred;
- `E2` — supported;
- `E3` — verified;
- `E4` — independently verified.

## Ciclo di vita

Una conoscenza persistente può attraversare, quando applicabile:

`PROPOSED → CONFIRMED → ACTIVE → SUPERSEDED/DEPRECATED`

La storia significativa non deve essere cancellata quando serve a comprendere perché la baseline è cambiata.
