# 🧠 Academic Search Engine (PyQt6 + NLP)

A modern academic research tool built with Python and PyQt6 that leverages **semantic similarity** and **multiple scholarly APIs** to return the most relevant research articles based on your query.

---

## 🔍 What it does

- Accepts a user query (e.g., `neural networks`, `hamming distance`, `AI in education`)
- Searches multiple academic sources:
  - ✅ [Semantic Scholar API](https://api.semanticscholar.org/)
  - ✅ [OpenAlex API](https://docs.openalex.org/)
- Calculates **semantic similarity** scores using [Sentence Transformers](https://www.sbert.net/)
- Displays the **title**, **abstract**, **semantic score**, and **clickable link** for each paper
- All within a sleek, **dark-mode GUI** built with PyQt6

---

## 🧠 Technologies Used

- **Python 3.10+**
- [PyQt6](https://pypi.org/project/PyQt6/) — graphical interface
- [sentence-transformers](https://pypi.org/project/sentence-transformers/) — semantic embeddings
- [Torch](https://pytorch.org/) — tensor support for NLP
- [Requests](https://pypi.org/project/requests/) — for HTTP requests to APIs

---

## 📦 Installation

```bash
git clone https://github.com/YOUR_USERNAME/academic-search-gui.git
cd academic-search-gui
pip install -r requirements.txt
python gui.py
