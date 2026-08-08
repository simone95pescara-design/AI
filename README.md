# AI Project Governance Framework

Repository per progettare e verificare un sistema di governance che consenta a un assistente AI di ricostruire, governare e sviluppare un progetto in modo controllato e progressivamente più autonomo.

> `README.md` è un punto di ingresso umano e **non è una fonte normativa autonoma**. In caso di conflitto valgono le fonti normative e gli artefatti autoritativi del repository.

## Da dove iniziare

Per una persona:

1. leggere questo README per orientarsi;
2. consultare `state/current.yaml` per la proiezione dello stato corrente;
3. consultare `decisions/` e `requirements/` per decisioni e requisiti persistenti;
4. consultare `governance/` per le regole normative vigenti.

Per un agente AI:

1. leggere `AGENTS.md`;
2. seguire `BOOTSTRAP.md`;
3. ricostruire il progetto dalle fonti autoritative prima di eseguire modifiche.

## Fonti principali

- `AGENTS.md` — istruzioni minime per agenti AI.
- `BOOTSTRAP.md` — sequenza di cold-start e ricostruzione.
- `governance/SPECIFICATION.md` — specifica di governance.
- `governance/transition-model.md` — modello normativo delle transizioni.
- `governance/repository-engineering.md` — architettura e convenzioni di repository/software.
- `decisions/` — decisioni persistenti.
- `requirements/` — requisiti persistenti.
- `state/current.yaml` — proiezione sintetica dello stato corrente; non sostituisce gli owner autoritativi dei singoli fatti.
- `schemas/` e `templates/` — contratti machine-readable e modelli degli artefatti attivi.
- `tests/` — test di governance e characterization dell'implementazione legacy.

## Stato dell'ingegnerizzazione

`DEC-004` stabilisce che l'espansione funzionale resta subordinata al riallineamento ingegneristico del repository. La migrazione deve essere incrementale e behavior-preserving: characterization test, packaging e struttura, refactoring controllato del validator e, solo dopo, normalizzazione documentale e naming.

Lo stato operativo corrente non viene duplicato qui: usare `state/current.yaml` e gli artefatti autoritativi.

## Python

La configurazione Python canonica è `pyproject.toml`.

Durante la fase transitoria il validator legacy resta eseguibile con:

```bash
python compliance/validate.py
```

I test correnti possono essere eseguiti con:

```bash
python -m pytest tests/governance tests/characterization
```

La futura API/CLI del package `ai_governance` verrà introdotta durante la migrazione architetturale; il vecchio script non deve essere trattato come API stabile.

## Principi di modifica

Le modifiche significative devono passare da working branch/candidate, verifiche automatiche e promotion controllata verso `main`. Nuove directory, layer, package o fonti di verità non devono essere introdotti opportunisticamente: devono rispettare `governance/repository-engineering.md` e, quando applicabile, il Transition Model vigente.
