# ADR 0005: A case is a patient turn and the clinic's next human reply

Status: proposed, 2026-09-24, to confirm with the author before the turn code is written

## Context

The export lists the messages of each conversation from the newest to the oldest, so a pairing done in file order matches a reply with the message before it instead of the message after it. Patients split one thought over several messages ("Sim", "Primeira vez", "Mas pela foto será apenas 1 ml pra cada lado?"), and the attendant answers in several messages too. Of the clinic's text messages, 26,052 carry no attendant in the field: 8,239 are the out-of-hours template, 13,348 carry the attendant's name as a bold prefix in the text, and 4,468 have no author at all (the bot flow). Many patient messages carry no content by themselves. "Sim" is a whole turn 1,261 times and "Pode sim" 515 times, and their reply depends on the question the clinic asked before.

## Decision

1. Messages are sorted by timestamp inside each conversation, and consecutive messages from the same side form one turn.
2. A case is a pair: a patient turn that has text, and the clinic turn that comes right after it, keeping only the messages written by a person (attendant in the field or in the bold prefix). A clinic turn with no human text gives no case.
3. A patient turn is a query only when it keeps at least 3 words after greetings and one-word acknowledgments are removed (the list lives in the code). The reply to "Sim" is not something a system can suggest from that message alone.

Measured on the export: 33,507 pairs, 25,243 of them with at least 3 content words. From the cutoff date of 2026-08-01 (ADR 0004): 3,507 pairs, 2,779 queries, in 1,602 conversations.

## Alternatives considered

Pairing message with message was rejected because the reply answers the whole turn. Including the previous clinic turn in the query would recover the "Sim" cases, and it stays as one row of the results table in the retrieval stage, where it is measured against the plain query. Keeping only turns with a question mark was rejected because patients state what they want without one ("Queria lábio, queixo e botox").

## Consequences

One pair in four is out of the evaluation as a short turn, and the README says the number covers content-carrying turns. The opener of the click-to-chat ads ("Oi! Gostaria de saber mais sobre a campanha de Harmonização...") is 1,048 of the 2,779 queries, and its reply is the same script every time, so the README reports recall at 5 twice: on all queries, and on the queries that are not a canned opener, where a canned opener is a query text that repeats verbatim 50 times or more in the training period.
