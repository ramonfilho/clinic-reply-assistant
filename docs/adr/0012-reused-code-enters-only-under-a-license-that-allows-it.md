# ADR 0004: Reused code enters only under a license that allows it, with its notice kept in a third-party file

Status: accepted, 2026-10-20

Origin: this ADR is maintained with the product base and mirrored into this repository on 2026-10-21. The repository copy is updated from that origin.

## Context

The base (ADR 0001) can start from open-source pieces instead of writing each one. Copyright exists from the moment code is written, so code with no license has all rights reserved, in the United States and in Brazil (Lei 9.610/98 and Lei 9.609/98, the Brazilian software law). Several projects in this space split their repository into an open part and a paid part, in folders named `enterprise` or `ee`, under a different license. The licenses below were read from each repository's license file. This record is a technical reading of licenses, and it does not replace a lawyer.

## Decision

1. Code enters the base by one of three legal routes. The first copies code under a permissive license (MIT, Apache 2.0, BSD or the PostgreSQL license), which allows use in a closed product, and keeps the copyright notice. The second respects copyleft: AGPL code would force this base to open its own code, because the base runs as a network service, and GPL code would do the same once the program is distributed. The third rewrites from scratch the idea, the flow, the data model and the screen, which is allowed even for closed products, because ideas and functions have no copyright (17 U.S.C. 102(b), and article 6 of Lei 9.609/98 accepts similarity that comes from function).
2. A clean-room rewrite runs in two steps. One session writes a specification reading only public documentation, and another session writes the code reading only that specification.
3. Code with no license stays out.
4. Nothing is taken from `enterprise` or `ee` folders, in any project.
5. Every reused file keeps its notice, and the notices are collected in one third-party file at the root of the repository, next to the `NOTICE` file of each Apache project that ships one. The file is created with the first reused code, and it stays for as long as that code does. The end users of a client never see it.
6. Five pieces enter as components. Chatwoot (MIT core) gives the inbox, the human handoff and the WhatsApp, SMS and web chat channels. pgvector (PostgreSQL license) holds retrieval. Langfuse (MIT outside `ee`) holds traces and evaluation. Pipecat (BSD 2-clause) gives voice when voice enters. The PDF and table reader of RAGFlow (Apache 2.0) is copied with its NOTICE.
7. These can also be copied with their notice: the integrations of the current Botpress repository (MIT, and never its v12, which is AGPL), Langflow (MIT), Flowise (Apache 2.0 outside its enterprise folder, archived on 2026-08-13), LiveKit Agents (Apache 2.0), promptfoo (MIT) and Ragas (Apache 2.0).
8. These stay out of the product. Dify uses a modified Apache license that forbids multi-tenant use without written permission and forbids removing its logo. n8n uses the Sustainable Use License, which allows only internal or non-commercial use. Typebot uses the Functional Source License since 2024-09-25, which forbids competing use. Open WebUI requires its brand on screen above 50 users in 30 days. Phoenix uses the Elastic License 2.0, which forbids offering it as a service. Evolution API and Baileys talk to WhatsApp through an unofficial protocol (ADR 0005).
9. Closed products in the same market are studied only from their public pages, documentation, videos and customer reviews, without opening an account. Their code, decompiled binaries, captured traffic, text and screens are never copied.
10. Reverse-engineering tools are used only to integrate with a client's own software, with written authorization from the owner of that software, and they are installed only from their official repository.

## Alternatives considered

Treating code with no license as free to use was rejected, because the law reads it the other way. Copying from `enterprise` folders was rejected, because those folders only run in production with a paid subscription. Building every piece from scratch was rejected, because the architecture review of 2026-10-18 estimated 170 to 290 hours for the whole set, and ready pieces are what bring that down.

## Consequences

Each new dependency gets its license read before it enters, and its row in the third-party file is part of the same change. Chatwoot keeps its AI agent (Captain) and its response-time targets in the `enterprise` folder, so the base writes its own bot layer. The free Chatwoot edition keeps the Chatwoot brand on screen, and removing it needs a paid plan. The LiteLLM SDK (MIT outside `enterprise`) follows ADR 0003.
