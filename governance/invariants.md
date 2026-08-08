# Repository Invariants

Gli invarianti sono condizioni che devono rimanere vere per mantenere il repository internamente coerente.

## INV-001 — Riferimenti validi
Ogni riferimento a un requisito identificato deve puntare a un requisito esistente.

## INV-002 — Decisioni complete
Ogni decisione con stato `APPROVED` deve contenere una motivazione non vuota.

## INV-003 — Successione valida
Ogni decisione o requisito con stato `SUPERSEDED` deve indicare tramite `superseded_by` un successore esistente dello stesso tipo e diverso da sé. Un elemento `SUPERSEDED` o `DEPRECATED` non deve essere usato come baseline corrente.

## INV-004 — DONE coerente
Un'attività non può essere `DONE` quando la verifica associata è `FAILED`.

## INV-005 — Requisiti verificabili
Ogni requisito con stato `APPROVED` deve avere un `verification_method` non vuoto.

## INV-006 — Identità persistenti
Un identificativo persistente non può essere riutilizzato per un elemento diverso.

## INV-007 — Decisioni sostitutive
Una decisione che dichiara di sostituirne un'altra tramite `supersedes` deve riferirsi a una decisione esistente; la decisione sostituita deve essere `SUPERSEDED` e indicare reciprocamente la nuova decisione in `superseded_by`.

## INV-008 — Secret
Credenziali, token e secret non devono essere presenti nel repository.

## INV-009 — Handoff minimo
Ogni handoff aperto deve identificare almeno stato corrente e prossimo passo.

## INV-010 — Configurazione baseline
La configurazione dichiarata come baseline deve essere identificabile e versionata quando applicabile.

## Stato di automazione

Attualmente il validator automatizza `INV-001`–`INV-008` per le porzioni tecnicamente rappresentabili nel modello dati corrente. `INV-009` e `INV-010` restano da implementare quando verranno introdotti handoff e configuration artifact formali.

## Evoluzione

Una nuova regola automatizzabile dovrebbe essere aggiunta qui prima di implementarne il validator. Il codice di compliance non deve introdurre requisiti normativi non documentati.
