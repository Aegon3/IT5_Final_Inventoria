"""
Inventory Management System - Controller with Logout / Login Loop
NO QMessageBox imports - All UI alerts delegated to view.
NO direct view imports - Only imports from model.
"""


class InventoryControllerWithLogout:
    """Controller that supports logout and login loop"""

    def __init__(self, model, view, db_config: dict):
        self.model = model
        self.view = view
        self.db_config = db_config
        self.model.add_observer(self)
        self._connec_signals()
        self.update()

    def _connect_signals(self):
        self.view.add_item_signal.connect(self.handle_add_item)
        self.view.edit_item_signal.connect(self.handle_edit_item)
        self.view.delete_item_signal.connect(self.handle_delete_item)
        self.view.adjust_stock_signal.connect(self.handle_adjust_stock)
        self.view.filter_changed_signal.connect(self.handle_filter_changed)
        self.view.refresh_low_stock_signal.connect(self.update_low_stock)
        self.view.logout_signal.connect(self.handle_logout)

    def update(self):
        self.update_inventory_table()
        self.update_low_stock()
        self.update_statistics()

    def update_inventory_table(self):
        search_text = self.view.get_search_text()
        category = self.view.get_category_filter()
        items = self.model.get_filtered_items(search_text, category)
        self.view.populate_inventory_table(items)

    def update_low_stock(self):
        items = self.model.get_low_stock_items()
        self.view.populate_low_stock_table(items)

    def update_statistics(self):
        stats = self.model.get_statistics()
        self.view.display_statistics(stats)

    def handle_add_item(self, item_data):
        if not item_data['name'].strip():
            self.view.show_message("Validation Error", "Item name cannot be empty!", "warning")
            return False
        success = self.model.add_item(
            item_data['name'], item_data['category'], item_data['quantity'],
            item_data['min_stock'], item_data['unit_price'], item_data['supplier']
        )
        if success:
            self.view.show_message("Success", "Item added successfully!", "information")
        else:
            self.view.show_message("Error", "Failed to add item to database!", "critical")
        return success

    def handle_edit_item(self, item_name, item_data):
        if not item_data['name'].strip():
            self.view.show_message("Validation Error", "Item name cannot be empty!", "warning")
            return False
        item_id = self.model.find_item_by_name(item_name)
        if item_id >= 0:
            success = self.model.update_item(
                item_id, item_data['name'], item_data['category'], item_data['quantity'],
                item_data['min_stock'], item_data['unit_price'], item_data['supplier']
            )
            if success:
                self.view.show_message("Success", "Item updated successfully!", "information")
            else:
                self.view.show_message("Error", "Failed to update item!", "critical")
            return success
        else:
            self.view.show_message("Error", "Item not found!", "warning")
            return False

    def handle_delete_item(self, item_name):
        reply = self.view.confirm_action("Confirm Delete",
                                         f"Are you sure you want to delete '{item_name}'?\n\nThis action cannot be undone!")
        if reply:
            item_id = self.model.find_item_by_name(item_name)
            if item_id >= 0:
                success = self.model.delete_item(item_id)
                if success:
                    self.view.show_message("Success", "Item deleted successfully!", "information")
                else:
                    self.view.show_message("Error", "Failed to delete item!", "critical")
                return success
            else:
                self.view.show_message("Error", "Item not found!", "warning")
                return False
        return False

    def handle_adjust_stock(self, item_name, adjustment):
        if adjustment == 0:
            self.view.show_message("Info", "No adjustment made (change is 0)", "information")
            return False
        item_id = self.model.find_item_by_name(item_name)
        if item_id >= 0:
            success = self.model.adjust_stock(item_id, adjustment)
            if success:
                action = "increased" if adjustment > 0 else "decreased"
                self.view.show_message("Success", f"Stock {action} by {abs(adjustment)} units!", "information")
            else:
                self.view.show_message("Error", "Failed to adjust stock!", "critical")
            return success
        else:
            self.view.show_message("Error", "Item not found!", "warning")
            return False

    def handle_filter_changed(self):
        self.update_inventory_table()

    def handle_logout(self):
        """Emit logout request to view - view handles the actual logout UI"""
        # Just emit the signal, let the main.py handle the actual logout flow
        # This way controller doesn't need to import view classes
        reply = self.view.confirm_action("Logout Confirmation", "Are you sure you want to logout?")
        if reply:
            self.cleanup()
            # Signal to main.py that logout was confirmed
            if hasattr(self.view, 'logout_confirmed'):
                self.view.logout_confirmed.emit()
            else:
                self.view.close()

    def cleanup(self):
        try:
            self.model.close()
        except Exception as e:
            print(f"Error during cleanup: {e}")