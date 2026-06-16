import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


PII_PATTERNS = {
    "EMAIL":       r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
    "PHONE":       r"\+?\d[\d\s().-]{7,}\d",
    "CREDIT_CARD": r"\b(?:\d[ -]*?){13,16}\b",
    "SSN":         r"\b\d{3}-\d{2}-\d{4}\b",
    "IBAN":        r"\b[A-Z]{2}\d{2}[A-Z0-9]{10,30}\b",
}


def redact_pii(text):
    found = []
    clean = text
    for label in ["EMAIL", "CREDIT_CARD", "IBAN", "SSN", "PHONE"]:
        pattern = PII_PATTERNS[label]
        for match in re.findall(pattern, clean):
            found.append((label, match))
        clean = re.sub(pattern, f"[{label}_REDACTED]", clean)
    return clean, found


class TinyRAG:
    def __init__(self, documents):
        self.docs = documents
        self.vec = TfidfVectorizer(stop_words="english")
        self.matrix = self.vec.fit_transform(documents)

    def retrieve(self, question, k=2):
        q = self.vec.transform([question])
        scores = cosine_similarity(q, self.matrix)[0]
        top = scores.argsort()[::-1][:k]
        return [self.docs[i] for i in top if scores[i] > 0]


def answer(rag, question):
    chunks = rag.retrieve(question)
    raw_context = "\n".join(chunks)
    safe_context, pii = redact_pii(raw_context)
    return raw_context, safe_context, pii


if __name__ == "__main__":
    knowledge_base = [
        "Refund policy: customers can request a refund within 30 days of purchase. "
        "Approved refunds are processed within 5 business days to the original card.",
        "To escalate an issue, contact the account manager Sarah Lee at sarah.lee@acme.com "
        "or call +1 415 555 0142. Her direct line is for priority clients only.",
        "Enterprise plan includes SSO, audit logs, and a dedicated success manager. "
        "Billing is annual; the saved card on file ending 4242 9988 1010 3344 is charged each January.",
        "Shipping: standard delivery takes 3-5 business days. Express delivery is next-day "
        "for orders placed before 2pm.",
    ]

    rag = TinyRAG(knowledge_base)

    questions = [
        "How do I get a refund?",
        "How do I escalate an urgent issue?",
        "How does enterprise billing work?",
    ]

    for q in questions:
        raw, safe, pii = answer(rag, q)
        print("=" * 72)
        print("QUESTION:", q)
        print("-" * 72)
        print("RETRIEVED CONTEXT (raw, contains PII):")
        print("  " + raw.replace("\n", "\n  "))
        if pii:
            print("\nGUARDRAIL caught and redacted:")
            for label, value in pii:
                print(f"  - {label}: {value}")
        else:
            print("\nGUARDRAIL: no PII in this context.")
        print("\nWHAT THE LLM ACTUALLY RECEIVES (safe):")
        print("  " + safe.replace("\n", "\n  "))
        print()

    print("=" * 72)
    print("Takeaway: the LLM answers the question, but emails, phone numbers and")
    print("card numbers are stripped before it ever sees them. The model cannot")
    print("leak data it was never given — privacy by architecture, not by trust.")
