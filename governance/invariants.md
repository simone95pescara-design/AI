# Repository Invariants

Gli invarianti sono condizioni che devono rimanere vere per mantenere il repository internamente coerente.

## INV-001 — Riferimenti requisiti validi
Ogni riferimento a un requisito identificato deve puntare a un requisito esistente.

## INV-002 — Decisioni complete
Ogni decisione con stato `APPROVED` deve contenere una motivazione non vuota.

## INV-003 — Successione valida
Ogni decisione o requisito con stato `SUPERSEDED` deve indicare tramite `superseded_by` un successore esistente dello stesso tipo e diverso da sé.

## INV-004 — DONE coerente
Un'attività non può essere `DONE` quando la verifica associata è `FAILED`.

## INV-005 — Requisiti verificabili
Ogni requisito con stato `APPROVED` deve avere un `verification_method` non vuoto.

## INV-006 — Identità persistenti
Un identificativo persistente non può essere riutilizzato per un elemento diverso.

## INV-007 — Decisioni sostitutive
Una decisione che dichiara di sostituirne un'altra deve avere reciprocità di supersessione.

## INV-008 — Secret
Credenziali, token e secret non devono essere presenti nel repository.

## INV-009 — Handoff minimo
Ogni handoff aperto deve identificare almeno stato corrente e prossimo passo.

## INV-010 — Configurazione baseline
La configurazione dichiarata come baseline deve essere identificabile e versionata quando applicabile.

## INV-011 — Evidenza di verifica
Un artefatto `VER-*` con stato `PASSED` deve contenere evidenza non vuota.

## INV-012 — Ownership del task attivo
Un `TASK-*` in stato `DOING` deve avere ownership esplicita.

## INV-013 — Promozione queue reciproca
Un `QUEUE-*` in stato `PROMOTED` deve puntare a un `TASK-*` esistente e il task deve indicare reciprocamente `queue_source`.

## INV-014 — Diagnosi epistemicamente coerente
Un `DIA-*` non può dichiarare una root cause confermata senza una causa esplicita; stato diagnostico e `root_cause_status` devono essere coerenti.

## INV-015 — Proiezione di stato coerente
Gli ID proiettati da `state/current.yaml` devono esistere, avere il tipo corretto e uno stato compatibile con la categoria proiettata.

## INV-016 — Integrità referenziale generale
Ogni riferimento persistente `DEC/REQ/RISK/VER/QUEUE/DIA/TASK` deve risolvere a un artefatto esistente del tipo implicato dal proprio prefisso.

## INV-017 — Provenance della verifica
Un `VER-*` in stato `PASSED` deve identificare strutturalmente target e baseline/ref contro cui l'evidenza è stata prodotta.

## INV-018 — Dipendenze task
Le dipendenze `TASK→TASK` devono esistere, essere acicliche e non consentire `READY` quando dipendenze o blocker sono irrisolti.

## INV-019 — Chiusura diagnostica
Una diagnostica chiusa deve soddisfare le precondizioni della categoria di chiusura: rationale esplicita; evidenza di verifica per `CLOSED_RESOLVED`; rischio residuo per `CLOSED_ACCEPTED_UNKNOWN`.

## INV-020 — Singola ownership della conoscenza
Quando un fatto ha un owner artifact definito dal metamodel, una proiezione o un summary non può sostituirsi all'owner né contraddirlo.

## INV-021 — Post-promotion truth
Dopo una promotion su baseline, gli artefatti baseline-facing non devono conservare marker di candidate/proposal incompatibili con decisioni già approvate e promosse; la proiezione di baseline deve includere le decisioni normative promosse.

## Stato di automazione

Nel candidate Operational Metamodel V1 il validator automatizza gli invarianti deterministici sopra rappresentabili, incluso `INV-016`–`INV-019`. `compliance/post_promotion.py`, eseguito sui push a `main`, automatizza il primo controllo di `INV-021`. `INV-009`, `INV-010` e le derivazioni complete di `INV-020` restano da estendere con i relativi modelli.

## Evoluzione

Una nuova regola automatizzabile deve essere documentata qui prima o nello stesso candidate change che ne implementa il validator. Il codice di compliance non deve introdurre requisiti normativi non documentati.
