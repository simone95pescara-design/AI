# Authority Model

Questa policy definisce il livello minimo di autonomia richiesto per le azioni degli agenti.

## Livelli

### A0 — ANALYZE
Nessuna modifica. Analisi, lettura, confronto e raccomandazioni.

### A1 — LOCAL
Azioni locali, reversibili e a basso impatto.

### A2 — STANDARD CHANGE
Modifiche ordinarie entro requisiti, scope e architettura già approvati.

### A3 — PROJECT DECISION
Richiede approvazione per modifiche a requisiti, scope, architettura, baseline o dipendenze strategiche.

### A4 — CRITICAL
Richiede autorizzazione esplicita per operazioni distruttive, irreversibili, production-critical, security-critical o data-critical.

## Regole

- Un agente MUST NOT auto-aumentare il proprio livello di autorità.
- Se l'azione richiesta supera il livello disponibile, l'agente deve fermare la parte non autorizzata e richiedere una decisione.
- A parità di risultato, preferire l'azione con minore blast radius e maggiore reversibilità.
- Operazioni in production o su dati reali devono applicare criteri più restrittivi rispetto a dev/test.

## Matrice minima

| Azione | Livello minimo |
|---|---:|
| Analizzare repository | A0 |
| Correggere typo o documentazione locale | A1 |
| Fix conforme a requisito approvato | A2 |
| Nuova dipendenza strategica | A3 |
| Modifica requisito | A3 |
| Modifica architettura | A3 |
| Cambio baseline approvata | A3 |
| Deploy production significativo | A4 |
| Cancellazione dati | A4 |
| Migrazione irreversibile | A4 |
| Modifica security-critical | A4 |

## Escalation

Quando è richiesta escalation, la risposta deve rendere visibile almeno:

- decisione richiesta;
- motivo;
- impatto previsto;
- elementi interessati;
- eventuale opzione raccomandata.
