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
- `governance/specification.md` — specifica di governance.
- `governance/transition-model.md` — modello normativo delle transizioni.
- `governance/repository-engineering.md` — architettura e convenzioni di repository/software.
- `governance/product-metamodel-v2.md` — direzione approvata del metamodel di prodotto; `SYS/BEH` non sono ancora artifact type attivi.
- `decisions/` — decisioni persistenti.
- `requirements/` — requisiti persistenti.
- `state/current.yaml` — proiezione sintetica dello stato corrente; non sostituisce gli owner autoritativi dei singoli fatti.
- `schemas/` e `templates/` — contratti machine-readable e modelli degli artefatti attivi/candidate secondo il registry e i test.
- `tests/` — unit, integration, architecture, governance e characterization test.

## Stato dell'ingegnerizzazione

`DEC-004` mantiene congelata l'espansione funzionale finché Repository Engineering V1 non supera il proprio exit gate. Lo stato operativo corrente non viene duplicato qui: usare `state/current.yaml` e `docs/repository-closure-audit.md`.

## Python

La configurazione Python canonica e unica source of truth per packaging e dipendenze è `pyproject.toml`.

Installazione locale con dipendenze di test:

```bash
python -m pip install ".[test]"
```

Compliance canonica:

```bash
ai-governance-compliance
```

Suite completa usata dalla CI:

```bash
python -m pytest tests/unit tests/governance tests/characterization tests/architecture tests/integration
```

Il package `ai_governance` è ancora interno: la versione `0.1.0` non dichiara un'API pubblica stabile.

## Principi di modifica

Le modifiche significative devono passare da working branch/candidate, verifiche automatiche e promotion controllata verso `main`. Nuove directory, layer, package o fonti di verità non devono essere introdotti opportunisticamente: devono rispettare `governance/repository-engineering.md` e, quando applicabile, il Transition Model vigente.
