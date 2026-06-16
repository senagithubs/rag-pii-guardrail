# RAG chatbot with a PII redaction guardrail

A small proof-of-concept I put together to show a pattern I keep running into with clients: they want a chatbot that can answer questions over their own documents, but they're (rightly) nervous about feeding customer data into an LLM.

The usual approach is "trust the model not to leak." I don't love that. This does it the other way around — anything sensitive is stripped out *before* the model ever sees it. The LLM can't leak what it never received.

## What it does

The flow is simple:

1. User asks a question
2. Retrieve the most relevant chunks from the knowledge base (TF-IDF here, so it runs offline with no API key)
3. **Run the retrieved text through a redaction step** — emails, phone numbers, credit cards, SSNs, IBANs get replaced with typed placeholders
4. Only the cleaned context goes to the LLM
5. You get an answer, minus the leaked PII

The redaction is plain regex, runs locally, and is deterministic — which also means it's easy to audit, unlike "we asked the model nicely."

## Running it

```bash
pip install scikit-learn
python rag_with_guardrail.py
```

You'll see three example questions. One has no PII (passes through untouched), the other two have an email + phone and a credit card buried in the source docs — watch them get caught.

Example output for the escalation question:

```
WHAT THE LLM ACTUALLY RECEIVES (safe):
  To escalate an issue, contact the account manager Sarah Lee at
  [EMAIL_REDACTED] or call [PHONE_REDACTED].
```

## Notes / honest caveats

- The retrieval is intentionally tiny (TF-IDF). In a real build I'd swap this for proper embeddings + a vector store, but the point of this repo is the **guardrail**, not the retrieval.
- Regex PII detection is a starting point, not a finished compliance solution. For production I usually layer in a proper NER pass for names/addresses and tune the patterns to the client's data. Regex is great for the structured stuff (cards, emails, IBANs); it's weaker on free-text names.
- Swapping TF-IDF for a real OpenAI/Claude call doesn't change the guardrail at all — the sanitized context is what gets sent either way.

## Why I built it

Most "AI chatbot" work treats data safety as an afterthought. I'd rather make leaks structurally impossible than promise they won't happen. If that's the kind of thing you need built properly, that's the work I do.
