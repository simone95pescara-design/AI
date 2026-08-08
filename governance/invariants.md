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

## INV-011 — Evidenza di verifica
Un artefatto `VER-*` con stato `PASSED` deve contenere evidenza non vuota attribuibile al target e alla baseline dichiarati.

## INV-012 — Ownership del task attivo
Un `TASK-*` in stato `DOING` deve avere ownership esplicita.

## INV-013 — Promozione queue valida
Un `QUEUE-*` in stato `PROMOTED` deve indicare tramite `promoted_to` un `TASK-*` esistente. La promozione non riutilizza l'identità QUEUE come identità TASK.

## INV-014 — Diagnosi epistemicamente coerente
Un `DIA-*` non può dichiarare una root cause confermata senza una causa esplicita; lo stato diagnostico e `root_cause_status` devono essere coerenti.

## INV-015 — Proiezione di stato valida
Gli ID dichiarati da `state/current.yaml` come task attivi, lavoro in queue o diagnostiche aperte devono risolvere rispettivamente a `TASK-*`, `QUEUE-*` e `DIA-*` esistenti.

## INV-016 — Singola ownership della conoscenza
Quando un fatto ha un owner artifact definito dal metamodel, una proiezione o un summary non può sostituirsi all'owner né contraddirlo. Il controllo automatico completo richiede ulteriori regole di derivazione e resta parzialmente implementato.

## Stato di automazione

Nel candidate Operational Metamodel V1 il validator automatizza `INV-001`–`INV-008` per le porzioni già esistenti e `INV-011`–`INV-015` per VER/QUEUE/DIA/TASK/STATE. `INV-009`, `INV-010` e la parte generale di `INV-016` restano da implementare quando i relativi modelli e derivazioni saranno formalizzati.

## Evoluzione

Una nuova regola automatizzabile deve essere documentata qui prima o nello stesso candidate change che ne implementa il validator. Il codice di compliance non deve introdurre requisiti normativi non documentati.
