# Audit di chiusura Repository Engineering V1

Stato: AUDIT NON NORMATIVO
Data: 2026-08-08
Baseline analizzata: `main` dopo PR #26.
Scopo: determinare se Repository Engineering V1 / DEC-004 può essere dichiarata chiusa prima di riprendere Product Metamodel V2.

## 1. Esito

**NOT READY FOR CLOSURE.**

Il refactoring del nucleo Python è avanzato, ma la fase Repository Engineering non soddisfa ancora i propri exit gate. I gap rimanenti non sono soltanto cosmetici: alcuni compromettono cold-start, source-of-truth, entry point canonico, enforcement architetturale e coerenza tra decisioni approvate e documenti baseline-facing.

Fino alla chiusura dei gap `BLOCKER` e `REQUIRED`, l'espansione funzionale (`SYS/BEH`, trading vertical slice, nuovi artifact type) resta congelata.

## 2. Criteri di classificazione

- `OK`: requisito di closure soddisfatto.
- `FIX`: correggere mantenendo la stessa responsabilità/owner.
- `MIGRATE`: spostare responsabilità o percorso verso il target approvato.
- `REMOVE`: eliminare residuo/entry point/source concorrente dopo equivalenza verificata.
- `DECIDE`: serve una scelta esplicita prima della correzione.

Priorità:

- `BLOCKER`: impedisce di dichiarare la repository engineering chiusa.
- `REQUIRED`: necessario prima della ripresa dell'espansione funzionale.
- `CLEANUP`: ordinamento utile ma non sufficiente da solo a bloccare la closure.

## 3. Gap list finita

| ID | Priorità | Classificazione | Finding | Exit condition |
|---|---|---|---|---|
| RC-01 | BLOCKER | FIX | `state/current.yaml` è materialmente obsoleto: baseline e next actions descrivono ancora DEC-001/DEC-002, TASK-003 e la vecchia estensione operativa, mentre `main` include DEC-004, DEC-005 e le migrazioni successive. | La proiezione di stato rappresenta la baseline reale oppure viene resa derivabile/validata; nessuna next action storica resta presentata come corrente. |
| RC-02 | BLOCKER | FIX | `governance/transition-model.md` è su baseline ma si auto-etichetta ancora `APPROVED_CANDIDATE`; il difetto era già noto nello state e non è mai stato chiuso. | Header/status/authority coerenti con DEC-002 e con la baseline promossa; test post-promotion impedisce recidiva. |
| RC-03 | BLOCKER | FIX | `governance/repository-engineering.md` conserva header `PROPOSTA/PROPOSTO` nonostante DEC-004 sia `APPROVED` e il documento venga usato come norma corrente. | Marker baseline-facing coerenti con DEC-004; nessuna fonte normativa approvata si presenta ancora come proposta. |
| RC-04 | BLOCKER | MIGRATE/REMOVE | La CI esegue ancora `python compliance/validate.py`. Il file fuori `src/` è un compatibility wrapper legacy e rimane l'entry point operativo reale. | Entry point canonico installabile definito in `pyproject.toml`; CI usa quello; wrapper legacy rimosso dopo equivalenza/characterization PASS. |
| RC-05 | BLOCKER | MIGRATE | `src/ai_governance/cli/compliance.py` possiede ancora repository checks, schema loading/validation composition e repository orchestration, mentre Repository Engineering V1 assegna alla CLI solo parsing/formatting/exit mapping e all'application i use case. | Use case di repository compliance posseduto da `application`; adapter concreti in `infrastructure`; CLI sottile e testata come presentation/composition boundary. |
| RC-06 | REQUIRED | FIX | `pyproject.toml` è source of truth delle dipendenze ma non espone ancora un `[project.scripts]`/entry point canonico per compliance; versione `0.0.0` è ancora transitoria. | Entry point esplicito e installabile; decisione documentata sul versioning interno minimo. |
| RC-07 | BLOCKER | FIX | Gli architecture test verificano layer interni e dependency direction, ma non impediscono nuovo codice applicativo fuori `src/`, entry point legacy, naming repository, duplicate dependency sources, stale path references o cold-start/layout drift. | Enforcement automatico copre tutti i controlli deterministici richiesti dalla sezione 18 di Repository Engineering V1. |
| RC-08 | REQUIRED | FIX | Il modello `Finding` non soddisfa ancora il contratto approvato: mancano almeno `severity`, origine/rule e context strutturato previsti da Repository Engineering V1. | Error model implementato o norma aggiornata con decisione esplicita; CLI non ricostruisce semantica da stringhe. |
| RC-09 | REQUIRED | FIX | `README.md` documenta ancora il validator legacy e una command line test incompleta rispetto alla CI corrente; presenta inoltre la migrazione come fase ancora in corso senza riflettere la situazione attuale. | README aggiornato come unico human entry point e descrive esclusivamente entry point/processi correnti. |
| RC-10 | REQUIRED | FIX/MIGRATE | La policy linguistica approvata richiede italiano per prose umana/normativa, ma `BOOTSTRAP.md` è sostanzialmente inglese, l'apertura di `AGENTS.md` è inglese e `transition-model.md` è in inglese. | Migrazione controllata della prose umana/normativa in italiano senza rinominare chiavi, enum, ID o contratti macchina. |
| RC-11 | REQUIRED | MIGRATE | `governance/SPECIFICATION.md` viola il naming ordinario `kebab-case.md` approvato; eventuali riferimenti entranti rendono il rename una migrazione, non una correzione cosmetica. | Inventario riferimenti → rename atomico a naming conforme → aggiornamento registry/bootstrap/docs/test → nessun path obsoleto. |
| RC-12 | REQUIRED | FIX | Il registry tecnico richiede ancora `governance/SPECIFICATION.md` e non include `BOOTSTRAP.md`, `transition-model.md`, `repository-engineering.md` o `product-metamodel-v2.md` tra i required paths, quindi CHECK-001 non rappresenta completamente il bootstrap/normativa realmente necessaria. | Definizione esplicita e verificata dei required bootstrap/normative paths, senza duplicare la normativa nel registry. |
| RC-13 | BLOCKER | FIX | Il post-promotion check richiesto dal piano di migrazione non è presente nella CI corrente. Il persistere di marker `APPROVED_CANDIDATE/PROPOSTA` dimostra che il gap ha già prodotto drift reale. | Use case post-promotion nel layer corretto + CI su push a `main` + test dei marker/baseline-facing projections. |
| RC-14 | REQUIRED | DECIDE/FIX | Gli schema candidate `system.schema.json`, `behavior.schema.json`, `typed-reference.schema.json` sono su `main` pur restando fuori dal registry attivo. È consentito mantenere candidate input, ma la loro natura non attiva deve essere machine-discernible e non ambigua. | Convenzione unica per contratti candidate su baseline oppure metadata/test che ne rendano inequivocabile lo stato non attivo; nessuna discovery li tratta come artifact baseline. |
| RC-15 | REQUIRED | FIX | Non esiste ancora un controllo automatico di naming/casing per documenti, directory, schema, template e artifact persistenti, benché la convenzione sia deterministica e quindi enforceable. | Architecture/governance test rileva naming/casing non conforme con whitelist solo per file speciali approvati. |
| RC-16 | REQUIRED | FIX | Non esiste un controllo automatico che `pyproject.toml` sia l'unica source of truth Python e che non ricompaiano `requirements.txt`/dependency list concorrenti. | Test repository impedisce dependency source concorrenti non autorizzate. |
| RC-17 | REQUIRED | FIX | Non esiste ancora una verifica di cold-start aggiornata alla baseline corrente dopo DEC-004/DEC-005 e dopo il refactoring; REQ-001/REQ-002 risultano verificate su una baseline molto precedente. | Nuovo cold-start evidence sulla struttura reale corrente, capace di rilevare state/projection drift e candidate vs active model. |
| RC-18 | CLEANUP | FIX | Sono presenti branch merged/candidate residui (es. `candidate/sys-beh-schemas-v1`). Non alterano `main`, ma aumentano rumore operativo se usati come stato corrente. | Policy/cleanup branch definita e branch non necessari rimossi o chiaramente storicizzati. |

## 4. Elementi già conformi

- package Python sotto `src/ai_governance/` con layer `domain/application/infrastructure/cli`;
- `pyproject.toml` come fonte corrente di packaging e dipendenze;
- eliminazione di `compliance/requirements.txt`;
- characterization test prima e durante il refactoring legacy;
- registry tecnico centralizzato per gli artifact type attivi;
- discovery/parsing separati dalle regole di dominio;
- invariant principali migrati nel dominio;
- secret scanning separato in infrastructure;
- `README.md` root unico trovato come entry point umano;
- `SYS/BEH` non ancora registrati come artifact type attivi.

Questi elementi sono necessari ma non sufficienti per la closure.

## 5. Root cause di processo

Il pattern osservato non è un singolo file fuori posto. La causa di processo è che la migrazione è stata trattata come una sequenza di refactoring locali senza un **gate formale di chiusura della fase**. Dopo aver ridotto il god-module, l'espansione Product Metamodel V2 è ripartita prima di verificare tutti i criteri della sezione 18/19 di Repository Engineering V1.

Correzione preventiva: ogni fase futura deve avere:

1. scope congelato;
2. entry criteria;
3. finite gap list;
4. remediation tracciata;
5. exit criteria machine-checkable quando deterministici;
6. audit finale indipendente;
7. promotion della fase successiva solo dopo `PASS` del gate precedente.

## 6. Ordine di remediation proposto

L'ordine non è ancora esecuzione; è il piano derivato dall'audit.

**Wave A — Truth & promotion integrity**: RC-01, RC-02, RC-03, RC-13.

**Wave B — Canonical Python execution path**: RC-04, RC-05, RC-06, RC-08.

**Wave C — Architecture enforcement**: RC-07, RC-12, RC-15, RC-16.

**Wave D — Documentation normalization**: RC-09, RC-10, RC-11, RC-14.

**Wave E — Closure verification**: RC-17, audit finale, compliance/test suite completa.

RC-18 è cleanup finale e non deve contaminare le wave funzionali.

## 7. Exit gate Repository Engineering V1

La fase può essere dichiarata `CLOSED/STABLE` solo quando:

- tutti i `BLOCKER` sono chiusi;
- tutti i `REQUIRED` sono chiusi o esplicitamente rideterminati tramite decisione approvata;
- CI usa solo entry point canonici;
- nessun codice applicativo legacy non autorizzato resta fuori `src/`;
- naming/casing deterministico è enforced;
- dependency source of truth è enforced;
- documentazione normativa approvata non conserva marker candidate/proposal incompatibili;
- state/bootstrap rappresentano la baseline reale;
- post-promotion checks sono attivi;
- compliance + unit + integration + architecture + governance + characterization passano;
- un cold-start nuovo ricostruisce correttamente baseline, stato, artifact attivi/candidate e next action;
- un secondo audit non trova gap obbligatori aperti.

Solo dopo questo gate può riprendere Product Metamodel V2 dal passo `domain types + invariants for SYS/BEH`.
