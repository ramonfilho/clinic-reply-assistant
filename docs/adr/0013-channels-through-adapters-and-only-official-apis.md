# ADR 0005: Channels enter through adapters, and only through official APIs

Status: accepted, 2026-10-20

Origin: this ADR is maintained with the product base and mirrored into this repository on 2026-10-21. The repository copy is updated from that origin.

## Context

Clients of the base (ADR 0001) reach their users on WhatsApp, on SMS, on a chat inside their website and, later, by voice. In the United States only 32% of adults use WhatsApp (Pew Research), so SMS carries the conversation there. There are two ways to connect to WhatsApp. The official one is the WhatsApp Business Platform, reached through a BSP (Business Solution Provider, the company that connects the client's account to Meta) or directly with Meta. The unofficial one uses bridges such as Evolution API, with the Baileys library underneath, which speak to WhatsApp through a protocol Meta does not publish. Evolution API is Apache 2.0 with an extra condition that a notice appear inside the system that uses it.

In the United States four rules apply to automatic messages in any sector. The TCPA (the federal law on automatic messages) requires consent and respect for STOP. 10DLC registration (the carriers' registry for SMS sent from an ordinary local number) takes one brand per client, and it accepts a Brazilian company number (CNPJ). California forbids a bot from hiding that it is a bot in order to sell, and Colorado requires an AI notice from 2027-01-01. In Brazil the LGPD applies, and each client's contract says who controls the data.

## Decision

1. Each channel enters through an adapter that translates it into the base's message format. The adapter is written once, and per client only the number and the account change.
2. WhatsApp is connected only through the official WhatsApp Business Platform, through a BSP or directly with Meta. Evolution API, Baileys and any other unofficial bridge stay out.
3. In the United States SMS is the main channel, and every US client gets its own 10DLC brand.
4. The web chat serves users who do not want WhatsApp. The web chat, WhatsApp and SMS adapters start from the MIT part of Chatwoot (ADR 0004).
5. Voice comes later, as one more adapter. It is heavier, because it has to listen and answer in under one second per turn, and Pipecat (BSD) or LiveKit Agents (Apache 2.0) give the code. A hosted voice platform can sit behind the same adapter as a provider.
6. The messaging rules live in the code, and each client's configuration turns on the ones that apply: consent and STOP for the TCPA, the bot disclosure for California, the AI notice for Colorado and the LGPD rules for Brazilian clients.

## Alternatives considered

The unofficial bridges were rejected, because they depend on a protocol Meta does not publish and because Evolution API adds its own notice to the product. WhatsApp as the only channel was rejected for the US share in the context.

## Consequences

Every new client needs an account with a BSP before its first WhatsApp message, and every US client needs a 10DLC registration before its first SMS. STOP handling and the consent check become test cases of the SMS adapter. US health clients get no WhatsApp channel (ADR 0006). The order in which channels get built follows the first client that needs each one.
