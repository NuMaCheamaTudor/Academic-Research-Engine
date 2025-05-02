import sys
import torch
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton,
    QLabel, QScrollArea, QFrame, QTextEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QDesktopServices, QCursor
from PyQt6.QtCore import QUrl

# Importa functionalitatea NLP si API din main.py
from main import search_all_sources, semantic_search

class ScholarApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Academic Search")
        self.setGeometry(300, 100, 1000, 700)
        self.setStyleSheet("background-color: #121212; color: #e0e0e0;")

        self.layout = QVBoxLayout(self)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Introdu un subiect academic...")
        self.search_input.setFont(QFont("Segoe UI", 14))
        self.search_input.setStyleSheet("background-color: #1e1e1e; padding: 10px; border: 1px solid #333; border-radius: 8px; color: white;")
        self.layout.addWidget(self.search_input)

        self.search_button = QPushButton("Cauta")
        self.search_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.search_button.setStyleSheet("background-color: #03DAC6; padding: 10px; border: none; border-radius: 6px; color: black; font-weight: bold;")
        self.search_button.clicked.connect(self.perform_search)
        self.layout.addWidget(self.search_button)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.results_container = QVBoxLayout()

        scroll_content = QWidget()
        scroll_content.setLayout(self.results_container)
        self.scroll_area.setWidget(scroll_content)
        self.layout.addWidget(self.scroll_area)

    def perform_search(self):
        query = self.search_input.text().strip()
        if not query:
            return

        for i in reversed(range(self.results_container.count())):
            item = self.results_container.itemAt(i).widget()
            if item:
                item.setParent(None)

        papers = search_all_sources(query)
        if not papers:
            self.add_result_card("Nimic gasit", "Nu s-au gasit articole relevante.", "")
            return

        results = semantic_search(query, papers)
        for (title, abstract, url), score in results[:8]:
            self.add_result_card(title, abstract, url, score)

    def add_result_card(self, title, abstract, url, score=None):
        card = QFrame()
        card.setStyleSheet("background-color: #1e1e1e; border-radius: 10px; padding: 15px;")
        card_layout = QVBoxLayout(card)

        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #ffffff;")

        score_label = QLabel(f"Scor semantic: {score:.4f}" if score is not None else "")
        score_label.setStyleSheet("color: #aaaaaa; font-size: 10pt;")

        abstract_box = QTextEdit()
        abstract_box.setReadOnly(True)
        abstract_box.setText(abstract[:500] + ("..." if len(abstract) > 500 else ""))
        abstract_box.setStyleSheet("background-color: #2a2a2a; border: none; color: #dddddd; padding: 5px;")

        link_label = QLabel(f"<a href='{url}'>Deschide in Semantic Scholar / OpenAlex</a>")
        link_label.setOpenExternalLinks(True)
        link_label.setStyleSheet("color: #03DAC6; margin-top: 5px;")

        card_layout.addWidget(title_label)
        card_layout.addWidget(score_label)
        card_layout.addWidget(abstract_box)
        card_layout.addWidget(link_label)

        self.results_container.addWidget(card)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = ScholarApp()
    win.show()
    sys.exit(app.exec())