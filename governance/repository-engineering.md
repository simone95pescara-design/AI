# Repository Engineering V1 — APPROVATO

Stato: APPROVATO
Autorità: normativa ai sensi di `DEC-004` e della promozione in baseline su `main`.

## 1. Scopo

Definire una struttura di repository, una politica linguistica e di naming, una tassonomia documentale e confini software che impediscano crescita casuale, duplicazione di responsabilità, accoppiamento progressivo e inserimento opportunistico di nuovi file o moduli.

L'architettura deve essere **enforceable**, non solo documentata: ogni regola deterministica deve avere un controllo automatico prima che la migrazione sia considerata completata.

## 2. Principi vincolanti

1. Architettura prima del refactoring.
2. Una responsabilità primaria per modulo/file.
3. Un solo punto di ingresso umano del repository.
4. Le fonti normative devono essere distinguibili da documentazione descrittiva e artefatti macchina.
5. Naming e casing devono essere deterministici e verificabili.
6. Nuove directory top-level, nuovi package o nuovi layer richiedono una decisione architetturale esplicita.
7. La struttura Python deve essere un package installabile/testabile, non una raccolta di script crescenti.
8. I test devono seguire i confini architetturali del codice.
9. Le dipendenze tra layer devono essere verificabili automaticamente.
10. Il refactoring strutturale deve essere behavior-preserving e preceduto da characterization tests.
11. I contratti machine-readable devono restare linguisticamente stabili.
12. Le dipendenze esterne devono essere ammesse intenzionalmente, non aggiunte per convenienza locale.
13. La configurazione strutturale deve avere una source of truth unica.
14. Una nuova regola architetturale deterministica non è completa finché non esiste un controllo che possa rilevarne la violazione.

## 3. Lingua canonica

### 3.1 Italiano — contenuto umano

Lingua canonica del contenuto umano e normativo: **italiano**.

Devono essere in italiano:
- `README.md` e documentazione utente;
- prose normative in `governance/`;
- spiegazioni, razionali, guide e descrizioni rivolte alle persone;
- messaggi di handoff destinati all'utente quando persistiti come documentazione.

### 3.2 Inglese — contratti macchina e codice

Restano in inglese:
- codice Python;
- package, moduli, classi, funzioni, variabili e CLI flags;
- chiavi YAML/JSON e proprietà degli schema;
- enum/status machine-readable (`APPROVED`, `PROPOSED`, `PASSED`, ecc.);
- identificatori persistenti (`DEC-001`, `REQ-001`, `TASK-001`, ecc.);
- keyword normative standard (`MUST`, `SHOULD`, `MAY`) quando usate formalmente;
- nomi di API, protocolli, librerie e tecnologie;
- file speciali imposti da convenzioni/tool (`README.md`, `AGENTS.md`, `.github/`, `pyproject.toml`).

La localizzazione non deve rinominare chiavi machine-readable, enum, ID, API o contratti serializzati senza una migrazione di compatibilità esplicita.

## 4. Naming e casing

La convenzione è deterministica:

| Categoria | Convenzione |
|---|---|
| File speciali | nome richiesto dallo strumento/convenzione (`README.md`, `AGENTS.md`) |
| Documenti Markdown ordinari | `kebab-case.md` minuscolo |
| Directory repository non-Python | nome semplice minuscolo; se composto, `kebab-case` |
| Package/directory Python | `snake_case` |
| Moduli Python | `snake_case.py` |
| Test Python | `test_<unit>.py` |
| Artefatti persistenti | `<PREFIX>-NNN.yaml` |
| Schemi | `<artifact>.schema.json` |
| Template | `<artifact>.yaml` |

Non sono ammesse scelte locali alternative senza una modifica esplicita della policy.

### 4.1 Rename e compatibilità

Un rename di file/path referenziato deve essere trattato come migrazione:
1. inventario di tutti i riferimenti entranti;
2. aggiornamento atomico dei riferimenti;
3. verifica che non restino path obsoleti;
4. aggiornamento di bootstrap, CI, schema registry e documentazione quando applicabile;
5. test di cold-start/compliance se il path partecipa al bootstrap o alla governance.

Non sono ammessi rename cosmetici isolati che lascino riferimenti concorrenti o alias indefiniti.

## 5. Tassonomia documentale

### Root

- `README.md`: unico entry point umano; overview, quick start, struttura e link alle fonti normative. **Non può introdurre regole normative autonome.**
- `AGENTS.md`: istruzioni minime per agenti AI e puntatore al bootstrap.
- `BOOTSTRAP.md`: entry sequence operativa per agenti; la sua collocazione root resta ammessa perché è un file di bootstrap speciale già normativo.

### `docs/`

Documentazione descrittiva/non normativa per umani. Non può diventare source of truth per regole, lifecycle o status.

### `governance/`

Solo fonti normative o candidate chiaramente marcate. Ogni documento deve dichiarare stato e autorità.

### Artefatti macchina

Directory dedicate secondo il metamodel **attivo**. Un artifact type non ancora attivato può comparire solo come candidate/migration input e non deve essere presentato come parte del layout baseline attivo.

## 6. Layout target

Il layout target del software è:

```text
/
├── README.md
├── AGENTS.md
├── BOOTSTRAP.md
├── pyproject.toml
├── src/
│   └── ai_governance/
│       ├── domain/
│       ├── application/
│       ├── infrastructure/
│       └── cli/
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── architecture/
│   └── governance/
├── governance/
├── docs/
├── schemas/
├── templates/
├── decisions/
├── requirements/
├── risks/
├── state/
└── .github/
```

Le directory relative a artifact type aggiuntivi (`tasks/`, `verification/`, `diagnostics/`, `queue/`, ecc.) entrano nel layout baseline soltanto quando il relativo metamodel è `MODEL_ACTIVE`.

## 7. Architettura Python

### 7.1 `domain/`

Contiene il modello puro del dominio:
- persistent ID e artifact type;
- riferimenti tipizzati;
- status/lifecycle;
- invarianti pure;
- transition contract;
- error/finding model di dominio.

Non dipende da filesystem, YAML/JSON, GitHub, CLI o framework esterni.

### 7.2 `application/`

Contiene i casi d'uso e l'orchestrazione:
- repository compliance;
- post-promotion verification;
- candidate validation;
- aggregazione risultati;
- exit semantics applicative.

Dipende dal dominio e da porte/interfacce, non dalle implementazioni concrete di filesystem/GitHub.

### 7.3 `infrastructure/`

Contiene adattatori e implementazioni tecniche:
- repository/filesystem access;
- YAML/JSON serialization;
- JSON Schema loading/validation adapters;
- schema/artifact registry loading;
- secret scanning adapter;
- eventuali adapter Git/GitHub quando introdotti.

L'infrastruttura implementa porte richieste dall'application/domain; non contiene policy normativa propria.

### 7.4 `cli/`

Contiene esclusivamente:
- parsing argomenti;
- formatting dell'output;
- mapping exit code;
- entry point eseguibile.

Non implementa invarianti o regole di dominio.

## 8. Dependency direction

Dipendenze consentite:

```text
cli ------------> application ------------> domain
                       ^                       ^
                       |                       |
                 infrastructure --------------+
```

Regole:
- `domain` non importa da `application`, `infrastructure` o `cli`;
- `application` non importa da `cli`;
- `application` usa infrastructure attraverso porte/interfacce dove l'accoppiamento concreto comprometterebbe testabilità o sostituibilità;
- `infrastructure` può dipendere dal dominio per implementare contratti, ma non può definire nuove regole normative;
- queste dipendenze devono essere coperte da architecture tests prima della chiusura della migrazione.

## 9. Anti-god-module e complessità

Un modulo non deve contemporaneamente possedere più responsabilità architetturali indipendenti, per esempio discovery filesystem + parsing + regole semantiche + graph analysis + CLI output.

Trigger obbligatori di review/split:
- un modulo attraversa due o più layer architetturali;
- una funzione implementa più di una categoria normativa indipendente;
- l'aggiunta di una regola richiede modifiche ripetute a una grande catena di `if/elif` centralizzata;
- test di componenti distinti richiedono import del medesimo script-monolite;
- un modulo non è testabile senza costruire repository/CLI non necessari alla responsabilità testata.

Metriche di complessità possono essere introdotte successivamente come guardrail, ma non sostituiscono questi confini di responsabilità.

## 10. Registry e configurazione

Deve esistere una source of truth unica per la registrazione tecnica di:
- artifact type attivi;
- path owner;
- schema associato;
- ID prefix;
- eventuali parser/validator applicabili.

Il registry non deve duplicare la normativa: traduce il metamodel approvato in configurazione tecnica. Nuovi artifact type non devono richiedere modifiche sparse in molte mappe hard-coded indipendenti.

`pyproject.toml` è la source of truth per packaging/tooling Python; il registry applicativo vive nel package e ha una responsabilità distinta.

## 11. Error model

Le verifiche devono produrre findings strutturati, almeno con:
- `code` stabile;
- `severity`;
- `message` umano;
- `artifact/path` quando applicabile;
- `rule/invariant` di origine;
- eventuale `context` strutturato.

La CLI formatta findings esistenti; non deve costruire la semantica degli errori.

Gli exit code devono essere definiti centralmente dall'application/CLI contract.

## 12. API boundary

Tutto il package è interno finché non viene esplicitamente dichiarata un'API stabile.

Una funzione/classe non diventa API pubblica solo perché importabile. Eventuali API pubbliche future devono essere esposte intenzionalmente da entry point/moduli dedicati e governate con compatibilità/versioning.

## 13. Dipendenze esterne

Una nuova dipendenza runtime richiede:
- necessità tecnica documentata;
- verifica che la standard library o dipendenze già presenti non siano sufficienti;
- valutazione di manutenzione, licenza, sicurezza e lock-in;
- owner/caso d'uso identificabile;
- test che giustifichino il comportamento introdotto.

Non è ammesso aggiungere una libreria solo per evitare una progettazione semplice realizzabile internamente con costo ragionevole.

## 14. Toolchain minima

La migrazione deve definire una toolchain minima e non proliferante. Baseline proposta da valutare in fase implementativa:
- formatter/linter unico o suite minima equivalente;
- type checker per il core Python;
- pytest per test;
- architecture test per dependency direction;
- vulnerability/dependency check solo quando giustificato dal livello di maturità e dal rischio.

La scelta esatta degli strumenti è una decisione implementativa separata se introduce nuove dipendenze o policy significative.

## 15. Test architecture

- `tests/unit/`: dominio puro, parser isolati, reference/graph logic, findings.
- `tests/integration/`: filesystem/repository adapters, schema loading, fixture repository.
- `tests/architecture/`: dependency direction, import boundaries, package layout.
- `tests/governance/`: baseline reale, metamodel, cold-start/compliance contract.

Un test end-to-end non sostituisce i test unitari.

### 15.1 Characterization tests

Prima di estrarre comportamento da `compliance/validate.py` devono essere congelati characterization tests che descrivano almeno:
- input repository valido → PASS;
- principali classi di errore esistenti → stessi codici/esiti;
- secret scanning;
- schema validation;
- referential integrity;
- task/graph checks quando attivi;
- post-promotion behavior.

Ogni fase di refactoring deve dimostrare equivalenza rispetto al set di characterization tests, salvo cambiamenti comportamentali esplicitamente approvati.

## 16. Packaging e configurazione Python

`pyproject.toml` deve diventare source of truth per:
- metadata package;
- Python supportato;
- dipendenze runtime;
- dipendenze development/test;
- entry point CLI;
- configurazione pytest/tooling quando opportuno.

`compliance/requirements.txt` deve essere eliminato o generato solo per una necessità esterna esplicita; non può restare seconda source of truth manuale.

## 17. Regola per nuovi file/moduli

Prima di introdurre un nuovo file significativo l'agente deve determinare:
1. responsabilità primaria;
2. layer/owner;
3. owner equivalente già esistente;
4. rischio di duplicazione/source-of-truth concorrente;
5. dipendenze ammesse;
6. necessità di aggiornare layout/registry/architecture tests.

Se la collocazione richiede inventare una nuova categoria o viola il dependency model, la modifica deve fermarsi e diventare decisione architetturale.

## 18. Enforcement della repository architecture

Prima di dichiarare completata la migrazione devono esistere controlli automatici per almeno:
- package/layout atteso;
- dependency direction;
- naming machine-verifiable;
- assenza di vecchi entry point non autorizzati;
- unica source of truth delle dipendenze Python;
- artifact/schema registry coerente;
- riferimenti a path rinominati;
- baseline compliance e cold-start.

Le regole linguistiche sulla prose possono richiedere review umana; non devono essere simulate con controlli fragili che producono falsa sicurezza.

## 19. Piano di migrazione

Ordine obbligatorio:
1. approvare architettura e convenzioni;
2. creare characterization tests sull'implementazione esistente;
3. introdurre `README.md` e `pyproject.toml` senza cambiare comportamento;
4. creare package `src/ai_governance/` e architecture tests;
5. introdurre domain/error/registry contracts minimi;
6. estrarre progressivamente il comportamento da `compliance/validate.py` mantenendo equivalenza;
7. migrare `post_promotion.py` nei layer corretti;
8. aggiornare CI agli entry point canonici e rimuovere entry point legacy solo dopo equivalenza dimostrata;
9. stabilizzare package e dependency checks;
10. solo dopo, tradurre/normalizzare documentazione e naming attraverso una migrazione di riferimenti controllata;
11. rieseguire cold-start, compliance, post-promotion e characterization regression;
12. solo allora riprendere l'espansione funzionale congelata.

Nessun big-bang refactor.

## 20. Criteri di accettazione di DEC-004

Prima dell'approvazione devono essere accettati esplicitamente:
- italiano come lingua canonica della prose umana/normativa;
- inglese stabile per codice e contratti machine-readable;
- naming/casing deterministico;
- layout target con distinzione tra artifact type attivi e futuri;
- confini `domain/application/infrastructure/cli`;
- dependency direction;
- registry/configuration ownership;
- error model;
- dependency admission rule;
- test architecture e characterization tests;
- enforcement architetturale;
- `pyproject.toml` come source of truth Python;
- migration strategy incrementale.

L'approvazione di questo documento autorizza la direzione architetturale e i vincoli, non un refactoring big-bang né l'attivazione automatica di artifact type ancora candidati.