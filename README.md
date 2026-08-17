# RAG PII Guardrail

A retrieval-augmented chatbot that redacts personally identifiable information from retrieved context before any of it reaches the language model.

## What it does

- Retrieves the most relevant chunks from a small in-memory knowledge base using TF-IDF + cosine similarity, so the demo runs fully offline with no API key.
- Passes every retrieved chunk through a regex-based redaction layer before it is added to the prompt that would go to an LLM.
- Detects and masks five PII types: email addresses, phone numbers, credit card numbers, SSNs, and IBANs.
- Replaces each detected value with a typed placeholder (e.g. [EMAIL_REDACTED], [PHONE_REDACTED]) so the context stays readable but the sensitive value is gone.
- Prints the raw retrieved text, the list of PII the guardrail caught, and the sanitized text side by side, so the redaction step is easy to audit.

## Why the order matters

The guardrail sits between retrieval and generation, not after generation. Redaction happens on the retrieved context before it is ever sent to the language model call, so the model structurally cannot leak an email, phone number, credit card number, SSN, or IBAN it was never given. Swapping the offline TF-IDF retriever for a real OpenAI/Claude API call would not change this at all - the sanitized context is what gets sent either way.

## Tech stack

- Python
- scikit-learn (TfidfVectorizer, cosine_similarity) for retrieval
- Standard library re for PII pattern matching and redaction

## Quickstart

```bash
pip install scikit-learn
python rag_with_guardrail_clean.py
```

The script runs three example questions against a tiny built-in knowledge base. For each question it prints the raw retrieved context, which PII types (if any) the guardrail caught, and the sanitized context that would actually be sent to the LLM.

## Example output

```
QUESTION: How do I escalate an urgent issue?

GUARDRAIL caught and redacted:
  - EMAIL: sarah.lee@acme.com
  - PHONE: +1 415 555 0142

WHAT THE LLM ACTUALLY RECEIVES (safe):
  To escalate an issue, contact the account manager Sarah Lee at
  [EMAIL_REDACTED] or call [PHONE_REDACTED].
```

## Notes / honest caveats

- Retrieval is intentionally tiny (TF-IDF) - the point of this repo is the guardrail, not the retrieval. A real build would use proper embeddings and a vector store.
- Regex-based PII detection is a starting point, not a finished compliance solution. It is strong on structured data (cards, emails, IBANs) but weaker on free-text names, which would need a proper NER pass in production.
