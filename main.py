import tkinter as tk
from tkinter import ttk, messagebox
from leaflink_api import fetch_orders, update_order_status
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from PIL import Image, ImageTk
import os
from datetime import datetime

# Constants
CORRECT_PIN = '1234'
ORDER_STATUSES = ["Submitted", "Accepted"]  # Adjusted to match API expected values

class OrderViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LeafLink Order Viewer by Grissom")
        
        self.window_width = int(self.root.winfo_screenwidth() * 0.9)
        self.window_height = int(self.root.winfo_screenheight() * 0.9)
        self.root.geometry(f'{self.window_width}x{self.window_height}')
        
        self.style = tb.Style(theme='flatly')  # Choose a theme

        self.create_widgets()

    def create_widgets(self):
        self.top_frame = ttk.Frame(self.root, padding=20)
        self.top_frame.pack(expand=False, fill=BOTH)
        
        self.main_frame = ttk.Frame(self.root, padding=20)
        self.main_frame.pack(expand=True, fill=BOTH)

        # Load and display the logo
        self.load_logo()
        
        self.pin_label = ttk.Label(self.top_frame, text="Enter PIN:", font=('Helvetica', 14, 'bold'))
        self.pin_label.grid(row=1, column=0, pady=10, padx=5)
        
        self.pin_entry = ttk.Entry(self.top_frame, font=('Helvetica', 14), show="*")
        self.pin_entry.grid(row=2, column=0, pady=5, padx=5)
        
        self.submit_button = ttk.Button(self.top_frame, text="Submit", command=self.validate_pin, bootstyle=SUCCESS)
        self.submit_button.grid(row=3, column=0, pady=10, padx=5)
        
        self.order_status_var = tk.StringVar(value=ORDER_STATUSES[0])
        self.order_status_dropdown = ttk.Combobox(self.top_frame, textvariable=self.order_status_var, values=ORDER_STATUSES)
        self.order_status_dropdown.grid(row=4, column=0, pady=10, padx=5)
        self.order_status_dropdown.bind("<<ComboboxSelected>>", self.refresh_orders)
        
        self.refresh_button = ttk.Button(self.top_frame, text="Refresh", command=self.refresh_orders, bootstyle=INFO)
        self.refresh_button.grid(row=5, column=0, pady=10, padx=5)
        self.refresh_button.grid_remove()
        
        self.top_frame.grid_columnconfigure(0, weight=1)

        self.create_main_frame(self.main_frame)

    def load_logo(self):
        try:
            # Ensure the path to the logo is correct
            image_path = "/robust_logo.jpg"
            if not os.path.exists(image_path):
                print(f"Logo image not found at path: {image_path}")
                return

            image = Image.open(image_path)
            image = image.resize((200, 100), Image.ANTIALIAS)  # Resize the image
            self.logo = ImageTk.PhotoImage(image)
            logo_label = ttk.Label(self.top_frame, image=self.logo)
            logo_label.grid(row=0, column=0, pady=10, padx=5)
            print("Logo loaded and displayed successfully.")
        except Exception as e:
            print(f"Error loading logo: {e}")

    def create_main_frame(self, parent):
        self.canvas = tk.Canvas(parent)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)

        self.scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side=RIGHT, fill=Y)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.main_frame_inner = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.main_frame_inner, anchor="nw")

        self.main_frame_inner.bind("<Configure>", self.on_frame_configure)

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def validate_pin(self):
        entered_pin = self.pin_entry.get()
        if entered_pin == CORRECT_PIN:
            self.pin_label.grid_remove()
            self.pin_entry.grid_remove()
            self.submit_button.grid_remove()
            self.refresh_button.grid()
            self.order_status_dropdown.grid()
            self.load_orders()
        else:
            messagebox.showerror("Error", "Invalid PIN")

    def load_orders(self):
        status = self.order_status_var.get()
        try:
            orders = fetch_orders(status)  # Pass the selected status to fetch_orders
            if orders:
                self.populate_treeview(orders)
            else:
                messagebox.showinfo("Information", f"No {status.lower()} orders to process.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load orders: {e}")

    def refresh_orders(self, event=None):
        self.load_orders()

    def format_date(self, date_str):
        if date_str:
            date_obj = datetime.fromisoformat(date_str)
            return date_obj.strftime('%m/%d/%Y')
        return "N/A"

    def populate_treeview(self, orders):
        for widget in self.main_frame_inner.winfo_children():
            widget.destroy()

        for order in orders:
            buyer_name = order.get("customer", {}).get("display_name", "Unknown Buyer")
            order_short_id = order.get("short_id", "N/A")
            ship_date = self.format_date(order.get("ship_date"))
            order_id = order.get("number")

            order_frame = ttk.Frame(self.main_frame_inner, padding="10")
            order_frame.pack(fill='x', expand=True, padx=10, pady=10, anchor="n")

            ttk.Label(order_frame, text=f"Buyer: {buyer_name} - Order Short ID: {order_short_id} - Ship Date: {ship_date}", font=('Helvetica', 16, 'bold')).pack(side="top", fill="x")

            columns = ('SKU', 'Ship Tag', 'Product Name', 'Base 0.5g', 'Base 1', 'Base 2.5', 'Base 3.5', 'Base 5', 'Base 7.0', 'Base 28.0', 'Base 448.0', 'Is Sample', 'Calculated Qty 1', 'Calculated Qty 2', 'Calculated Price')
            tree = self.create_treeview(order_frame, columns)
            self.populate_tree(tree, order)

            copy_button = ttk.Button(order_frame, text="Copy Order to Clipboard", command=lambda tr=tree: self.copy_to_clipboard(tr), bootstyle=PRIMARY)
            copy_button.pack(pady=10, side=tk.LEFT)

            update_button = ttk.Button(order_frame, text="Update Status to Accepted", command=lambda oid=order_id: self.confirm_update_status(oid), bootstyle=WARNING)
            update_button.pack(pady=10, side=tk.RIGHT)

    def create_treeview(self, parent, columns):
        tree = ttk.Treeview(parent, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", stretch=tk.YES, width=200 if col == 'Product Name' else 100)

        tree.tag_configure('sample', background='lightblue')

        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(expand=True, fill='both')

        return tree

    def populate_tree(self, tree, order):
        for item in order.get("line_items", []):
            product_info = item.get("frozen_data", {}).get("product", {})
            is_sample = "Yes" if item.get("is_sample", False) else "No"
            ordered_unit_price = item.get('ordered_unit_price', {}).get('amount', 0)
            quantity = float(item.get("quantity", 0))
            bulk_units = item.get("bulk_units", 0)
            price_per_unit = float(product_info.get("price", 0))
            calculated_price = bulk_units * price_per_unit

            base_units = float(product_info.get('base_units_per_unit', 0))
            base_columns, calculated_qtys = self.calculate_base_units(base_units, item)

            sku = product_info.get("sku", "N/A").lstrip('0') or "-"

            values = (
                sku,
                "",  # Ship Tag left empty
                product_info.get("name", "N/A") or "-",
                *base_columns,
                is_sample,
                *calculated_qtys,
                f"${calculated_price:.2f}"
            )

            tree.insert('', 'end', values=values, tags=('sample',) if item.get("is_sample", False) else ())

    def calculate_base_units(self, base_units, item):
        base_dict = {
            0.5: 'Base 0.5g',
            1.00: 'Base 1',
            2.5: 'Base 2.5',
            3.50: 'Base 3.5',
            5.00: 'Base 5',
            7.00: 'Base 7.0',
            28.00: 'Base 28.0',
            448.00: 'Base 448.0'
        }

        base_columns = {k: "" for k in base_dict.values()}
        calculated_qty_1 = calculated_qty_2 = ""

        quantity = float(item.get("quantity", "N/A")) if item.get("quantity", "N/A") != "N/A" else 0

        if base_units in base_dict:
            base_columns[base_dict[base_units]] = str(int(quantity))

        if base_units == 3.50:
            calculated_qty_1 = str(quantity * 3.6)
            calculated_qty_2 = str(quantity * 3.5)
        elif base_units == 7.00:
            calculated_qty_1 = str(quantity * 7.2)
            calculated_qty_2 = str(quantity * 7.0)

        base_columns_list = [base_columns[key] or "-" for key in base_dict.values()]
        calculated_qtys = [calculated_qty_1 or "-", calculated_qty_2 or "-"]

        return base_columns_list, calculated_qtys

    def copy_to_clipboard(self, tree):
        tree.selection_set(tree.get_children())
        selected_items = tree.selection()
        clipboard_data = '\n'.join('\t'.join(tree.item(item, 'values')) for item in selected_items)
        self.root.clipboard_clear()
        self.root.clipboard_append(clipboard_data)
        messagebox.showinfo("Success", "All order data copied to clipboard!")

    def confirm_update_status(self, order_id):
        print(f"Updating order with ID: {order_id}")
        if messagebox.askyesno("Confirmation", "Are you sure you want to update the order status to 'Accepted'?"):
            self.update_order_status(order_id)

    def update_order_status(self, order_id):
        try:
            success = update_order_status(order_id, "Accepted")
            if success:
                messagebox.showinfo("Success", "Order status updated to 'Accepted'.")
                self.refresh_orders()
            else:
                messagebox.showerror("Error", "Failed to update the order status.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update the order status: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = OrderViewerApp(root)
    root.mainloop()
