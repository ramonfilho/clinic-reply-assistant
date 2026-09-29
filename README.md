# clinic-reply-assistant

Vision: an automatic WhatsApp assistant for clinics that sells, schedules, updates the patient's status and follows up.

Scope delivered here: the first step of that assistant. For each new patient message, the system retrieves the replies the clinic gave to similar messages in its own history, and an LLM writes the reply from them. The attendant decides what to send. Selling, scheduling, status updates and follow-up are later steps and are not in this repository.

Status: in progress. The evaluation set is built before the retrieval code (ADR 0004).

## Run

```
uv sync
make test
CLINIC_RAW_DIR=/path/to/export make eval-set   # writes data/processed/ and reports/eval_set.json
```

## Data

The real export never enters this repository. `data/sample/` holds a synthetic sample with the same schema, so the pipeline runs end to end for a reader. To reproduce the README number, point `CLINIC_RAW_DIR` at the real export.

## Decisions

One record per decision, in `docs/adr/`.
