# Repository Engineering V1 — PROPOSTA

Stato: PROPOSTO
Autorità: diventa normativo solo dopo approvazione esplicita di `DEC-004`, verifica del candidate e promozione in baseline.

## 1. Scopo

Definire una struttura di repository, una politica linguistica e di naming, una tassonomia documentale e confini software che impediscano crescita casuale, duplicazione di responsabilità e inserimento opportunistico di nuovi file o moduli.

## 2. Principi

1. Architettura prima del refactoring.
2. Una responsabilità primaria per modulo/file.
3. Un solo punto di ingresso umano del repository.
4. Le fonti normative devono essere distinguibili da documentazione descrittiva e artefatti macchina.
5. Le convenzioni di naming devono essere deterministiche e verificabili.
6. Nuove directory o nuovi moduli top-level richiedono una motivazione architetturale esplicita.
7. La struttura Python deve essere un package installabile/testabile, non una raccolta di script crescenti.
8. I test devono seguire i confini architetturali del codice.

## 3. Lingua canonica

### 3.1 Documentazione umana e normativa

Lingua canonica proposta: **italiano**.

Sono mantenuti in inglese quando tecnicamente opportuno:
- identificatori persistenti (`DEC-001`, `REQ-001`, `TASK-001`);
- enum/status macchina (`APPROVED`, `PROPOSED`, `PASSED`, `FAILED`, ecc.);
- keyword normative standard (`MUST`, `SHOULD`, `MAY`) quando usate come termini formali;
- nomi di tecnologie, protocolli, API e concetti tecnici per cui la traduzione ridurrebbe precisione;
- nomi di file speciali richiesti da strumenti o convenzioni esterne (`README.md`, `AGENTS.md`, `.github/`).

La traduzione non deve cambiare identificatori, enum o semantica macchina.

### 3.2 Codice

Codice Python, nomi di moduli, classi, funzioni e variabili: inglese tecnico coerente con le convenzioni Python.

Commenti e docstring: preferibilmente inglese tecnico per il codice riutilizzabile; la documentazione utente resta italiana.

## 4. Naming e casing

- File speciali root: convenzione richiesta dallo strumento (`README.md`, `AGENTS.md`).
- Documenti normativi ordinari: `kebab-case.md` minuscolo.
- Directory: `snake_case` o nomi semplici minuscoli; evitare nuove varianti senza motivazione.
- Artefatti persistenti: `<PREFIX>-NNN.yaml` con prefisso e ID in maiuscolo.
- Schemi: `<artifact>.schema.json` minuscolo.
- Template: `<artifact>.yaml` minuscolo.
- Moduli Python: `snake_case.py`.
- Package Python: `snake_case` minuscolo.
- Test Python: `test_<unit>.py`.

Il casing non deve essere scelto caso per caso.

## 5. Tassonomia documentale

### Root

- `README.md`: unico entry point umano; spiega scopo, struttura, bootstrap, sviluppo e link alle fonti normative.
- `AGENTS.md`: istruzioni minime per agenti AI e puntatore al bootstrap.

### `docs/`

Documentazione descrittiva/non normativa per umani. Non deve diventare source of truth per regole di governance.

### `governance/`

Solo fonti normative approvate o candidate chiaramente marcate. Ogni documento deve dichiarare stato e autorità.

### Artefatti macchina

Directory dedicate (`decisions/`, `requirements/`, `tasks/`, ecc.) secondo metamodel attivo. Nessun README locale deve ridefinire la semantica normativa dell'artifact type; può solo spiegarne l'uso e puntare alla fonte normativa.

## 6. Layout target proposto

```text
/
├── README.md
├── AGENTS.md
├── pyproject.toml
├── src/
│   └── ai_governance/
│       ├── domain/
│       ├── validation/
│       ├── application/
│       └── cli/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── governance/
├── governance/
├── docs/
├── schemas/
├── templates/
├── decisions/
├── requirements/
├── tasks/
├── verification/
├── diagnostics/
├── queue/
├── risks/
├── state/
└── .github/
```

Il layout è una proposta e non autorizza ancora la migrazione.

## 7. Confini Python

### `domain/`

Modello puro del dominio: ID, artifact type, riferimenti, status, transizioni e invarianti rappresentabili senza accesso al filesystem.

Non deve contenere:
- CLI;
- scansione repository;
- GitHub Actions;
- output testuale;
- parsing di directory.

### `validation/`

Motore di validazione:
- schema validation;
- referential integrity;
- semantic rules;
- graph validation;
- repository consistency checks.

Le singole regole devono essere registrate come componenti testabili, non accumulate in una funzione monolitica.

### `application/`

Casi d'uso/orchestrazione:
- eseguire compliance repository;
- eseguire post-promotion check;
- aggregare risultati;
- definire exit status.

Non contiene regole di dominio primitive.

### `cli/`

Parsing argomenti, formatting output e entry point eseguibile.

## 8. Regole anti-god-module

Un modulo non deve contemporaneamente:
- scoprire file;
- parsare documenti;
- conoscere tutti gli schemi;
- implementare tutte le invarianti;
- gestire grafi;
- cercare secret;
- stampare output CLI.

Quando una modifica introduce una seconda responsabilità architetturale significativa nello stesso modulo, deve essere valutata un'estrazione prima del merge.

## 9. Dependency direction

Dipendenze ammesse:

```text
cli -> application -> validation -> domain
                       |
                       -> repository adapters
```

Il dominio non dipende da CLI, filesystem o GitHub.

## 10. Test architecture

- `tests/unit/`: regole pure, parser, graph/reference logic.
- `tests/integration/`: filesystem/repository candidate fixtures.
- `tests/governance/`: verifica che la baseline reale soddisfi governance e metamodel.

Un test end-to-end della repository compliance non sostituisce i test unitari delle regole.

## 11. Configurazione e packaging

`pyproject.toml` deve diventare la fonte canonica per:
- metadata package;
- versione Python supportata;
- dipendenze runtime;
- dipendenze development/test;
- entry point CLI;
- configurazione pytest e tooling quando opportuno.

`compliance/requirements.txt` deve essere eliminato o generato solo se esiste una necessità esterna esplicita; non deve essere una seconda fonte concorrente delle dipendenze.

## 12. Regola per nuovi file/moduli

Prima di introdurre un nuovo file significativo, l'agente deve determinare:
1. quale responsabilità possiede;
2. quale layer/directorio la possiede;
3. se esiste già un owner equivalente;
4. se il nuovo file crea duplicazione o nuova fonte di verità;
5. se richiede aggiornamento della repository layout policy.

Se la collocazione non è determinabile senza inventare una nuova categoria, la modifica deve fermarsi e trattare l'estensione della struttura come decisione di architettura.

## 13. Piano di migrazione proposto

Ordine obbligatorio:
1. approvare architettura e convenzioni;
2. introdurre `README.md` e `pyproject.toml` senza cambiare comportamento;
3. creare package `src/ai_governance/` e test layout;
4. estrarre progressivamente il comportamento da `compliance/validate.py` mantenendo test di regressione;
5. migrare `post_promotion.py` nel layer applicativo;
6. aggiornare CI agli entry point canonici;
7. solo dopo stabilizzazione, tradurre/normalizzare documentazione e naming secondo policy;
8. eseguire cold-start e compliance regression finali.

La migrazione deve essere incrementale e behavior-preserving; nessun big-bang refactor.

## 14. Criteri di accettazione

Prima dell'approvazione di DEC-004 devono essere accettati esplicitamente:
- lingua canonica;
- naming/casing;
- layout target;
- confini Python;
- dependency direction;
- test architecture;
- packaging/configuration source of truth;
- migration strategy.

L'approvazione di questo documento non approva automaticamente ogni dettaglio di implementazione del refactoring; autorizza la direzione architetturale e i vincoli entro cui progettare le singole migrazioni.
