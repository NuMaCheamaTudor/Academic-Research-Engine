import requests
from sentence_transformers import SentenceTransformer, util
import torch

print("Incarc modelul SentenceTransformer... (asteapta cateva secunde, prima data dureaza)")
model = SentenceTransformer('all-MiniLM-L6-v2')
print("Model incarcat cu succes!\n")

def search_semantic_scholar(query, limit=10):
    print(f"Caut in Semantic Scholar pentru: '{query}'...")
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": query,
        "limit": limit,
        "fields": "title,abstract,paperId"
    }
    response = requests.get(url, params=params)
    data = response.json()
    print("Rezultatele au fost primite de la Semantic Scholar.\n")
    results = []
    for paper in data.get('data', []):
        title = paper.get('title') or "Titlu indisponibil"
        abstract = paper.get('abstract') or "Abstract indisponibil"
        paper_id = paper.get('paperId')
        url = f"https://www.semanticscholar.org/paper/{paper_id}" if paper_id else "Link indisponibil"
        results.append((title, abstract, url))
    return results

def search_openalex(query, limit=10):
    print(f"Caut in OpenAlex pentru: '{query}'...")
    url = "https://api.openalex.org/works"
    params = {
        "search": query,
        "per-page": limit
    }
    response = requests.get(url, params=params)
    data = response.json()
    print("Rezultatele au fost primite de la OpenAlex.\n")
    results = []
    for item in data.get("results", []):
        title = item.get("title", "Titlu indisponibil")
        abstract_data = item.get("abstract_inverted_index")
        if abstract_data:
            words = sorted(abstract_data.items(), key=lambda x: x[1][0])
            abstract_text = " ".join([w[0] for w in words])
        else:
            abstract_text = "Abstract indisponibil"
        url = item.get("id", "Link indisponibil")
        results.append((title, abstract_text, url))
    return results

def search_all_sources(query):
    results = []
    try:
        results += search_semantic_scholar(query)
    except Exception as e:
        print("Eroare la Semantic Scholar:", e)
    try:
        results += search_openalex(query)
    except Exception as e:
        print("Eroare la OpenAlex:", e)
    return results

def semantic_search(user_query, papers):
    print("Incep analiza semantica...")
    query_embedding = model.encode(user_query, convert_to_tensor=True)

    docs = []
    embeddings = []
    for title, abstract, url in papers:
        text = abstract if abstract != "Abstract indisponibil" else title
        docs.append((title, abstract, url))
        embeddings.append(model.encode(text, convert_to_tensor=True))

    embedding_tensor = torch.stack(embeddings)
    results = util.cos_sim(query_embedding, embedding_tensor)[0]
    scored_docs = sorted(zip(docs, results), key=lambda x: x[1], reverse=True)

    print("Similaritatea semantica a fost calculata.\n")
    return scored_docs

def main():
    user_query = input("Introdu subiectul dorit: ")

    print("\nIncepem cautarea in toate sursele...\n")
    papers = search_all_sources(user_query)

    if not papers:
        print("Nu s-au gasit articole.")
        return

    results = semantic_search(user_query, papers)

    print(f"\nTop rezultate pentru: '{user_query}'\n")
    for i, ((title, abstract, url), score) in enumerate(results[:5]):  # Top 5
        print(f"{i+1}. {title}")
        print(f"    Scor similaritate: {score:.4f}")
        print(f"    Link: {url}")
        print(f"    Abstract: {abstract[:300]}...\n")  # Primele 300 caractere

if __name__ == "__main__":
    main()