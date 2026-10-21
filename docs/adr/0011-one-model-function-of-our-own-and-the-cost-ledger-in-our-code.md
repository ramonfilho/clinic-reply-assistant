# ADR 0003: One thin function of our own calls every model, and the cost ledger stays in our code

Status: accepted, 2026-10-20

Origin: this ADR is maintained with the product base and mirrored into this repository on 2026-10-21. The repository copy is updated from that origin.

## Context

ADR 0008 of the clinic repository already routes every language model call through one function, so the move from a local model to an API changes one file. With many clients (ADR 0001) that function has to do more. It picks each client's model, keeps a monthly budget per client, falls back to another model when the first one fails, and records what each call cost. Whether a client runs on an API or on a local model is decided per client.

LiteLLM was the ready candidate. Its SDK (MIT) puts more than 100 providers behind one API, according to its documentation, with retries, fallback, rate limits per provider, cache and a cost per call. That cost comes from a price table kept by its community, which the SDK downloads from their server by default. Budgets and limits per client live in the proxy, a separate server with Postgres and one virtual key per client. Budgets per tag, e-mail alerts and the audit log are in the Enterprise version, which has no public price. A reading of its public record on 2026-10-19 found five risks.

1. The GitHub security advisories page lists 17 advisories for the proxy, all between April and October 2026, and four of them are critical. One is an SQL injection that works without login (CVE-2026-42208, versions 1.81.16 to 1.83.6).
2. On 2026-03-24, versions 1.82.7 and 1.82.8 were published on PyPI with code that steals credentials. LiteLLM's own report says they stayed up about 40 minutes and reached whoever installed the SDK with pip. In a multi-client base, a theft like that would take every client's API key at once.
3. The PyPI metadata lists 22 direct dependencies for the SDK and 34 more for the proxy. Since June, 28 to 45 versions a month have come out, counting test releases.
4. FutureSearch reports that version 1.83.14, in June, started to drop tags by default. Their cost records went without a client for about six and a half days, and no error was raised.
5. An issue open since May reports that a custom price ignores the cache discount (67% overcharge in the reporter's example). A local model is exactly the case that needs a custom price.

Ollama and vLLM answer in the OpenAI API format, so the official Anthropic SDK (MIT) and the official OpenAI SDK (Apache 2.0) reach the three kinds of destination.

## Decision

1. The base has one function of its own that every model call goes through, and its signature is fixed from the first day. It receives the client and the messages.
2. The function reads the client's primary model and fallback model from Postgres, sums the client's spend for the month, and refuses the call when that spend has passed the client's cap.
3. It calls the provider through the official Anthropic SDK or the official OpenAI SDK. Ollama and vLLM are reached through the OpenAI SDK.
4. On error 429 (the provider's rate limit), on a 5xx error (a failure on the provider's side) or on a timeout, it retries with the fallback model.
5. At the end it writes one ledger row with client, model, input tokens, output tokens, cache tokens, cost and latency. The price table lives in our code, about eight rows. A local model costs zero in the ledger until a price per token, taken from the cost of the GPU, is set.
6. The LiteLLM SDK enters later, as one more provider behind the same function, in one of two cases: a fourth provider appears (Gemini, Bedrock or Azure), or translating tool calls between formats becomes weekly work. It then enters with its version pinned by hash and its price table kept on our server, and the code that calls the function does not change.
7. The LiteLLM proxy stays out. It comes back only if keys and dashboards have to be handed to third parties.

## Alternatives considered

The LiteLLM proxy was rejected for the risks in the context, and because a team of one would have to run Postgres and Redis and follow a stream of advisories. The LiteLLM SDK as the first layer was rejected because the ledger is where per-client cost comes from, and the FutureSearch case shows the risk of leaving that record to someone else's default behavior. The Portkey gateway (MIT, TypeScript) was rejected because Palo Alto Networks bought Portkey in 2026 and the repository has had no commit since 2026-05-25. OpenRouter was rejected because it does not run local models and client data would pass through a third party. Helicone (Apache 2.0) was rejected because Mintlify bought it in March 2026 and the announcement puts the product in maintenance mode.

## Consequences

The author's estimate, without measurement, is 30 to 50 hours to build the function. Most of that goes to tests and to translating tool calls and streaming (the reply arriving in pieces) between the Anthropic and the OpenAI formats. Maintenance means updating the price rows when a model or a price changes, plus the SDK versions, which the author estimates at two to four hours a month. Health clients are routed only to the models that ADR 0006 allows. ADR 0008 of the clinic repository keeps its single function, and this record says what that function does.
