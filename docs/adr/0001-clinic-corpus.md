# ADR 0001: Build the take-home on the clinic WhatsApp corpus

Status: accepted, 2026-09-24

## Context

This self-imposed take-home has to produce a public repository with a measured number in 8 hours of work, and it has to be a retrieval-augmented system, because 19 of the 69 job descriptions in the application tracker ask for LLM or RAG experience. Two data sources were available. One is the Bring Data lead-scoring project, which the author runs in production. The other is 13,583 WhatsApp conversations (206,999 messages) collected from one aesthetic clinic through BotConversa, for a product built with a partner whose clinic software has about 30 clients.

## Decision

Use the clinic corpus.

## Alternatives considered

Bring Data has no document corpus and no user who asks questions, so a retrieval system there would be a toy over the repository docs. A public corpus would be reproducible by anyone, but it would carry no real user and no real reply to measure against.

## Consequences

The conversations hold patient data, so the raw export never leaves the author's machine, and the repository carries the code and the evaluation, plus a synthetic sample (ADR 0003). The number in the README is measured on the real data, and a reader can reproduce the pipeline only on the sample. Bring Data stays for the second take-home, where its model is served on AWS in shadow mode.
