import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGroupBox, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel, QLineEdit, QTreeView, QMessageBox
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon
from PyQt5.QtWidgets import QMessageBox

from leaflink_api import fetch_orders  # Ensure this module is adapted for PyQt or works generically

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('LeafLink Order Viewer by Grissom')
        self.setGeometry(100, 100, 1440, 810)  # 75% of 1920x1080 screen size

        # Main Widget and Layout
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.main_layout = QVBoxLayout()
        self.main_widget.setLayout(self.main_layout)

        # PIN Entry
        self.pin_layout = QHBoxLayout()
        self.pin_label = QLabel("Enter PIN:")
        self.pin_entry = QLineEdit()
        self.pin_entry.setEchoMode(QLineEdit.Password)  # Hide password
        self.pin_submit = QPushButton('Submit')
        self.pin_submit.clicked.connect(self.validate_pin)

        self.pin_layout.addWidget(self.pin_label)
        self.pin_layout.addWidget(self.pin_entry)
        self.pin_layout.addWidget(self.pin_submit)

        self.main_layout.addLayout(self.pin_layout)

    def validate_pin(self):
        CORRECT_PIN = '1234'
        entered_pin = self.pin_entry.text()
        if entered_pin == CORRECT_PIN:
            self.fetch_and_display_orders()
        else:
            QMessageBox.critical(self, "Error", "Invalid PIN")

    def fetch_and_display_orders(self):
        orders = fetch_orders()
        self.populate_treeview(orders)  # Pass the fetched orders to populate_treeview

    def populate_treeview(self, orders):
        self.clear_layout(self.main_layout)  # Clear layout before adding new items

        if not orders:
            QMessageBox.information(self, "No Orders", "No orders found or available for display.")
            return

        for order in orders:
            group_box = QGroupBox(f"Order ID: {order.get('id', 'N/A')} - Buyer: {order.get('customer', {}).get('display_name', 'Unknown')}")
            vbox = QVBoxLayout()

            tree = QTreeView()
            model = QStandardItemModel()
            columns = ['SKU', 'Ship Tag', 'Product Name', 'MIP Units', 'Base 3.50', 'Base 7.00', 'Base 28.00', 'Base 448.00', 'Is Sample']
            model.setHorizontalHeaderLabels(columns)
            tree.setModel(model)

            for item in order.get("line_items", []):
                product_info = item.get("frozen_data", {}).get("product", {})
                base_units_per_unit = int(float(product_info.get("base_units_per_unit", "1")))
                quantity = int(float(item.get("quantity", "0")))
                base_3_5 = int(quantity) if base_units_per_unit == 3.5 else "-"
                base_7 = int(quantity) if base_units_per_unit == 7 else "-"
                base_28 = int(quantity) if base_units_per_unit == 28 else "-"
                base_448 = int(quantity) if base_units_per_unit == 448 else "-"

                mip_units_display = str(quantity) if base_units_per_unit < 1 else "-"

                row_data = [
                    product_info.get("sku", "-"),
                    "",
                    product_info.get("name", "-"),
                    mip_units_display,
                    str(base_3_5),
                    str(base_7),
                    str(base_28),
                    str(base_448),
                    "Yes" if item.get("is_sample", False) else "No"
                ]
                items = [QStandardItem(field) for field in row_data]
                model.appendRow(items)

            tree.setModel(model)
            vbox.addWidget(tree)

            # Save Button
            save_button = QPushButton()
            save_button.setIcon(QIcon('/src/save.png'))  # Ensure you have an appropriate save icon
            save_button.clicked.connect(lambda _, b=order: self.copy_info_to_clipboard(b))
            vbox.addWidget(save_button)

            group_box.setLayout(vbox)
            self.main_layout.addWidget(group_box)

    def copy_info_to_clipboard(self, order):
        clipboard = QApplication.clipboard()

        # Start building the order details string
        order_details = ""

        # Loop through each line item to append their details
        for item in order.get("line_items", []):
            product_info = item.get("frozen_data", {}).get("product", {})
            base_units_per_unit = int(float(product_info.get("base_units_per_unit", "1")))
            quantity = int(float(item.get("quantity", "0")))
            base_3_5 = int(quantity) if base_units_per_unit == 3.5 else "-"
            base_7 = int(quantity) if base_units_per_unit == 7 else "-"
            base_28 = int(quantity) if base_units_per_unit == 28 else "-"
            base_448 = int(quantity) if base_units_per_unit == 448 else "-"

            mip_units_display = str(quantity) if base_units_per_unit < 1 else "-"

            # Append formatted line item details to the order details string
            order_details += f"{product_info.get('sku', '-')}\t\t{product_info.get('name', '-')}\t{mip_units_display}\t{base_3_5}\t{base_7}\t{base_28}\t{base_448}\t{'Yes' if item.get('is_sample', False) else 'No'}\n"  # Removed \t{int(quantity)}

        # Copy the order details string to the clipboard
        clipboard.setText(order_details)

        QMessageBox.information(self, "Copied", "Order details copied to clipboard!")

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())