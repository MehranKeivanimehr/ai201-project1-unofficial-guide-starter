"""
Milestone 4: Embedding & Vector Store
Embeds chunks with all-MiniLM-L6-v2, stores in ChromaDB, and tests retrieval.
"""

import os
import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

from sentence_transformers import SentenceTransformer
import chromadb


def load_chunks(path="chunks.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_collection(client, name="uf_professors"):
    # Use cosine similarity for standard semantic search scoring
    return client.get_or_create_collection(
        name=name,
        metadata={"hnsw:space": "cosine"}
    )


def build_collection(chunks, model, collection):
    """Embed all chunks and add them to ChromaDB."""
    texts = [c["text"] for c in chunks]
    ids = [f"{c['filename'].replace(' ', '_')}_{c['chunk_index']}" for c in chunks]
    metadatas = [{"source": c["filename"], "chunk_index": c["chunk_index"]} for c in chunks]

    print(f"Embedding {len(texts)} chunks with {model}...")
    embeddings = model.encode(texts, batch_size=32, show_progress_bar=True).tolist()

    print(f"Adding to ChromaDB collection '{collection.name}'...")
    collection.add(
        ids=ids,
        embeddings=embeddings,
        metadatas=metadatas,
        documents=texts
    )
    print(f"✅ {len(texts)} chunks embedded and stored.")


def retrieve(query, model, collection, top_k=5):
    """Retrieve top-k chunks for a query."""
    query_embedding = model.encode([query]).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )

    retrieved = []
    for i in range(top_k):
        retrieved.append({
            "text": results["documents"][0][i],
            "source": results["metadatas"][0][i]["source"],
            "chunk_index": results["metadatas"][0][i]["chunk_index"],
            "distance": results["distances"][0][i]
        })
    return retrieved


def test_retrieval(model, collection):
    """Test retrieval with 3 evaluation queries."""
    test_queries = [
        "What do students say about Peter Dobbins's teaching style?",
        "What do Reddit users say about Christina Boucher?",
        "What do students say about Tamer Kahveci's lectures?"
    ]

    print("\n" + "=" * 70)
    print("RETRIEVAL TESTS")
    print("=" * 70)

    for query in test_queries:
        print(f"\n🔍 QUERY: {query}")
        print("-" * 70)
        results = retrieve(query, model, collection, top_k=5)

        for i, r in enumerate(results, 1):
            text_preview = r["text"][:200].replace("\n", " ")
            print(f"  {i}. [{r['distance']:.4f}] {r['source']} (chunk {r['chunk_index']})")
            print(f"     → {text_preview}...")


def main():
    chunks = load_chunks("chunks.json")
    print(f"Loaded {len(chunks)} chunks from chunks.json")

    # Initialize embedding model
    model_name = "all-MiniLM-L6-v2"
    print(f"Loading embedding model: {model_name}...")
    model = SentenceTransformer(model_name)

    # Initialize ChromaDB (persistent)
    db_path = "./chroma_db"
    client = chromadb.PersistentClient(path=db_path)
    collection = get_collection(client)

    # Check if collection already has data
    existing_count = collection.count()
    if existing_count == 0:
        build_collection(chunks, model, collection)
    else:
        print(f"Collection already has {existing_count} items. Skipping build.")
        print(f"To rebuild, delete the '{db_path}' folder and re-run.")

    # Run retrieval tests
    test_retrieval(model, collection)

    print("\n✅ Milestone 4 complete. Retrieval is working.")


if __name__ == "__main__":
    main()
