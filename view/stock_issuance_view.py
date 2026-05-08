"""
Stock Issuance - View
UI tab and helper methods for the Stock Issuance feature.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QSpinBox, QTextEdit,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


def create_stock_issuance_tab(view_instance):
    tab = QWidget()
    layout = QVBoxLayout(tab)

    title = QLabel("Stock Issuance")
    title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
    title.setStyleSheet("padding: 10px; color: #2C3E50;")
    layout.addWidget(title)

    desc = QLabel("Record items taken out of the storeroom for department use. Stock will be automatically deducted.")
    desc.setStyleSheet("color: #666; padding: 0 10px 10px 10px;")
    desc.setWordWrap(True)
    layout.addWidget(desc)

    form_widget = QWidget()
    form_widget.setStyleSheet("""
        QWidget {
            background-color: #f9f9f9;
            border: 1px solid #ddd;
            border-radius: 6px;
            padding: 10px;
        }
    """)
    form_layout = QVBoxLayout(form_widget)

    item_row = QHBoxLayout()
    item_label = QLabel("Item:")
    item_label.setFixedWidth(120)
    view_instance.issuance_item_combo = QComboBox()
    view_instance.issuance_item_combo.addItem("Select Item", None)
    item_row.addWidget(item_label)
    item_row.addWidget(view_instance.issuance_item_combo)
    form_layout.addLayout(item_row)

    qty_row = QHBoxLayout()
    qty_label = QLabel("Quantity:")
    qty_label.setFixedWidth(120)
    view_instance.issuance_qty_spin = QSpinBox()
    view_instance.issuance_qty_spin.setRange(1, 10000)
    view_instance.issuance_qty_spin.setValue(1)
    qty_row.addWidget(qty_label)
    qty_row.addWidget(view_instance.issuance_qty_spin)
    qty_row.addStretch()
    form_layout.addLayout(qty_row)

    notes_row = QHBoxLayout()
    notes_label = QLabel("Notes:")
    notes_label.setFixedWidth(120)
    notes_label.setAlignment(Qt.AlignmentFlag.AlignTop)
    view_instance.issuance_notes_input = QTextEdit()
    view_instance.issuance_notes_input.setMaximumHeight(70)
    notes_row.addWidget(notes_label)
    notes_row.addWidget(view_instance.issuance_notes_input)
    form_layout.addLayout(notes_row)

    layout.addWidget(form_widget)

    submit_btn = QPushButton("Issue Stock")
    submit_btn.setObjectName("adjust_btn")
    submit_btn.setFixedHeight(36)
    submit_btn.clicked.connect(lambda: _on_submit(view_instance))
    layout.addWidget(submit_btn)

    table_label = QLabel("Issuance History")
    table_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
    table_label.setStyleSheet("padding: 10px 0 5px 0;")
    layout.addWidget(table_label)

    view_instance.issuance_table = QTableWidget()
    view_instance.issuance_table.setColumnCount(5)
    view_instance.issuance_table.setHorizontalHeaderLabels([
        "Date", "Item", "Quantity", "Issued By", "Notes"
    ])
    view_instance.issuance_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    view_instance.issuance_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    view_instance.issuance_table.setAlternatingRowColors(True)
    view_instance.issuance_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
    layout.addWidget(view_instance.issuance_table)

    return tab


def _on_submit(view_instance):
    item_id = view_instance.issuance_item_combo.currentData()
    item_name = view_instance.issuance_item_combo.currentText()
    quantity = view_instance.issuance_qty_spin.value()
    notes = view_instance.issuance_notes_input.toPlainText()

    if ' (Stock:' in item_name:
        item_name = item_name.split(' (Stock:')[0]

    view_instance.stock_issuance_signal.emit(item_id or 0, item_name, quantity, notes)


def load_issuance_item_combo(view_instance, items):
    if not hasattr(view_instance, 'issuance_item_combo'):
        return
    view_instance.issuance_item_combo.clear()
    view_instance.issuance_item_combo.addItem("Select Item", None)
    for item in items:
        view_instance.issuance_item_combo.addItem(
            f"{item.name} (Stock: {item.quantity})", item.id
        )


def populate_issuance_table(view_instance, issuances):
    if not hasattr(view_instance, 'issuance_table'):
        return
    view_instance.issuance_table.setRowCount(0)
    if not issuances:
        return
    for issuance in issuances:
        row = view_instance.issuance_table.rowCount()
        view_instance.issuance_table.insertRow(row)

        view_instance.issuance_table.setItem(row, 0, QTableWidgetItem(str(issuance.issued_date)))
        view_instance.issuance_table.setItem(row, 1, QTableWidgetItem(issuance.item_name))
        view_instance.issuance_table.setItem(row, 2, QTableWidgetItem(str(issuance.quantity)))
        view_instance.issuance_table.setItem(row, 3, QTableWidgetItem(issuance.issued_by))

        notes = issuance.notes or ''
        notes_item = QTableWidgetItem(notes[:50] + '...' if len(notes) > 50 else notes)
        notes_item.setToolTip(notes)
        view_instance.issuance_table.setItem(row, 4, notes_item)


def clear_issuance_form(view_instance):
    if hasattr(view_instance, 'issuance_item_combo'):
        view_instance.issuance_item_combo.setCurrentIndex(0)
    if hasattr(view_instance, 'issuance_qty_spin'):
        view_instance.issuance_qty_spin.setValue(1)
    if hasattr(view_instance, 'issuance_notes_input'):
        view_instance.issuance_notes_input.clear()