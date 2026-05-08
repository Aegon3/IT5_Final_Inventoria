"""
Supplier Management System - Views
Dialog boxes for supplier and order management
"""

from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QComboBox, QSpinBox,
    QDoubleSpinBox, QPushButton, QHBoxLayout, QVBoxLayout,
    QLabel, QTextEdit, QDateEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QWidget
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QColor
from datetime import datetime


class SupplierDialog(QDialog):
    def __init__(self, parent=None, supplier_data=None):
        super().__init__(parent)
        self.supplier_data = supplier_data
        self.setWindowTitle("Add Supplier" if not supplier_data else "Edit Supplier")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        title_label = QLabel(" Supplier Information")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        form = QFormLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter supplier name")

        self.contact_input = QLineEdit()
        self.contact_input.setPlaceholderText("Enter contact person name")

        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Enter phone number")

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter email address")

        self.address_input = QTextEdit()
        self.address_input.setMaximumHeight(100)
        self.address_input.setPlaceholderText("Enter full address")

        self.status_combo = QComboBox()
        self.status_combo.addItems(["active", "inactive"])

        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(80)
        self.notes_input.setPlaceholderText("Enter any notes about this supplier...")

        if self.supplier_data:
            self.name_input.setText(self.supplier_data.get('name', ''))
            self.contact_input.setText(self.supplier_data.get('contact_person', ''))
            self.phone_input.setText(self.supplier_data.get('phone', ''))
            self.email_input.setText(self.supplier_data.get('email', ''))
            self.address_input.setText(self.supplier_data.get('address', ''))
            self.status_combo.setCurrentText(self.supplier_data.get('status', 'active'))
            self.notes_input.setText(self.supplier_data.get('notes', ''))

        form.addRow("Supplier Name*:", self.name_input)
        form.addRow("Contact Person:", self.contact_input)
        form.addRow("Phone:", self.phone_input)
        form.addRow("Email:", self.email_input)
        form.addRow("Address:", self.address_input)
        form.addRow("Status:", self.status_combo)
        form.addRow("Notes:", self.notes_input)

        layout.addLayout(form)

        required_label = QLabel("* Required field")
        required_label.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(required_label)

        button_layout = QHBoxLayout()
        save_btn = QPushButton(" Save")
        cancel_btn = QPushButton("Cancel")
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def get_data(self):
        return {
            'name': self.name_input.text().strip(),
            'contact_person': self.contact_input.text().strip(),
            'phone': self.phone_input.text().strip(),
            'email': self.email_input.text().strip(),
            'address': self.address_input.toPlainText().strip(),
            'status': self.status_combo.currentText(),
            'notes': self.notes_input.toPlainText().strip()
        }


class StockRequestDialog(QDialog):
    def __init__(self, parent=None, item_name="", current_qty=0):
        super().__init__(parent)
        self.item_name = item_name
        self.current_qty = current_qty
        self.setWindowTitle("Request Stock")
        self.setModal(True)
        self.setMinimumWidth(400)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        title_label = QLabel(" Stock Request")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        item_label = QLabel(f"<b>Item:</b> {self.item_name}")
        item_label.setStyleSheet("font-size: 13px; padding: 5px; background-color: #f0f0f0; border-radius: 5px;")
        layout.addWidget(item_label)

        current_label = QLabel(f"<b>Current Stock:</b> {self.current_qty}")
        current_label.setStyleSheet("font-size: 12px; padding: 5px; color: #0066cc;")
        layout.addWidget(current_label)

        form = QFormLayout()

        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(1, 10000)
        self.quantity_spin.setValue(10)

        self.reason_input = QTextEdit()
        self.reason_input.setMaximumHeight(80)
        self.reason_input.setPlaceholderText("Why do you need this stock? (optional)")

        form.addRow("Request Quantity*:", self.quantity_spin)
        form.addRow("Reason:", self.reason_input)

        layout.addLayout(form)

        required_label = QLabel("* Required field")
        required_label.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(required_label)

        button_layout = QHBoxLayout()
        submit_btn = QPushButton(" Submit Request")
        cancel_btn = QPushButton("Cancel")
        submit_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(submit_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def get_quantity(self):
        return self.quantity_spin.value()

    def get_reason(self):
        return self.reason_input.toPlainText().strip()


class OrderDialog(QDialog):
    def __init__(self, parent=None, supplier_id=None, supplier_name="", db_config=None, order_controller=None):
        super().__init__(parent)
        self.supplier_id = supplier_id
        self.supplier_name = supplier_name
        self.order_controller = order_controller
        self.items = []
        self.order_suppliers = {}
        self.auto_detect_mode = supplier_id is None

        if self.auto_detect_mode:
            self.setWindowTitle(" Place Order ")
        else:
            self.setWindowTitle(f" Place Order - {supplier_name}")

        self.setModal(True)
        self.setMinimumWidth(750)
        self.setup_ui()
        if self.order_controller:
            self.load_inventory_items()

    def setup_ui(self):
        layout = QVBoxLayout()

        if self.auto_detect_mode:
            title_label = QLabel(" Place New Order ")
        else:
            title_label = QLabel(f" Place Order with {self.supplier_name}")

        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        if not self.auto_detect_mode:
            supplier_label = QLabel(f"<b>Supplier ID:</b> {self.supplier_id}")
            supplier_label.setStyleSheet("padding: 5px; background-color: #f0f0f0; border-radius: 5px;")
            layout.addWidget(supplier_label)
        else:
            info_label = QLabel(" <b>Supplier will be auto-detected based on items you select</b>")
            info_label.setStyleSheet("padding: 10px; background-color: #E8F6F3; border-radius: 5px; color: #2C3E50;")
            layout.addWidget(info_label)

        form = QFormLayout()

        self.order_number_input = QLineEdit()
        self.order_number_input.setText(f"ORD-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
        self.order_number_input.setReadOnly(True)

        self.order_date_input = QDateEdit()
        self.order_date_input.setDate(QDate.currentDate())
        self.order_date_input.setCalendarPopup(True)

        self.expected_date_input = QDateEdit()
        self.expected_date_input.setDate(QDate.currentDate().addDays(7))
        self.expected_date_input.setReadOnly(True)
        self.expected_date_input.setCalendarPopup(False)

        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(80)
        self.notes_input.setPlaceholderText("Enter order notes...")

        form.addRow("Order Number:", self.order_number_input)
        form.addRow("Order Date:", self.order_date_input)
        form.addRow("Expected Delivery:", self.expected_date_input)
        form.addRow("Notes:", self.notes_input)

        layout.addLayout(form)

        items_label = QLabel("Order Items:")
        items_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        layout.addWidget(items_label)

        if self.auto_detect_mode:
            self.items_table = QTableWidget()
            self.items_table.setColumnCount(7)
            self.items_table.setHorizontalHeaderLabels(["Item ID", "Item Name", "Category", "Current Stock", "Quantity", "Unit Price", "Supplier"])
            self.items_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.items_table.setColumnWidth(4, 100)
            self.items_table.setColumnWidth(5, 150)
            self.items_table.setMaximumHeight(200)
            self.items_table.setColumnHidden(0, True)
        else:
            self.items_table = QTableWidget()
            self.items_table.setColumnCount(6)
            self.items_table.setHorizontalHeaderLabels(["Item ID", "Item Name", "Category", "Current Stock", "Quantity", "Unit Price"])
            self.items_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.items_table.setColumnWidth(4, 100)
            self.items_table.setColumnWidth(5, 150)
            self.items_table.setMaximumHeight(200)
            self.items_table.setColumnHidden(0, True)

        layout.addWidget(self.items_table)

        add_layout = QHBoxLayout()

        self.item_combo = QComboBox()
        self.item_combo.addItem("Select Item", None)
        self.item_combo.currentIndexChanged.connect(self._on_item_selected)

        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(1, 10000)
        self.quantity_spin.setValue(1)

        self.unit_price_spin = QDoubleSpinBox()
        self.unit_price_spin.setRange(0.00, 10000)
        self.unit_price_spin.setValue(0.00)
        self.unit_price_spin.setPrefix("₱ ")
        self.unit_price_spin.setDecimals(2)

        add_btn = QPushButton(" Add Item")
        add_btn.clicked.connect(self._on_add_item_clicked)

        add_layout.addWidget(QLabel("Item:"))
        add_layout.addWidget(self.item_combo)
        add_layout.addWidget(QLabel("Qty:"))
        add_layout.addWidget(self.quantity_spin)
        add_layout.addWidget(QLabel("Price:"))
        add_layout.addWidget(self.unit_price_spin)
        add_layout.addWidget(add_btn)
        layout.addLayout(add_layout)

        button_layout = QHBoxLayout()
        place_order_btn = QPushButton(" Place Order")
        cancel_btn = QPushButton("Cancel")
        place_order_btn.clicked.connect(self._on_place_order_clicked)
        cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(place_order_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def load_inventory_items(self):
        success, items, error = self.order_controller.get_inventory_items()
        if not success:
            QMessageBox.critical(self, "Database Error", error)
            self.item_combo.addItem("Error Loading Items", None)
            return
        self.items = items

        self.item_combo.clear()
        self.item_combo.addItem("Select Item", None)

        if not self.items:
            self.item_combo.addItem("No items found in inventory", None)
            QMessageBox.information(self, "Info", "No items found in inventory!")
        else:
            for item in self.items:
                display_text = f"{item['name']} ({item['category']}) - Stock: {item['quantity']}"
                self.item_combo.addItem(display_text, item['id'])

    def _on_item_selected(self, index):
        item_id = self.item_combo.currentData()
        if not item_id:
            self.unit_price_spin.setValue(0.00)
            return

        for item in self.items:
            if item['id'] == item_id:
                unit_price = float(item.get('unit_price', 0.00))
                self.unit_price_spin.setValue(unit_price)
                break

    def _on_add_item_clicked(self):
        item_id = self.item_combo.currentData()

        if not item_id:
            QMessageBox.warning(self, "Warning", "Please select an item!")
            return

        if item_id is None and self.item_combo.currentText() in ["No items found in inventory", "Database Error - Check Connection", "Error Loading Items"]:
            QMessageBox.warning(self, "Warning", "Cannot add item - please fix the issue first!")
            return

        selected_item = None
        for item in self.items:
            if item['id'] == item_id:
                selected_item = item
                break

        if not selected_item:
            QMessageBox.warning(self, "Warning", "Selected item not found!")
            return

        for row in range(self.items_table.rowCount()):
            table_item_id = int(self.items_table.item(row, 0).text())
            if table_item_id == item_id:
                QMessageBox.warning(self, "Warning", "Item is already in the order!")
                return

        supplier_name = "No Supplier"
        supplier_id = None

        if self.auto_detect_mode:
            supplier_name_from_item = selected_item.get('supplier', '').strip()
            if supplier_name_from_item:
                supplier_id, found_name = self.order_controller.find_or_create_supplier(supplier_name_from_item)
                supplier_name = found_name if found_name else "No Supplier"

        self.order_suppliers[item_id] = {
            'name': supplier_name,
            'id': supplier_id
        }

        row = self.items_table.rowCount()
        self.items_table.insertRow(row)
        self.items_table.setRowHeight(row, 36)

        id_item = QTableWidgetItem(str(selected_item['id']))
        id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.items_table.setItem(row, 0, id_item)

        name_item = QTableWidgetItem(selected_item['name'])
        name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.items_table.setItem(row, 1, name_item)

        category_item = QTableWidgetItem(selected_item['category'])
        category_item.setFlags(category_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.items_table.setItem(row, 2, category_item)

        stock_item = QTableWidgetItem(str(selected_item['quantity']))
        stock_item.setFlags(stock_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.items_table.setItem(row, 3, stock_item)

        qty_spin = QSpinBox()
        qty_spin.setRange(1, 10000)
        qty_spin.setValue(self.quantity_spin.value())
        qty_spin.setMinimumWidth(90)
        self.items_table.setCellWidget(row, 4, qty_spin)

        price_spin = QDoubleSpinBox()
        price_spin.setRange(0.00, 10000)
        price_spin.setValue(self.unit_price_spin.value())
        price_spin.setPrefix("₱ ")
        price_spin.setDecimals(2)
        price_spin.setMinimumWidth(140)
        self.items_table.setCellWidget(row, 5, price_spin)

        if self.auto_detect_mode:
            supplier_item = QTableWidgetItem(supplier_name)
            supplier_item.setFlags(supplier_item.flags() & ~Qt.ItemFlag.ItemIsEditable)

            if supplier_name == "No Supplier":
                supplier_item.setForeground(QColor('#E74C3C'))
            elif supplier_id:
                supplier_item.setForeground(QColor('#27AE60'))
            else:
                supplier_item.setForeground(QColor('#F39C12'))

            self.items_table.setItem(row, 6, supplier_item)

        self.item_combo.setCurrentIndex(0)
        self.quantity_spin.setValue(1)
        self.unit_price_spin.setValue(0.00)

    def _on_place_order_clicked(self):
        order_data = self.get_data()
        if order_data is None:
            return
        self.accept()

    def get_data(self):
        items = []
        row_count = self.items_table.rowCount()

        for row in range(row_count):
            try:
                id_item = self.items_table.item(row, 0)
                if not id_item:
                    continue

                item_id = int(id_item.text())
                name_item = self.items_table.item(row, 1)
                if not name_item:
                    continue

                item_name = name_item.text()
                qty_widget = self.items_table.cellWidget(row, 4)
                if not qty_widget:
                    continue

                quantity = qty_widget.value() if hasattr(qty_widget, 'value') else 1
                price_widget = self.items_table.cellWidget(row, 5)
                if not price_widget:
                    continue

                unit_price = price_widget.value() if hasattr(price_widget, 'value') else 0.0

                items.append({
                    'id': item_id,
                    'name': item_name,
                    'quantity': quantity,
                    'unit_price': unit_price
                })

            except Exception as e:
                continue

        if len(items) == 0:
            QMessageBox.warning(self, "No Items",
                               "Please add at least one item to the order.\n\n"
                               "To add items:\n"
                               "1. Select an item from the dropdown\n"
                               "2. Set the quantity\n"
                               "3. Set the price\n"
                               "4. Click the ' Add Item' button")
            return None

        order_data = {
            'supplier_id': self.supplier_id,
            'supplier_name': self.supplier_name,
            'order_number': self.order_number_input.text(),
            'order_date': self.order_date_input.date().toString('yyyy-MM-dd'),
            'expected_delivery': self.expected_date_input.date().toString('yyyy-MM-dd'),
            'notes': self.notes_input.toPlainText().strip(),
            'items': items
        }

        if self.auto_detect_mode and self.supplier_id is None:
            valid = [info for info in self.order_suppliers.values() if info['id'] is not None]
            if valid:
                order_data['supplier_name'] = valid[0]['name']
                order_data['supplier_id'] = valid[0]['id']

        return order_data


class OrdersDialog(QDialog):
    def __init__(self, parent=None, db_config=None, user_role="staff", order_controller=None):
        super().__init__(parent)
        self.user_role = user_role
        self.order_controller = order_controller
        self.setWindowTitle(" View Orders")
        self.setModal(True)
        self.showMaximized()
        self.setup_ui()
        if self.order_controller:
            self.load_orders()

    def setup_ui(self):
        layout = QVBoxLayout()

        title_label = QLabel(" ORDER MANAGEMENT")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("padding: 10px; color: #2C3E50;")
        layout.addWidget(title_label)

        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Status Filter:"))

        self.status_filter = QComboBox()
        self.status_filter.addItems(["All", "ordered", "delivered", "cancelled"])
        self.status_filter.currentTextChanged.connect(self.load_orders)
        filter_layout.addWidget(self.status_filter)

        filter_layout.addStretch()

        refresh_btn = QPushButton(" Refresh")
        refresh_btn.clicked.connect(self.load_orders)
        filter_layout.addWidget(refresh_btn)

        layout.addLayout(filter_layout)

        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(8)
        self.orders_table.setHorizontalHeaderLabels([
            "Order #", "Supplier", "Order Date", "Expected Delivery",
            "Status", "Total Amount", "Items Count", "Actions"
        ])
        self.orders_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.orders_table.setAlternatingRowColors(True)
        self.orders_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.orders_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.orders_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        layout.addWidget(self.orders_table)

        self.details_widget = QWidget()
        self.details_widget.setVisible(False)
        details_layout = QVBoxLayout(self.details_widget)

        details_title = QLabel(" Order Details")
        details_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        details_layout.addWidget(details_title)

        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(300)
        self.details_text.setStyleSheet("""
            QTextEdit {
                padding: 15px;
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                font-size: 12px;
            }
        """)
        details_layout.addWidget(self.details_text)

        close_details_btn = QPushButton("Close Details")
        close_details_btn.clicked.connect(lambda: self.details_widget.setVisible(False))
        details_layout.addWidget(close_details_btn)

        layout.addWidget(self.details_widget)

        button_layout = QHBoxLayout()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def load_orders(self):
        try:
            filter_status = self.status_filter.currentText()
            success, orders, error = self.order_controller.get_orders(filter_status)
            if not success:
                QMessageBox.critical(self, "Database Error", error)
                return

            self.orders_table.setRowCount(0)

            for order in orders:
                row = self.orders_table.rowCount()
                self.orders_table.insertRow(row)

                from controller.supplier_controller import SupplierController
                status_color = SupplierController.get_status_color(order['status'])

                self.orders_table.setItem(row, 0, QTableWidgetItem(order['order_number']))
                self.orders_table.setItem(row, 1, QTableWidgetItem(order.get('supplier_name', 'Unknown')))

                order_date = order['order_date'].strftime('%Y-%m-%d') if order['order_date'] else 'N/A'
                expected_date = order['expected_delivery'].strftime('%Y-%m-%d') if order['expected_delivery'] else 'N/A'

                self.orders_table.setItem(row, 2, QTableWidgetItem(order_date))
                self.orders_table.setItem(row, 3, QTableWidgetItem(expected_date))

                status_combo = QComboBox()
                status_combo.addItems(['ordered', 'delivered', 'cancelled'])
                status_combo.setCurrentText(order['status'])
                status_combo.setStyleSheet(f"color: {status_color}; font-weight: bold;")

                if self.user_role == "admin":
                    status_combo.currentTextChanged.connect(
                        lambda new_status, oid=order['id'], row_idx=row: self.update_order_status(oid, new_status, row_idx)
                    )
                else:
                    status_combo.setEnabled(False)

                self.orders_table.setCellWidget(row, 4, status_combo)

                total_amount = order['total_amount'] or 0.0
                self.orders_table.setItem(row, 5, QTableWidgetItem(f"₱{total_amount:.2f}"))

                items_count = order['items_count'] or 0
                self.orders_table.setItem(row, 6, QTableWidgetItem(str(items_count)))

                self.orders_table.setRowHeight(row, 38)
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(4, 4, 4, 4)
                actions_layout.setSpacing(4)

                view_btn = QPushButton("View")
                view_btn.setFixedSize(68, 28)
                view_btn.clicked.connect(lambda checked, o=order: self.view_order_details(o))
                actions_layout.addWidget(view_btn)

                if self.user_role == "admin":
                    delete_btn = QPushButton("Delete")
                    delete_btn.setFixedSize(68, 28)
                    delete_btn.setStyleSheet("background-color: #E74C3C; color: white; border-radius:4px;")
                    delete_btn.clicked.connect(lambda checked, o=order: self.delete_order(o))
                    actions_layout.addWidget(delete_btn)

                actions_layout.addStretch()
                self.orders_table.setCellWidget(row, 7, actions_widget)

        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to load orders: {str(e)}")

    def update_order_status(self, order_id, new_status, row_idx):
        try:
            success, message = self.order_controller.update_order_status(order_id, new_status)
            if not success:
                QMessageBox.critical(self, "Error", message)
                return

            from controller.supplier_controller import SupplierController
            status_color = SupplierController.get_status_color(new_status)

            combo = self.orders_table.cellWidget(row_idx, 4)
            if combo:
                combo.setStyleSheet(f"color: {status_color}; font-weight: bold;")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update order status: {str(e)}")

    def delete_order(self, order):
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete order {order['order_number']}?\n\nThis action cannot be undone!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            success, message = self.order_controller.delete_order(order['id'], order['order_number'])
            if success:
                QMessageBox.information(self, "Success", message)
                self.load_orders()
            else:
                QMessageBox.critical(self, "Error", message)

    def view_order_details(self, order):
        success, items, supplier, error = self.order_controller.get_order_details(order['id'], order['supplier_id'])
        if not success:
            QMessageBox.critical(self, "Error", error)
            return

        from controller.supplier_controller import SupplierController
        details_html = SupplierController.build_order_details_html(order, items, supplier)
        self.details_text.setHtml(details_html)
        self.details_widget.setVisible(True)