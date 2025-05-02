import requests
from sentence_transformers import SentenceTransformer, util
import torch

print("👉 Încarc modelul SentenceTransformer... (așteaptă câteva secunde, prima dată durează)")
model = SentenceTransformer('all-MiniLM-L6-v2')
print("✅ Model încărcat cu succes!\n")

def search_semantic_scholar(query, limit=10):
    print(f"🔍 Caut în Semantic Scholar pentru: '{query}'...")
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": query,
        "limit": limit,
        "fields": "title,abstract,paperId"
    }
    response = requests.get(url, params=params)
    data = response.json()
    print("✅ Rezultatele au fost primite de la API.\n")
    return data.get('data', [])

def semantic_search(user_query, papers):
    print("✨ Încep analiza semantică...")
    query_embedding = model.encode(user_query, convert_to_tensor=True)

    docs = []
    embeddings = []
    for paper in papers:
        title = paper.get('title') or "Titlu indisponibil"
        abstract = paper.get('abstract') or "Abstract indisponibil"
        paper_id = paper.get('paperId')
        url = f"https://www.semanticscholar.org/paper/{paper_id}" if paper_id else "Link indisponibil"

        text = abstract if abstract != "Abstract indisponibil" else title
        docs.append((title, abstract, url))
        embeddings.append(model.encode(text, convert_to_tensor=True))

    embedding_tensor = torch.stack(embeddings)
    results = util.cos_sim(query_embedding, embedding_tensor)[0]

    scored_docs = sorted(zip(docs, results), key=lambda x: x[1], reverse=True)

    print("✅ Similaritatea semantică a fost calculată.\n")
    return scored_docs

def main():
    user_query = input("📝 Introdu subiectul dorit: ")

    print("\n🚀 Începem căutarea...\n")
    papers = search_semantic_scholar(user_query)

    if not papers:
        print("⚠️ Nu s-au găsit articole.")
        return

    results = semantic_search(user_query, papers)

    print(f"\n📚 Top rezultate pentru: '{user_query}'\n")
    for i, ((title, abstract, url), score) in enumerate(results[:5]):  # Top 5
        print(f"{i+1}. {title}")
        print(f"    Scor similaritate: {score:.4f}")
        print(f"    Link: {url}")
        print(f"    Abstract: {abstract[:300]}...\n")  # Primele 300 caractere

if __name__ == "__main__":
    main()
