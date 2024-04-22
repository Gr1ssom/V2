import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QTreeWidget, QTreeWidgetItem, QMessageBox, QScrollArea, QGroupBox)
from leaflink_api import fetch_orders

# Constants
CORRECT_PIN = '1234'

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 800, 600)  # Adjust window size
        self.setWindowTitle('LeafLink Order Viewer by Grissom')

        # PIN Entry
        self.pin_label = QLabel("Enter PIN:", self)
        self.pin_entry = QLineEdit(self)
        self.pin_entry.setEchoMode(QLineEdit.Password)

        # Submit Button
        self.submit_button = QPushButton('Submit', self)
        self.submit_button.clicked.connect(self.validate_pin)

        # Refresh Button
        self.refresh_button = QPushButton('Refresh', self)
        self.refresh_button.clicked.connect(self.refresh_orders)
        self.refresh_button.hide()  # Initially hide the refresh button

        # Orders Scroll Area
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)

        self.scroll_area.setWidget(self.scroll_widget)

        # Layout
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.pin_label)
        self.layout.addWidget(self.pin_entry)
        self.layout.addWidget(self.submit_button)
        self.layout.addWidget(self.refresh_button)
        self.layout.addWidget(self.scroll_area)

        self.setLayout(self.layout)

    def populate_treeview(self, orders):
        for i in reversed(range(self.scroll_layout.count())):
            self.scroll_layout.itemAt(i).widget().deleteLater()

        for order in orders:
            group_box = QGroupBox("Order Details")
            box_layout = QVBoxLayout()

            # Displaying buyer information as a label
            buyer_info = f"Buyer: {order.get('customer', {}).get('display_name', 'Unknown Buyer')} - ID: {order.get('customer', {}).get('id', 'N/A')}"
            buyer_label = QLabel(buyer_info)
            box_layout.addWidget(buyer_label)

            # Create a tree widget for this particular order
            tree = QTreeWidget()
            tree.setHeaderLabels(['SKU', 'Ship Tag', 'Product Name', 'Base 1', 'Base 2.5', 'Base 3.50',
                                  'Base 7.00', 'Base 28.00', 'Base 448.00', 'Is Sample'])
            tree.setColumnCount(10)

            for item in order.get("line_items", []):
                product_info = item.get("frozen_data", {}).get("product", {})
                is_sample = "Yes" if item.get("is_sample", False) else "No"
                values = [
                    product_info.get("sku", "N/A"),
                    "",  # Ship Tag left empty
                    product_info.get("name", "N/A"),
                    "-", "-", "-", "-", "-", "-", is_sample
                ]
                QTreeWidgetItem(tree, values)

            tree.expandAll()
            box_layout.addWidget(tree)

            copy_button = QPushButton('Copy to Clipboard')
            copy_button.clicked.connect(lambda _, tr=tree: self.copy_to_clipboard(tr))
            box_layout.addWidget(copy_button)

            group_box.setLayout(box_layout)
            self.scroll_layout.addWidget(group_box)

    def copy_to_clipboard(self, tree):
        clipboard_data = ""
        for item in tree.selectedItems():
            clipboard_data += '\t'.join(item.text(i) for i in range(10)) + '\n'
        QApplication.clipboard().setText(clipboard_data)
        QMessageBox.information(self, "Success", "Order data copied to clipboard!")

    def validate_pin(self):
        entered_pin = self.pin_entry.text()
        if entered_pin == CORRECT_PIN:
            orders = fetch_orders()
            if orders:
                self.populate_treeview(orders)
                self.refresh_button.show()
            else:
                QMessageBox.information(self, "Information", "No submitted orders to process.")
        else:
            QMessageBox.critical(self, "Error", "Invalid PIN")

    def refresh_orders(self):
        orders = fetch_orders()
        if orders:
            self.populate_treeview(orders)
        else:
            QMessageBox.information(self, "Information", "No new submitted orders to process.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
