# Audit di readiness del metamodel

Stato: AUDIT NON NORMATIVO
Data: 2026-08-08
Oggetto: confronto tra la PR #4 `Operational Metamodel V1`, la baseline corrente e i requisiti minimi per guidare in modo ricostruibile e verificabile lo sviluppo di un sistema software reale.
Stress test concettuale: sistema di trading, usato esclusivamente per verificare la completezza del modello; nessun comportamento di trading viene attivato da questo documento.

## 1. Conclusione sintetica

La PR #4 affronta principalmente il **metamodel operativo del progetto**: lavoro da eseguire, lavoro differito, diagnosi, verifica e proiezione dello stato del progetto.

Questo è necessario, ma non sufficiente per derivare un sistema software. Manca ancora un **metamodel del prodotto/sistema** capace di rappresentare in modo autoritativo cosa il sistema deve fare, quali stati può assumere, quali eventi e comandi lo fanno evolvere, quali componenti possiedono le responsabilità, quali interfacce e dati attraversano i confini, quali vincoli devono rimanere veri e come ogni elemento viene verificato e collegato all'implementazione.

La PR #4 non deve quindi essere promossa nella forma storica. Deve essere trattata come input per una nuova proposta coerente con l'architettura corrente `domain/application/infrastructure/cli`.

## 2. Criterio di classificazione

- `KEEP`: concetto valido da preservare sostanzialmente.
- `REDESIGN`: concetto valido, ma struttura/contratto/implementazione devono essere ridisegnati sulla baseline corrente.
- `DROP`: soluzione storica da non trasportare nella nuova proposta.
- `MISSING`: capacità necessaria non rappresentata adeguatamente dalla PR #4.

## 3. Matrice PR #4

| Elemento PR #4 | Classificazione | Motivazione | Direzione V2 |
|---|---|---|---|
| `VER` — verification evidence | KEEP / REDESIGN tecnico | La separazione tra requisito/task e prova di verifica è corretta; provenance e baseline sono fondamentali. Lo schema storico va però adattato al nuovo domain model e a riferimenti tipizzati. | Mantenere un owner persistente della prova; distinguere verification, validation e runtime evidence senza duplicare test result già disponibili altrove. |
| `DIA` — diagnostics/root cause | KEEP | Separare osservazione, ipotesi, causa confermata e chiusura evita inferenze premature ed è utile anche durante sviluppo e operazioni. | Conservare il lifecycle epistemico; riferimenti tipizzati verso finding, task, requirement, risk, componenti e verifiche. |
| `QUEUE` — lavoro differito | KEEP / REDESIGN | La distinzione queue/task evita di presentare come eseguibile ciò che non è pronto. Il modello storico è però troppo vicino a una semplice lista di lavoro. | Mantenere deferred intent con condizioni di riattivazione e promozione esplicita; evitare duplicazioni con eventuale issue tracker esterno. |
| `TASK` — lavoro eseguibile | REDESIGN | Obiettivo, scope, dipendenze, authority, DoD e verification sono corretti; mancano però output attesi tipizzati e legami deterministici con elementi di sistema da modificare. | TASK deve rappresentare una change eseguibile derivata da requisiti/decisioni/design, non essere il luogo in cui nasce l'architettura del prodotto. |
| `STATE` come proiezione | KEEP | Una proiezione non proprietaria è coerente con cold-start e single ownership. | Rendere sempre più derivabili i campi; nessun fatto proprietario deve vivere solo in `state/current.yaml`. |
| general persistent-reference integrity | KEEP / REDESIGN | La referential integrity generale è necessaria. Il vecchio validator monolitico è superato. | Riferimenti tipizzati nel dominio, registry unico, regole per tipo e dependency graph esplicito. |
| task dependency/readiness/cycle checks | KEEP | Sono prerequisiti per selezione semi-autonoma sicura del lavoro. | Implementare nel domain/application usando il nuovo modello, non nel validator storico. |
| QUEUE↔TASK reciprocal promotion | KEEP | Evita identità e stato concorrenti. | Conservare come transition contract tipizzato. |
| diagnostic closure enforcement | KEEP | Impedisce chiusure senza causalità/evidenza adeguata. | Conservare con Finding strutturati e verification refs. |
| post-promotion check | REDESIGN | Il problema è reale: candidate marker e baseline devono essere coerenti dopo il merge. L'implementazione storica non è allineata alla nuova architettura. | Reintrodurre come use case applicativo con adapter Git/repository e test post-promotion. |
| attivazione atomica di `VER/QUEUE/DIA/TASK` | DROP | L'accoppiamento obbligatorio dei quattro artifact type crea un big-bang non necessario e contrasta con l'attuale strategia incrementale. | Attivare solo concetti con dipendenze realmente necessarie, attraverso decisioni/migrazioni verificabili. |
| modifiche dirette al vecchio `compliance/validate.py` | DROP | Il god-module è stato bonificato e non deve tornare source of truth dell'architettura/metamodel. | Ogni nuova regola segue `domain → application → infrastructure/cli` con architecture test. |
| schema storico TASK con `baseline` stringa e campi generici | REDESIGN | Utile come prima bozza ma non sufficiente per derivazione software e ownership delle modifiche. | Introdurre riferimenti strutturati a target di sistema, acceptance/verification e change set. |
| schema storico VER con evidence string list | REDESIGN | La provenance è buona, ma una lista di stringhe non garantisce riproducibilità o collegamento a risultati macchina. | Evidence reference tipizzato, metodo, ambiente, target revision, result, limitations e reproducibility metadata. |

## 4. Gap critico: progetto operativo vs sistema da costruire

Gli artifact `TASK/QUEUE/DIA/VER` rispondono soprattutto a domande del tipo:

- cosa dobbiamo fare;
- cosa è differito;
- che problema stiamo diagnosticando;
- come dimostriamo che una change è corretta;
- qual è lo stato corrente del progetto.

Per sviluppare automaticamente o semi-automaticamente un sistema serve anche rispondere in modo persistente e machine-checkable a domande diverse:

- qual è il confine del sistema;
- quali capacità deve fornire;
- quali comportamenti/scenari sono ammessi;
- quali stati e transizioni esistono;
- quali eventi/command causano le transizioni;
- quali invarianti runtime non devono mai essere violati;
- quali componenti possiedono quali responsabilità;
- quali interfacce, protocolli e contratti collegano i componenti;
- quali dati esistono, chi li possiede e quali semantiche hanno;
- quali configurazioni/ambienti alterano il comportamento;
- quali requisiti non funzionali e limiti operativi sono vincolanti;
- quali failure mode e strategie di recovery devono essere gestiti;
- quale codice/test/config/deployment realizza e verifica ciascun elemento.

Questa seconda famiglia di conoscenza non è ancora modellata in modo sufficiente.

## 5. Capacità mancanti per un metamodel di sviluppo software

| Capacità | Stato | Perché serve |
|---|---|---|
| System boundary / context | MISSING | Impedisce che responsabilità interne, attori esterni e dipendenze vengano confusi. |
| Capability / responsibility model | MISSING | Collega requisiti ad aree di responsabilità stabili prima dei task implementativi. |
| Behavior / scenario model | MISSING | Rende esplicito il comportamento osservabile invece di lasciarlo implicito nei requisiti o nel codice. |
| State machine / transition model di prodotto | MISSING | Serve per lifecycle runtime, precondizioni, transizioni illegali e recovery. Il transition model di governance non sostituisce quello del prodotto. |
| Event / command model | MISSING | Definisce cause delle transizioni, input, output, idempotenza e ordering. |
| Component / ownership model | MISSING | Consente di derivare moduli/servizi e impedisce distribuzione casuale delle responsabilità nel codice. |
| Interface / contract model | MISSING | Necessario per API, adapter, protocolli, error contract e compatibilità. |
| Data / information model | MISSING | Definisce entità, unità, precisione, temporalità, ownership e lineage. |
| Runtime invariant / policy model | MISSING | Formalizza vincoli che devono valere durante l'esecuzione, non solo durante la governance del repository. |
| Configuration / environment model | MISSING | Separa comportamento configurabile da codice e rende riproducibili test/deployment. |
| Non-functional requirements / SLO | PARTIAL | I `REQ` possono contenerli, ma manca una struttura che li colleghi a componenti, misure e verification evidence. |
| Failure mode / recovery model | PARTIAL | `RISK` e `DIA` aiutano, ma manca il contratto operativo del prodotto: detection, containment, retry, rollback, degraded mode. |
| Traceability to implementation | MISSING | Manca una relazione verificabile tra requirement/design/behavior e file, package, test, config, migration/deployment. |
| Derived change plan | MISSING | Il repository non può ancora trasformare automaticamente un delta di requisito in un set minimo di componenti/contratti/test da cambiare. |

## 6. Stress test: sistema di trading

Un sistema di trading evidenzia rapidamente i gap perché richiede almeno:

- market-data ingestion con timestamp, qualità e lineage;
- signal/strategy behavior con input e output determinati;
- portfolio/position state;
- pre-trade e post-trade risk invariants;
- order lifecycle e state machine (`created/submitted/acknowledged/partially_filled/filled/cancelled/rejected/...`);
- command/event ordering, retry e idempotenza;
- execution venue/broker interfaces;
- reconciliation tra stato interno ed esterno;
- precisione numerica, unità, valuta e rounding policy;
- clock/session/calendar semantics;
- failure handling, stale data, disconnect, partial execution e recovery;
- backtest/simulation assumptions e separazione tra simulated/live behavior;
- audit trail e verificabilità delle decisioni operative.

La PR #4 può gestire il lavoro necessario a implementare questi elementi, ma non può ancora **rappresentare questi elementi come modello autoritativo del sistema**. Di conseguenza non può ancora determinare in modo affidabile quale software debba essere generato o modificato.

## 7. Catena target di derivazione

Il metamodel V2 deve rendere attraversabile e verificabile almeno la catena:

`NEED / GOAL → REQ → DEC → SYSTEM ELEMENT → BEHAVIOR → STATE/TRANSITION → INTERFACE/DATA → INVARIANT → VERIFICATION → IMPLEMENTATION → TASK`

Il punto chiave è che `TASK` viene **dopo** la definizione sufficiente del sistema. Un task non deve diventare il contenitore informale in cui un agente inventa requisito, architettura e comportamento mentre implementa.

Non è ancora deciso che ogni nodo della catena debba corrispondere a un nuovo artifact type. Prima va minimizzato il metamodel distinguendo:

1. concetti che richiedono identità/lifecycle/versionamento propri;
2. concetti che possono essere sezioni strutturate di artifact esistenti;
3. proiezioni derivabili che non devono avere ownership autonoma.

## 8. Prerequisiti per dichiarare il repository pronto a un vertical slice reale

Prima di introdurre il trading come primo sistema concreto devono essere soddisfatti almeno questi criteri:

1. definizione approvata del metamodel minimo di prodotto;
2. ownership univoca per ogni categoria di conoscenza;
3. schema/contratti machine-readable per gli elementi attivati;
4. riferimenti tipizzati e traceability graph;
5. lifecycle e invarianti deterministici dove applicabili;
6. mapping esplicito da modello a package/componenti/test/config;
7. capability di derivare una change impact analysis da un requisito modificato;
8. verification evidence collegabile al target e alla revision verificata;
9. cold-start in cui un'altra AI ricostruisce non solo lo stato del progetto ma anche struttura e comportamento del sistema;
10. un vertical slice piccolo che dimostri end-to-end `requirement → design/behavior → implementation → verification` senza conoscenza critica lasciata solo nella chat.

## 9. Raccomandazione

La prossima change normativa non deve essere il merge della PR #4. Deve essere una nuova proposta di **Metamodel V2 minimo**, costruita dalla baseline corrente e da questo audit.

La proposta V2 deve:

- preservare le parti `KEEP` della PR #4;
- ridisegnare le parti `REDESIGN` sulla nuova architettura;
- non reintrodurre le parti `DROP`;
- chiudere prima i gap `MISSING` indispensabili alla derivazione software;
- evitare proliferazione di artifact type: ogni nuovo owner persistente deve essere giustificato da identità, lifecycle, versionamento o verifica indipendente;
- usare un micro vertical slice di trading solo come prova di completezza, non come fonte di regole speciali del framework.

## 10. Stato della PR #4

La PR #4 resta una proposta storica `draft` e non deve essere promossa direttamente. Dopo la creazione e l'approvazione della proposta V2, la PR #4 potrà essere chiusa come superseded con riferimento alla nuova decisione/proposta, preservandone la history come evidence di progetto.
