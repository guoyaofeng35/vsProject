import math
import re
from dataclasses import dataclass
from pathlib import Path

from minimax_client import MiniMaxClient


DOCS_DIR = Path(__file__).resolve().parent / "rag_docs"


@dataclass
class Chunk:
    source: str
    index: int
    text: str
    score: float = 0.0


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z0-9_]+|[\u4e00-\u9fff]", text.lower())


def split_text(text: str, max_chars: int = 450) -> list[str]:
    paragraphs = [item.strip() for item in re.split(r"\n\s*\n", text) if item.strip()]
    chunks = []
    current = ""

    for paragraph in paragraphs:
        if not current:
            current = paragraph
        elif len(current) + len(paragraph) + 2 <= max_chars:
            current = f"{current}\n\n{paragraph}"
        else:
            chunks.append(current)
            current = paragraph

    if current:
        chunks.append(current)

    return chunks


def load_documents(docs_dir: Path) -> list[Chunk]:
    chunks = []
    for path in sorted(docs_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        for index, part in enumerate(split_text(text), 1):
            chunks.append(Chunk(source=path.name, index=index, text=part))
    return chunks


def search(question: str, chunks: list[Chunk], top_k: int = 3) -> list[Chunk]:
    query_terms = tokenize(question)
    if not query_terms:
        return []

    doc_freq = {}
    chunk_terms = []
    for chunk in chunks:
        terms = tokenize(chunk.text)
        chunk_terms.append(terms)
        for term in set(terms):
            doc_freq[term] = doc_freq.get(term, 0) + 1

    total_docs = len(chunks)
    scored = []
    for chunk, terms in zip(chunks, chunk_terms):
        term_counts = {}
        for term in terms:
            term_counts[term] = term_counts.get(term, 0) + 1

        score = 0.0
        for term in query_terms:
            if term not in term_counts:
                continue
            tf = term_counts[term] / max(len(terms), 1)
            idf = math.log((total_docs + 1) / (doc_freq.get(term, 0) + 1)) + 1
            score += tf * idf

        if score > 0:
            scored.append(Chunk(chunk.source, chunk.index, chunk.text, score))

    return sorted(scored, key=lambda item: item.score, reverse=True)[:top_k]


def build_prompt(question: str, hits: list[Chunk]) -> list[dict]:
    context = "\n\n".join(f"[{hit.source}#{hit.index}]\n{hit.text}" for hit in hits)
    system = (
        "You are a RAG assistant. Answer in Chinese. "
        "Use only the provided context. If the context is insufficient, say so. "
        "Cite sources like [file#chunk]."
    )
    user = f"Context:\n{context}\n\nQuestion:\n{question}"
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def local_answer(question: str, hits: list[Chunk]) -> str:
    if not hits:
        return "没有检索到相关资料。请换个问法，或把资料放到 rag_demo/rag_docs 目录。"

    lines = [
        "本地 RAG 模式：已检索到相关资料，但没有调用大模型生成。",
        f"问题：{question}",
        "",
        "最相关片段：",
    ]
    for hit in hits:
        preview = hit.text.replace("\n", " ")
        lines.append(f"- [{hit.source}#{hit.index}] score={hit.score:.4f} {preview}")
    return "\n".join(lines)


def answer_question(question: str) -> str:
    chunks = load_documents(DOCS_DIR)
    hits = search(question, chunks)
    client = MiniMaxClient()

    if not client.enabled:
        return local_answer(question, hits)

    if not hits:
        return "没有检索到相关资料，因此不调用模型。"

    try:
        return client.chat(build_prompt(question, hits), temperature=0.1)
    except Exception as exc:
        return f"MiniMax 调用失败，改用本地检索结果。\n\n错误：{exc}\n\n{local_answer(question, hits)}"


def main():
    print("RAG demo started.")
    print("Documents directory: rag_demo/rag_docs")
    print("Ask a question, or type exit.")

    while True:
        try:
            question = input("\n你: ").strip()
        except EOFError:
            print("\nRAG: 输入结束，已退出。")
            break

        if question.lower() in {"exit", "quit"} or question == "退出":
            print("RAG: 下次继续。")
            break

        print(f"\nRAG:\n{answer_question(question)}")


if __name__ == "__main__":
    main()
