# 🚀 Academic Search GUI Ultimate
# PyQt6 + Animations + Export + Theme Toggle + Autocomplete + Shadow + History + Clear History

import sys
import os
import torch
import csv
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton,
    QLabel, QScrollArea, QFrame, QTextEdit, QMessageBox, QHBoxLayout,
    QCompleter, QFileDialog, QGraphicsDropShadowEffect, QProgressDialog, QDialog
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer
from PyQt6.QtGui import QFont, QCursor, QColor
from main import search_all_sources, semantic_search

HISTORY_FILE = "history.txt"

class ScholarApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cautatorul academic 3000")
        self.setGeometry(300, 100, 1000, 700)
        self.setStyleSheet("background-color: #121212; color: #e0e0e0;")
        self.dark_mode = True

        self.layout = QVBoxLayout(self)
        self.history = self.load_history()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Introdu subiectul")
        self.search_input.setFont(QFont("Segoe UI", 14))
        self.search_input.setStyleSheet("background-color: #1e1e1e; padding: 10px; border: 1px solid #333; border-radius: 8px; color: white;")
        self.completer = QCompleter(self.history)
        self.search_input.setCompleter(self.completer)
        self.layout.addWidget(self.search_input)

        btn_row = QHBoxLayout()

        self.search_button = QPushButton("Cauta")
        self.search_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.search_button.clicked.connect(self.perform_search)

        self.export_button = QPushButton("Export")
        self.export_button.clicked.connect(self.export_results)

        self.theme_button = QPushButton("Schimba tema")
        self.theme_button.clicked.connect(self.toggle_theme)

        self.history_button = QPushButton("istoric")
        self.history_button.clicked.connect(self.show_history)

        self.clear_history_button = QPushButton("Curata istoric")
        self.clear_history_button.clicked.connect(self.clear_history)

        for btn in [self.search_button, self.export_button, self.theme_button, self.history_button, self.clear_history_button]:
            btn.setStyleSheet("QPushButton { background-color: #03DAC6; padding: 10px; border-radius: 6px; color: black; font-weight: bold; } QPushButton:hover { background-color: #00b8a9; }")
            btn_row.addWidget(btn)

        self.layout.addLayout(btn_row)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.results_container = QVBoxLayout()
        scroll_content = QWidget()
        scroll_content.setLayout(self.results_container)
        self.scroll_area.setWidget(scroll_content)
        self.layout.addWidget(self.scroll_area)

        self.results = []

    def show_toast(self, message):
        toast = QLabel(message, self)
        toast.setStyleSheet("background-color: #333; color: white; padding: 10px; border-radius: 5px;")
        toast.move(30, self.height() - 80)
        toast.show()
        QTimer.singleShot(3000, toast.hide)

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.setStyleSheet("background-color: #121212; color: #e0e0e0;")
            self.search_input.setStyleSheet("background-color: #1e1e1e; padding: 10px; border: 1px solid #333; border-radius: 8px; color: white;")
        else:
            self.setStyleSheet("background-color: white; color: black;")
            self.search_input.setStyleSheet("background-color: #f5f5f5; padding: 10px; border: 1px solid #ccc; border-radius: 8px; color: black;")
        self.show_toast("Theme changed")

    def load_history(self):
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip()]
        return []

    def save_to_history(self, query):
        if query not in self.history:
            self.history.insert(0, query)
            self.history = self.history[:20]
            with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
                f.write("\n".join(self.history))
            self.completer.setModel(self.completer.model())

    def show_history(self):
        if not self.history:
            QMessageBox.information(self, "History", "No previous searches found.")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Search History")
        dialog.setStyleSheet("background-color: #1e1e1e; color: white;")
        layout = QVBoxLayout(dialog)

        for query in self.history:
            btn = QPushButton(query)
            btn.setStyleSheet("background-color: #2a2a2a; color: white; margin: 4px; padding: 6px;")
            btn.clicked.connect(lambda checked, q=query: self.set_query_and_search(q, dialog))
            layout.addWidget(btn)

        dialog.setLayout(layout)
        dialog.exec()

    def clear_history(self):
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)
        self.history = []
        self.completer.setModel(self.completer.model())
        self.show_toast("History cleared")

    def set_query_and_search(self, query, dialog):
        dialog.accept()
        self.search_input.setText(query)
        self.perform_search()

    def perform_search(self):
        query = self.search_input.text().strip()
        if not query:
            return

        self.save_to_history(query)

        for i in reversed(range(self.results_container.count())):
            item = self.results_container.itemAt(i).widget()
            if item:
                item.setParent(None)

        loading = QProgressDialog("Searching...", None, 0, 0, self)
        loading.setWindowModality(Qt.WindowModality.ApplicationModal)
        loading.setCancelButton(None)
        loading.setStyleSheet("background-color: #222; color: white; padding: 10px;")
        loading.show()

        QTimer.singleShot(300, lambda: self.fetch_and_display(query, loading))

    def fetch_and_display(self, query, loading):
        papers = search_all_sources(query)
        loading.close()

        if not papers:
            self.show_toast("No results found")
            return

        self.results = semantic_search(query, papers)
        for (title, abstract, url), score in self.results[:8]:
            self.add_result_card(title, abstract, url, score)

    def add_result_card(self, title, abstract, url, score):
        card = QFrame()
        card.setStyleSheet("background-color: #1e1e1e; border-radius: 10px; padding: 15px;")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(2)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 150))
        card.setGraphicsEffect(shadow)

        layout = QVBoxLayout(card)

        title_lbl = QLabel(title)
        title_lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        title_lbl.setStyleSheet("color: #ffffff;")

        abstract_box = QTextEdit()
        abstract_box.setReadOnly(True)
        abstract_box.setText(abstract[:500] + ("..." if len(abstract) > 500 else ""))
        abstract_box.setStyleSheet("background-color: #2a2a2a; border: none; color: #dddddd; padding: 5px;")

        link_lbl = QLabel(f"<a href='{url}'>Open Article</a>")
        link_lbl.setOpenExternalLinks(True)
        link_lbl.setStyleSheet("color: #03DAC6; margin-top: 5px;")

        score_lbl = QLabel(f"Semantic Score: {score:.4f}")
        score_lbl.setStyleSheet("color: #aaaaaa; font-size: 10pt;")

        for w in [title_lbl, score_lbl, abstract_box, link_lbl]:
            layout.addWidget(w)

        self.results_container.addWidget(card)

        anim = QPropertyAnimation(card, b"windowOpacity")
        anim.setDuration(500)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        anim.start()
        card.anim = anim

    def export_results(self):
        if not self.results:
            self.show_toast("No results to export")
            return

        path, _ = QFileDialog.getSaveFileName(self, "Export as CSV", "results.csv", "CSV files (*.csv)")
        if not path:
            return

        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Title", "Abstract", "Link", "Score"])
            for (title, abstract, url), score in self.results:
                writer.writerow([title, abstract, url, f"{score:.4f}"])

        self.show_toast("Exported successfully")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = ScholarApp()
    win.show()
    sys.exit(app.exec())