import tkinter as tk
from tkinter import ttk, messagebox
from leaflink_api import fetch_orders, update_order_status
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from PIL import Image, ImageTk
import os
from datetime import datetime

# Fetch CORRECT_PIN from environment variable
CORRECT_PIN = os.getenv('APP_PIN', '1234')

ORDER_STATUSES = ["Submitted", "Accepted"]

class OrderViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LeafLink Order Viewer by Grissom")
        
        self.window_width = int(self.root.winfo_screenwidth() * 0.9)
        self.window_height = int(self.root.winfo_screenheight() * 0.9)
        self.root.geometry(f'{self.window_width}x{self.window_height}')
        
        self.style = tb.Style(theme='flatly')

        self.create_widgets()

    def create_widgets(self):
        self.top_frame = ttk.Frame(self.root, padding=20)
        self.top_frame.pack(expand=False, fill=BOTH)
        
        self.main_frame = ttk.Frame(self.root, padding=20)
        self.main_frame.pack(expand=True, fill=BOTH)

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
        """Dynamically load and display the logo."""
        image_path = os.path.join(os.getcwd(), "robust_logo.jpg")
        if not os.path.exists(image_path):
            print(f"Logo image not found at path: {image_path}")
            return
        try:
            image = Image.open(image_path)
            image = image.resize((200, 100), Image.Resampling.LANCZOS)
            self.logo = ImageTk.PhotoImage(image)
            logo_label = ttk.Label(self.top_frame, image=self.logo)
            logo_label.grid(row=0, column=0, pady=10, padx=5)
        except Exception as e:
            print(f"Error loading logo: {e}")

    def create_main_frame(self, parent):
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(expand=True, fill=BOTH)

        self.orders_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.orders_tab, text="Orders")

        self.create_orders_tab(self.orders_tab)

    def create_orders_tab(self, parent):
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
        """Load orders from the API and handle UI updates."""
        status = self.order_status_var.get()
        try:
            orders = fetch_orders(status)
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

            columns = ('SKU', 'Ship Tag', 'Product Name', 'Quantity', 'Is Sample', 'Price', 'WT 1', 'WT 2')
            tree = self.create_treeview(order_frame, columns)
            self.populate_tree(tree, order)

            copy_button = ttk.Button(order_frame, text="Copy Order to Clipboard", command=lambda tr=tree: self.copy_to_clipboard(tr), bootstyle=PRIMARY)
            copy_button.pack(pady=10, side=tk.LEFT)

            update_button = ttk.Button(order_frame, text="Update Status to Accepted", command=lambda oid=order_id: self.confirm_update_status(oid), bootstyle=WARNING)
            update_button.pack(pady=10, side=tk.RIGHT)

    def create_treeview(self, parent, columns):
        """Utility function to create a Treeview widget with given columns."""
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
            quantity = float(item.get("quantity", 0))

            # Use sale_price if it's greater than 0, otherwise use ordered_unit_price
            sale_price = float(item.get("sale_price", {}).get("amount", 0))
            ordered_unit_price = float(item.get("ordered_unit_price", {}).get("amount", 0))

            # Get the price per unit (sale price takes priority)
            price_per_unit = sale_price if sale_price > 0 else ordered_unit_price

            # Get the unit multiplier
            unit_multiplier = float(item.get("unit_multiplier", 1))  # Default to 1 if not provided

            # Calculate total units (cases being sold)
            total_units = quantity / unit_multiplier  # This gives the number of cases sold

            # Calculate the total price based on the total units sold
            total_price = total_units * price_per_unit

            # Adjust price for samples (samples should be priced at 0.01 per unit)
            if is_sample == "Yes":
                total_price = 0.01 * quantity

            # Formatting product info and weights
            sku = product_info.get("sku", "N/A").lstrip('0') or "-"
            product_name = product_info.get("name", "N/A") or "-"
            base_units = float(product_info.get('base_units_per_unit', 0))

            wt1 = wt2 = ""

            # Weight calculations based on base units
            if base_units == 3.5:
                wt1 = quantity * 3.5
                wt2 = quantity * 3.6
            elif base_units == 7.0:
                wt1 = quantity * 7.0
                wt2 = quantity * 7.2

            wt1 = f"{wt1:.2f}".rstrip('0').rstrip('.') if wt1 else ""
            wt2 = f"{wt2:.2f}".rstrip('0').rstrip('.') if wt2 else ""
            total_price_str = f"${total_price:.2f}".rstrip('0').rstrip('.') if total_price else ""

            # Insert data into the treeview
            values = (
                sku,
                "",
                product_name,
                str(quantity),
                is_sample,
                total_price_str,
                wt1,
                wt2
            )
            
            tree.insert('', 'end', values=values, tags=('sample',) if item.get("is_sample", False) else ())

    def copy_to_clipboard(self, tree):
        tree.selection_set(tree.get_children())
        selected_items = tree.selection()
        clipboard_data = '\n'.join('\t'.join(tree.item(item, 'values')) for item in selected_items)
        self.root.clipboard_clear()
        self.root.clipboard_append(clipboard_data)

    def confirm_update_status(self, order_id):
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
