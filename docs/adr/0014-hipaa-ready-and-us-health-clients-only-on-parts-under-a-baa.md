# ADR 0006: The base is HIPAA-ready, and a US health client runs only on parts covered by a BAA

Status: accepted, 2026-10-20

Origin: this ADR is maintained with the product base and mirrored into this repository on 2026-10-21. The repository copy is updated from that origin.

## Context

On 2026-10-19 HIPAA readiness became a requirement of the base for US health clients. HIPAA, the US law on health data, requires a Business Associate Agreement (BAA) with every vendor that stores, receives or transmits protected health information for the client, and the operator of the base is one of those vendors. The research of 2026-10-17 read clause 4.2 of Meta's terms, which says "the WhatsApp Business Platform is not HIPAA compliant". It found that Twilio signs a BAA for SMS and voice, and it found no BAA from Chatwoot. Whether Meta signs a BAA at all still has to be confirmed. A model behind an API is one more vendor that sees the text, and a model on our own server is not (ADR 0008 of the clinic repository, ADR 0003). In Brazil, health data is a sensitive category under article 11 of the LGPD, and the same per-client configuration carries those rules (ADR 0005).

## Decision

1. HIPAA-ready is a technical requirement. The base can run a US health client in a way where every component that touches protected health information is either a vendor that signs a BAA or software we host on infrastructure whose provider signs one.
2. Each client's configuration has a health flag. When the flag is on, the base refuses at startup any channel, model or vendor that is missing from that client's BAA list, and that check has a test.
3. A US health client has no WhatsApp channel. Its SMS and voice go through a vendor that signs a BAA.
4. The model function (ADR 0003) routes a health client only to a model whose provider signed a BAA, or to a local model.
5. Logs, traces and the cost ledger never store the raw text of a message. ADR 0003 of the clinic repository already requires this for the development corpus, and it now holds for every client.
6. The inbox of a US health client is Chatwoot hosted by us on infrastructure covered by a BAA, with Langfuse on the same infrastructure. The hosted Chatwoot Cloud stays out for those clients.

## Alternatives considered

Adding HIPAA support only when the first health client appears was the reading of 2026-10-18, and it was replaced on 2026-10-19 when readiness entered the requirements. Moving US health clients to a third-party platform that signs a BAA, as the architecture review of 2026-10-18 suggested, stays as the fallback if no host for our own inbox signs one.

## Consequences

HIPAA-ready names a set of technical controls. Compliance itself depends on the signed agreements and on how each client operates, so the README never claims a certification. The BAA list of each client is configuration, and it has to be checked with each vendor before the client goes live. Two questions stay open: which hosting provider signs a BAA for the inbox we host, and whether Meta signs one.

## Amendment (2026-10-20)

On acceptance, the author chose the SMS vendor for US health clients, and the reading of 2026-10-19 answered one of the two open questions and found one more gap.

1. The author chose AWS End User Messaging (formerly Amazon Pinpoint) for the SMS of US health clients, under the AWS BAA. The AWS list of HIPAA eligible services, updated on 2026-10-15, includes it and leaves out its voice messages and its WhatsApp channel. Twilio signs a BAA only on its Security Edition or Enterprise Edition. Chatwoot has no native channel for AWS SMS, so that channel needs an adapter of its own under ADR 0005.
2. Meta does not sign a BAA. Clause 4.2 of its WhatsApp Business Platform terms, updated on 2026-09-23, says Meta is not a business associate and that the platform is not HIPAA compliant, so decision 3 holds as written.
3. The hosting question stays open in a narrower form. AWS (EC2 and RDS for PostgreSQL), Azure, DigitalOcean (Droplets, without its managed databases), Render (Scale or Enterprise plan), Fly.io, Railway (above a monthly spend) and Supabase (from its Team plan) sign a BAA, and none of them has been chosen yet.
4. The Security Rule asks for audit controls that record activity in systems holding protected health information (45 CFR 164.312(b)). The free Chatwoot edition keeps no audit log of who opened which conversation, and the audit log comes only with its paid Enterprise edition. So the base either writes its own audit log for health clients or runs that edition under its license, and copying the code of the paid edition stays out under ADR 0004.

Sources, read on 2026-10-19 unless noted: aws.amazon.com/compliance/hipaa-eligible-services-reference/ (read again on 2026-10-20), aws.amazon.com/compliance/hipaa-compliance/, www.twilio.com/docs/iam/twilio-editions/hippa, www.facebook.com/legal/Meta-Terms-for-WhatsApp-Business-Platform, learn.microsoft.com/en-us/azure/compliance/offerings/offering-hipaa-us, digitalocean.com/trust/hipaa-at-do, render.com/docs/hipaa-compliance, fly.io/pricing.md, docs.railway.com/maturity/compliance, supabase.com/pricing, www.ecfr.gov/current/title-45/section-164.312, www.chatwoot.com/pricing and www.chatwoot.com/industries/healthcare.
