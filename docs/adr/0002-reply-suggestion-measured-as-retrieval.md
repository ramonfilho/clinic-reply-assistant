# ADR 0002: Suggest the attendant's reply, measured as retrieval first

Status: accepted, 2026-09-24

## Context

Each conversation alternates patient messages and clinic replies, with the attendant's name and a timestamp on every message, so the corpus already holds pairs of patient message and real reply without any labeling. The median conversation has 10 messages. About a third of the messages are audio or images, and those stay out of this work.

## Decision

The system takes a new patient message and suggests a reply for the attendant. Stage one retrieves the most similar past patient messages and returns the replies the clinic gave them. Stage two, if the time budget allows, generates a reply with a language model from the retrieved replies. Stage one gets measured before any code of stage two is written.

## Alternatives considered

Answering the patient directly with generation only was rejected because there would be no ground truth to score against. Classifying the intent of the message was rejected because it would measure classification instead of retrieval, which is what the job descriptions ask about.

## Consequences

The metric of stage one is recall at 5 on held-out conversations: the share of new patient messages for which one of the five retrieved replies says the same thing the attendant actually answered. "Says the same thing" is decided by a similarity threshold between the retrieved reply and the real one, and the threshold is checked by hand on 50 cases before it is used. Stage two is judged on a sample of 100 cases.
