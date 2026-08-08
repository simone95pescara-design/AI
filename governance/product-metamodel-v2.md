# Product Metamodel V2 — PROPOSTA

Stato: PROPOSTO
Autorità: diventa normativo solo dopo approvazione esplicita di `DEC-005`, verifica del candidate e promozione in baseline.

## 1. Scopo

Definire il metamodel minimo necessario affinché il repository possa rappresentare in modo ricostruibile, verificabile e derivabile non solo il lavoro del progetto, ma anche il sistema software da costruire.

Il metamodel deve permettere a un agente AI di ricostruire il confine del sistema, la struttura, il comportamento, i vincoli, le prove e l'impatto di una modifica senza affidarsi a conoscenza critica presente solo nella conversazione o nel codice.

## 2. Principio di minimizzazione

Un nuovo artifact type è ammesso solo quando la conoscenza richiede almeno una tra: identità persistente autonoma, lifecycle proprio, versionamento indipendente, riferimenti esterni stabili o verifica indipendente.

Per evitare proliferazione, Product Metamodel V2 introduce solo due nuovi owner persistenti di prodotto:

- `SYS-*` — struttura e confine del sistema;
- `BEH-*` — comportamento osservabile/runtime del sistema.

Componenti, interfacce, dati, configurazioni, eventi, comandi, stati, transizioni e runtime invariant NON diventano automaticamente artifact top-level separati. Sono elementi strutturati con identificatori locali stabili all'interno di `SYS` o `BEH` e possono essere promossi a artifact autonomi solo mediante decisione successiva motivata.

## 3. Catena di derivazione

Il repository deve rendere attraversabile almeno la catena:

`NEED / GOAL → REQ → DEC → SYS → BEH → VERIFICATION → IMPLEMENTATION → TASK`

`SYS` e `BEH` possono riferirsi reciprocamente dove necessario, ma la responsabilità resta distinta:

- `SYS` risponde a **che cosa esiste, dove sono i confini e chi possiede cosa**;
- `BEH` risponde a **che cosa accade, in quali condizioni, con quali transizioni e vincoli runtime**.

`TASK` viene dopo una definizione sufficiente del delta di sistema. Non è il luogo in cui requisiti, architettura e comportamento vengono inventati implicitamente durante l'implementazione.

## 4. SYS — System Specification

Scopo: possedere il modello strutturale del prodotto/sistema.

Un `SYS-*` deve poter rappresentare almeno:

- system boundary e contesto;
- attori e dipendenze esterne rilevanti;
- capability/responsibility;
- componenti logici e relativa ownership;
- interfacce e contratti tra componenti o con sistemi esterni;
- modello dati/information ownership;
- configuration/environment dimensions che alterano il comportamento;
- allocazione di requisiti e decisioni ai system element;
- riferimenti all'implementazione corrente quando disponibili.

Gli elementi interni devono avere identificatori locali stabili, ad esempio `component.execution`, `interface.broker`, `data.order`, così da consentire riferimenti tipizzati senza creare un file top-level per ogni elemento.

### 4.1 Regole SYS

- ogni responsabilità significativa deve avere un owner identificabile;
- un'interfaccia deve identificare producer/consumer o provider/consumer;
- i dati devono identificare ownership e semantica essenziale quando rilevante;
- configurazioni che cambiano il comportamento devono essere esplicite e non nascoste nel codice;
- riferimenti a file/package/test sono mapping verso l'implementazione, non sostituti del modello;
- un cambio strutturale incompatibile richiede una decisione e una nuova revisione del `SYS` interessato.

## 5. BEH — Behavior Contract

Scopo: possedere il comportamento osservabile e i contratti runtime del sistema.

Un `BEH-*` deve poter rappresentare almeno:

- scenario/use case osservabile;
- trigger, command ed event rilevanti;
- precondizioni;
- input/output e postcondizioni;
- state machine quando esiste lifecycle runtime;
- stati e transizioni consentite/vietate;
- runtime invariant/policy;
- ordering, idempotenza e retry quando rilevanti;
- failure mode, detection, containment e recovery;
- collegamenti a `REQ`, `DEC` e agli elementi `SYS` responsabili;
- criteri di verifica e riferimenti alla evidence.

Gli elementi interni devono avere identificatori locali stabili, ad esempio `state.submitted`, `event.fill_received`, `transition.submit_order`, `invariant.max_risk`.

### 5.1 Regole BEH

- comportamento critico non deve restare descritto solo in prose libera o codice;
- una transizione deve identificare source, trigger/condition e target quando applicabile;
- gli stati illegali e le transizioni non consentite devono poter essere verificati;
- un runtime invariant deve avere condizione verificabile e target;
- failure/recovery devono distinguere detection, action e stato risultante;
- uno scenario deve essere collegabile a verification evidence.

## 6. Traceability e implementation mapping

Non viene introdotto un artifact `IMP-*` nella V2 minima.

L'implementazione resta posseduta dal repository sorgente. `SYS` e `BEH` possono contenere mapping strutturati verso:

- package/module/file;
- test automatici;
- schema/configuration;
- migration/deployment artifact;
- entry point o adapter.

Il mapping è verificabile ma non deve duplicare contenuto del codice. Il repository deve poter determinare almeno:

- quali system element sono implementati da quali target;
- quali behavior sono coperti da quali test/evidence;
- quali requirement/decision hanno copertura strutturale e comportamentale;
- quali target sono potenzialmente impattati da un delta di requisito o decisione.

## 7. Operational Metamodel: riuso selettivo della PR #4

Product Metamodel V2 non attiva automaticamente `TASK`, `VER`, `DIA` o `QUEUE`.

La direzione proposta è:

- `VER`: KEEP, da ridisegnare tecnicamente e attivare come owner della verification evidence;
- `TASK`: REDESIGN, da attivare dopo che il task può riferirsi a delta `SYS/BEH` determinati;
- `DIA`: KEEP, attivazione indipendente quando serve lifecycle diagnostico persistente;
- `QUEUE`: KEEP/REDESIGN, attivazione indipendente quando serve deferred work persistente;
- `STATE`: resta proiezione non proprietaria.

È vietata l'attivazione atomica obbligatoria dei quattro artifact type solo per ragioni storiche.

## 8. Riferimenti tipizzati

La V2 richiede un modello di riferimento capace di distinguere almeno:

- artifact reference: `REQ-001`, `DEC-005`, `SYS-001`, `BEH-001`;
- local element reference: `SYS-001#component.execution`, `BEH-001#transition.submit_order`;
- implementation reference: path/package/test/config con tipo esplicito.

La sintassi definitiva e il parser sono parte della fase implementativa e devono essere testati prima dell'attivazione dei nuovi artifact type.

## 9. Change impact analysis

Il metamodel è considerato utile solo se consente di derivare un change impact set.

Dato un requisito o una decisione modificata, il sistema deve poter risalire almeno a:

1. `SYS` e system element interessati;
2. `BEH` e behavior element interessati;
3. verification target da rieseguire o aggiornare;
4. implementation target potenzialmente da modificare;
5. task eseguibili da generare solo dopo che l'impatto è sufficientemente determinato.

La prima versione può produrre un insieme conservativo; non deve però inventare target senza traceability registrata.

## 10. Cold-start reconstructibility del prodotto

Un'altra AI deve poter ricostruire senza conversazioni pregresse:

- confine e scopo del sistema;
- principali capability e componenti;
- interfacce e dati critici;
- behavior/scenari principali;
- lifecycle e runtime invariant critici;
- mapping a requirement/decision;
- mapping a implementazione e verification evidence dove presenti;
- gap espliciti e conoscenza ancora non modellata.

La ricostruzione non richiede che ogni dettaglio sia duplicato nel metamodel: il modello deve puntare alle source of truth appropriate.

## 11. Stress test trading

Il trading è usato come stress test, non come fonte di regole speciali del framework.

Il metamodel deve poter rappresentare, senza nuovi artifact type ad hoc, almeno un micro-slice con:

- `SYS`: market-data source, strategy, risk gate, order manager, broker interface, portfolio/position data;
- `BEH`: ricezione dato di mercato → valutazione segnale → controllo rischio → submit order → acknowledge/fill/reject → aggiornamento stato;
- runtime invariant: limite di rischio pre-trade;
- failure path: stale data o broker unavailable;
- implementation mapping e verification evidence.

Se questo micro-slice richiede conoscenza critica lasciata solo in chat o codice, la V2 non è ancora pronta.

## 12. Sequenza di attivazione proposta

Nessun big-bang.

1. approvare il metamodel concettuale minimo;
2. definire schema `SYS` e `BEH` e riferimenti tipizzati;
3. introdurre domain types e invariant senza attivare artifact baseline;
4. aggiungere validator/application use case e test;
5. creare un micro vertical slice candidate di trading;
6. verificare cold-start e change impact analysis;
7. solo se la prova passa, attivare `SYS/BEH` come artifact type baseline;
8. attivare poi `VER` e `TASK` nelle forme ridisegnate, indipendentemente;
9. `DIA` e `QUEUE` restano attivazioni separate quando giustificate.

## 13. Criteri di accettazione di DEC-005

L'approvazione deve accettare esplicitamente:

- distinzione tra metamodel operativo del progetto e metamodel del prodotto;
- introduzione minima di soli `SYS` e `BEH` come nuovi owner di prodotto;
- elementi interni strutturati al posto della proliferazione di artifact top-level;
- catena `REQ/DEC → SYS → BEH → verification → implementation → TASK`;
- riferimenti a elementi locali stabili;
- traceability verso implementazione senza introdurre `IMP-*`;
- change impact analysis come capability obbligatoria;
- cold-start reconstructibility del prodotto;
- attivazione incrementale e non atomica di `SYS/BEH/VER/TASK/DIA/QUEUE`;
- micro vertical slice trading come prova di completezza prima dell'attivazione finale.

L'approvazione di questo documento autorizza la direzione del metamodel e la progettazione dei candidate schema/contratti. Non attiva automaticamente nuovi artifact type né autorizza la generazione autonoma di un trading system reale.
