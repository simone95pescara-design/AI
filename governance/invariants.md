# Repository Invariants

Gli invarianti sono condizioni che devono rimanere vere per mantenere il repository internamente coerente.

## INV-001 — Riferimenti validi
Ogni riferimento a un requisito identificato deve puntare a un requisito esistente.

## INV-002 — Decisioni complete
Ogni decisione con stato `APPROVED` deve contenere una motivazione o un riferimento alla motivazione.

## INV-003 — Baseline corrente
Un elemento marcato `SUPERSEDED` o `DEPRECATED` non deve essere usato come baseline corrente.

## INV-004 — DONE coerente
Un'attività non può essere `DONE` quando una verifica obbligatoria associata è `FAILED`.

## INV-005 — Requisiti verificabili
Ogni requisito obbligatorio deve avere un metodo di verifica oppure essere esplicitamente marcato come non ancora verificabile.

## INV-006 — Identità persistenti
Un identificativo persistente non può essere riutilizzato per un elemento diverso.

## INV-007 — Decisioni sostitutive
Una decisione che modifica o sostituisce una decisione precedente deve mantenere una relazione esplicita con l'elemento sostituito.

## INV-008 — Secret
Credenziali, token e secret non devono essere presenti nel repository.

## INV-009 — Handoff minimo
Ogni handoff aperto deve identificare almeno stato corrente e prossimo passo.

## INV-010 — Configurazione baseline
La configurazione dichiarata come baseline deve essere identificabile e versionata quando applicabile.

## Evoluzione

Gli invarianti dovrebbero diventare controlli automatici quando tecnicamente possibile. Una nuova regola automatizzabile dovrebbe essere aggiunta qui prima di implementarne il validator.
