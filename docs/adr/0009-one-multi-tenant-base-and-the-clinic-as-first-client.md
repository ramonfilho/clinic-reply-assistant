# ADR 0001: One multi-tenant base serves businesses of any kind, and the clinic is its first client

Status: accepted, 2026-10-20

Origin: this ADR is maintained with the product base and mirrored into this repository on 2026-10-21. The repository copy is updated from that origin.

## Context

The clinic repository started as a take-home on the WhatsApp history of one aesthetic clinic (ADR 0001 of the clinic repository), and its README states its vision as an automatic WhatsApp assistant for clinics. On 2026-10-18 the author changed the premise. The project is a base for AI customer-service assistants that serves businesses of any kind, many of them at once, and a clinic is one client of that base. In these records a client is a business that runs on the base, and a user is the person who writes to that business.

A review of the architecture on 2026-10-18 split the base into 13 pieces. Only one of them, the integration with each client's own software, needs new code per client. Everything else is common code that reads per-client content or configuration.

## Decision

1. Every table, document, vector, log line and cost record carries a `client_id`, and every query filters by it. Isolation is common code, written once.
2. What changes between clients is content (documents, frequently asked questions, prices, opening hours, tone of voice) and configuration (channels, language, model, handoff rule, the legal rules that apply). Code does not change per client.
3. Language is a configuration field. The lists that are Brazilian today, such as the CPF pattern of the scrubbing step (ADR 0003 of the clinic repository) and greetings like "blz" in the case rule (ADR 0005 of the clinic repository), become one list per language, so the English version is the same base with English lists.
4. The 13 pieces fall in three groups. Four are pure common code: isolation, the model function (ADR 0003), deploy and monitoring. Eight are common code with per-client content or configuration: channels (ADR 0005), knowledge, cold start (ADR 0002), the inbox with human handoff, API or local model, language, evaluation (ADR 0002) and legal rules. The last one, the integration with a client's software, needs code per software, and one adapter then serves every client that runs the same software.
5. Each client's knowledge comes from its own documents, read by retrieval (RAG) and stored with pgvector in the base's Postgres. The reader is common and the content belongs to the client.
6. The bot hands the conversation to a person when it cannot answer or when the user asks for one. The rule is configuration, and the inbox (ADR 0004) carries the conversation to the attendant.
7. Deploy is one command, on a shared server or on a server of a single client, and a new client enters by configuration. Monitoring shows, per client, the cost, the handoffs to a person and the replies the judge failed.
8. The BotConversa export reader already written in the clinic repository becomes the import path for any client with history in that tool.

## Alternatives considered

Building the base inside the clinic repository, on top of the take-home, was the plan of 2026-10-18 and 2026-10-19. It was set aside on 2026-10-20, when the author chose a private repository of its own for the base, because the take-home was made to become a public repository (ADR 0001 of the clinic repository) and the production code stays private. The clinic repository stays as the take-home it was, with ADRs 0001 to 0008 of the clinic repository as its record. A separate codebase per client or per kind of business was rejected on 2026-10-18, when the author decided that work for any client goes ahead only on the common base. A dedicated deployment per client stays available as a deploy option (decision 7), and it runs the same code.

## Consequences

ADRs 0001 to 0008 of the clinic repository describe the first client and its evaluation, and they stay in that repository with their status, its README and its name unchanged. A test checks that a query made for one client never returns a row of another client, and it runs with `make test`. Voice and actions inside a client's software come after the text channels.
