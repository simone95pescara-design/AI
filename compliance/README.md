# Compliance

Questa cartella contiene i controlli automatici derivati dagli invarianti di governance.

## Esecuzione locale

```bash
python -m pip install -r compliance/requirements.txt
python compliance/validate.py
python -m pytest tests/governance
```

## Artefatti controllati

Il validator legge file YAML/YML/JSON nelle cartelle:

- `decisions/`
- `requirements/`
- `risks/`
- `state/`

Gli artefatti devono rispettare gli schemi presenti in `schemas/`.

## Controlli attivi

- `CHECK-001`: presenza dei file fondamentali di governance.
- `CHECK-002`: validità formale degli JSON Schema.
- `CHECK-003`: conformità degli artefatti ai rispettivi schemi.
- `INV-001`: riferimenti a requisiti esistenti.
- `INV-002`: decisioni `APPROVED` con rationale.
- `INV-003`: elementi `SUPERSEDED` con successore valido.
- `INV-004`: task `DONE` non compatibili con verifica `FAILED`.
- `INV-005`: requisiti `APPROVED` con metodo di verifica.
- `INV-006`: ID persistenti univoci.
- `INV-007`: supersessione delle decisioni reciproca e consistente.
- `INV-008`: rilevamento di alcuni pattern evidenti di secret.

## Principio

Il validator implementa regole già definite in `governance/invariants.md`; non deve diventare una fonte normativa indipendente.
