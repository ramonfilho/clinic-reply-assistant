# clinic-reply-assistant

Reply suggestions for the attendant of a clinic's WhatsApp line. For each new patient message, the system retrieves the replies the clinic gave to similar messages in its own history and suggests one. The attendant decides what to send.

Status: in progress. The evaluation set is built before the retrieval code (ADR 0004).

## Run

```
uv sync
uv run pytest
```

## Data

The real export never enters this repository. `data/sample/` holds a synthetic sample with the same schema, so the pipeline runs end to end for a reader. To reproduce the README number, point `CLINIC_RAW_DIR` at the real export.

## Decisions

One record per decision, in `docs/adr/`.
