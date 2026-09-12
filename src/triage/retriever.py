import math
import re
from typing import Literal
from pydantic import BaseModel
from .corpus import Document
from .allowlist import Allowlist


STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
    "has", "he", "in", "is", "it", "its", "of", "on", "or", "that",
    "the", "to", "was", "will", "with"
}


class RetrievalHit(BaseModel):
    source_id: str
    source_type: Literal["paper", "patent", "trial_registry", "internal_report"]
    title: str
    status: Literal["active", "stale", "retracted"]
    raw_score: float
    score: float


class BM25Index:
    def __init__(self, doc_ids: list[str], tokenized_docs: list[list[str]], k1: float = 1.5, b: float = 0.75):
        self.doc_ids = doc_ids
        self.tokenized_docs = tokenized_docs
        self.k1 = k1
        self.b = b
        self.n_docs = len(doc_ids)
        self.avg_doc_len = sum(len(doc) for doc in tokenized_docs) / self.n_docs if self.n_docs > 0 else 0
        self.idf = self._compute_idf()
        self.excluded_count = 0
        self.excluded_ids = []

    def _compute_idf(self) -> dict[str, float]:
        doc_freq = {}
        for tokens in self.tokenized_docs:
            for token in set(tokens):
                doc_freq[token] = doc_freq.get(token, 0) + 1
        idf = {}
        for token, freq in doc_freq.items():
            idf[token] = math.log((self.n_docs - freq + 0.5) / (freq + 0.5) + 1.0)
        return idf

    def score(self, query_tokens: list[str]) -> dict[str, float]:
        scores = {doc_id: 0.0 for doc_id in self.doc_ids}
        for token in query_tokens:
            if token not in self.idf:
                continue
            idf_score = self.idf[token]
            for i, doc_tokens in enumerate(self.tokenized_docs):
                term_freq = doc_tokens.count(token)
                if term_freq == 0:
                    continue
                doc_len = len(doc_tokens)
                numerator = idf_score * term_freq * (self.k1 + 1)
                denominator = term_freq + self.k1 * (1 - self.b + self.b * (doc_len / self.avg_doc_len))
                scores[self.doc_ids[i]] += numerator / denominator
        return scores


def _tokenize(text: str) -> list[str]:
    text = text.lower()
    tokens = re.findall(r'\w+', text)
    return [t for t in tokens if t not in STOPWORDS and len(t) > 1]


def build_index(documents: list[Document], allowlist: Allowlist) -> BM25Index:
    doc_ids = []
    tokenized_docs = []
    excluded_ids = []

    for doc in documents:
        if not allowlist.is_allowed(doc.source_id):
            excluded_ids.append(doc.source_id)
            continue
        doc_ids.append(doc.source_id)
        tokens = _tokenize(f"{doc.title} {doc.body}")
        tokenized_docs.append(tokens)

    index = BM25Index(doc_ids, tokenized_docs)
    index.excluded_count = len(excluded_ids)
    index.excluded_ids = excluded_ids
    return index


def query(index: BM25Index, documents_by_id: dict[str, Document], text: str,
          top_k: int = 6, min_score: float = 0.15) -> list[RetrievalHit]:
    query_tokens = _tokenize(text)
    if not query_tokens:
        return []

    raw_scores = index.score(query_tokens)
    max_score = max(raw_scores.values()) if raw_scores else 1.0

    hits = []
    for doc_id in index.doc_ids:
        raw_score = raw_scores[doc_id]
        normalized_score = raw_score / max_score if max_score > 0 else 0.0

        if normalized_score < min_score:
            continue

        doc = documents_by_id[doc_id]
        hits.append(RetrievalHit(
            source_id=doc_id,
            source_type=doc.source_type,
            title=doc.title,
            status=doc.status,
            raw_score=raw_score,
            score=normalized_score
        ))

    hits.sort(key=lambda h: h.score, reverse=True)
    return hits[:top_k]
