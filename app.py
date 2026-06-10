"""
Milestone 5: Grounded Generation & Interface
End-to-end RAG: retrieve chunks -> generate grounded answer -> Gradio UI.
"""

import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
from groq import Groq
from sentence_transformers import SentenceTransformer
import chromadb
import gradio as gr

# Load API key
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in .env")

# ---------------------------------------------------------------------------
# Retrieval setup (reused from retrieval.py)
# ---------------------------------------------------------------------------
MODEL_NAME = "all-MiniLM-L6-v2"
DB_PATH = "./chroma_db"
COLLECTION_NAME = "uf_professors"
TOP_K = 5

print(f"Loading embedding model: {MODEL_NAME}...")
_embed_model = SentenceTransformer(MODEL_NAME)

_chroma_client = chromadb.PersistentClient(path=DB_PATH)
_collection = _chroma_client.get_or_create_collection(
    name=COLLECTION_NAME,
    metadata={"hnsw:space": "cosine"}
)
print(f"Collection '{COLLECTION_NAME}' has {_collection.count()} chunks.")


def retrieve_context(query: str, top_k: int = TOP_K):
    """Retrieve top-k chunks for a query."""
    query_embedding = _embed_model.encode([query]).tolist()
    results = _collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )

    chunks = []
    for i in range(top_k):
        chunks.append({
            "text": results["documents"][0][i],
            "source": results["metadatas"][0][i]["source"],
            "chunk_index": results["metadatas"][0][i]["chunk_index"],
            "distance": results["distances"][0][i]
        })
    return chunks


# ---------------------------------------------------------------------------
# Generation setup
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are The Unofficial Guide, a helpful assistant that answers questions about University of Florida professors STRICTLY using only the provided document excerpts.

GROUNDING RULES — follow these exactly:
1. Use ONLY the information in the provided excerpts to answer.
2. You MUST NOT use any outside knowledge, training data, or assumptions.
3. If the excerpts do not contain enough information to answer the question, say exactly: "I don't have enough information in the provided documents to answer that."
4. Do NOT guess, speculate, or hallucinate.
5. Cite the source file name for each claim you make, like (source: filename.txt).
6. Keep answers concise and directly supported by the excerpts.
"""

_groq_client = Groq(api_key=GROQ_API_KEY)


def generate_answer(query: str, chunks: list) -> str:
    """Call Groq LLM with strict grounding prompt and retrieved context."""
    # Format context
    context_lines = []
    for i, chunk in enumerate(chunks, 1):
        context_lines.append(
            f"[Excerpt {i} from {chunk['source']} (chunk {chunk['chunk_index']})]\n{chunk['text']}"
        )
    context = "\n\n".join(context_lines)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"Use ONLY the following excerpts to answer the question.\n\n{context}\n\nQuestion: {query}\n\nAnswer:"
        }
    ]

    response = _groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.3,
        max_tokens=512
    )

    return response.choices[0].message.content.strip()


# ---------------------------------------------------------------------------
# End-to-end
# ---------------------------------------------------------------------------
def ask(question: str) -> dict:
    """Full pipeline: retrieve -> generate -> return answer + sources."""
    chunks = retrieve_context(question)
    answer = generate_answer(question, chunks)
    sources = [c["source"] for c in chunks]
    return {"answer": answer, "sources": sources}


# ---------------------------------------------------------------------------
# Gradio interface
# ---------------------------------------------------------------------------
def handle_query(question: str):
    if not question or not question.strip():
        return "Please enter a question.", ""
    result = ask(question)
    sources_text = "\n".join(f"• {s}" for s in result["sources"])
    return result["answer"], sources_text


with gr.Blocks(title="The Unofficial Guide — UF CS Professors") as demo:
    gr.Markdown("# 🐊 The Unofficial Guide")
    gr.Markdown("Ask about UF Computer Science professors. Answers are grounded in student reviews from Rate My Professors and Reddit.")

    with gr.Row():
        inp = gr.Textbox(
            label="Your question",
            placeholder="e.g., What do students say about Peter Dobbins's teaching style?",
            lines=2
        )

    btn = gr.Button("Ask", variant="primary")

    with gr.Row():
        answer_out = gr.Textbox(label="Answer", lines=10)
        sources_out = gr.Textbox(label="Retrieved from", lines=10)

    btn.click(handle_query, inputs=inp, outputs=[answer_out, sources_out])
    inp.submit(handle_query, inputs=inp, outputs=[answer_out, sources_out])

    gr.Markdown("---")
    gr.Markdown("**Tip:** Try asking about teaching style, exam difficulty, or grading fairness. If the documents don't cover it, the system will say so.")


# ---------------------------------------------------------------------------
# CLI test mode
# ---------------------------------------------------------------------------
def test_queries():
    """Run end-to-end tests on evaluation queries + one out-of-domain query."""
    test_cases = [
        "What do students say about Peter Dobbins's teaching style?",
        "What do Reddit users say about Christina Boucher?",
        "What do students say about Tamer Kahveci's lectures?",
        "What is the best pizza place in Gainesville?"
    ]

    print("\n" + "=" * 70)
    print("END-TO-END GROUNDED GENERATION TESTS")
    print("=" * 70)

    for q in test_cases:
        print(f"\n🔍 QUESTION: {q}")
        print("-" * 70)
        result = ask(q)
        print(f"📝 ANSWER:\n{result['answer']}")
        print(f"\n📄 SOURCES: {', '.join(result['sources'])}")
        print()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true", help="Run CLI tests instead of launching UI")
    args = parser.parse_args()

    if args.test:
        test_queries()
    else:
        print("Launching Gradio interface at http://localhost:7860 ...")
        demo.launch()
