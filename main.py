import requests
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('all-MiniLM-L6-v2')

def search_semantic_scholar(query, limit=10):
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": query,
        "limit": limit,
        "fields": "title,abstract,url"
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data.get('data', [])

def semantic_search(user_query, papers):
    query_embedding = model.encode(user_query, convert_to_tensor=True)

    docs = []
    embeddings = []
    for paper in papers:
        text = paper.get('abstract') or paper.get('title')
        if text:
            docs.append((paper.get('title'), text, paper.get('url')))
            embeddings.append(model.encode(text, convert_to_tensor=True))

    results = util.cos_sim(query_embedding, embeddings).tolist()[0]

    scored_docs = sorted(zip(docs, results), key=lambda x: x[1], reverse=True)

    return scored_docs

def main():
    user_query = input("Introdu subiectul dorit: ")

    print("\nCautam articole relevante...\n")
    papers = search_semantic_scholar(user_query)

    if not papers:
        print("Nu s-au găsit articole.")
        return

    results = semantic_search(user_query, papers)

    print(f"Top rezultate pentru: '{user_query}'\n")
    for i, ((title, abstract, url), score) in enumerate(results[:5]):  # Top 5
        print(f"{i+1}. {title}")
        print(f"    Scor similaritate: {score:.4f}")
        print(f"    Link: {url}")
        print(f"    Abstract: {abstract[:300]}...")  # Primele 300 caractere
        print()

if __name__ == "__main__":
    main()