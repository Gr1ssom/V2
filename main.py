import tkinter as tk
from tkinter import ttk, messagebox
from leaflink_api import fetch_orders

# Constants
CORRECT_PIN = '1234'

def populate_treeview(orders, scrollable_frame):
    """Populates the treeview with detailed order and line item data in separate sections, each with a copy button."""
    for widget in scrollable_frame.winfo_children():
        widget.destroy()  # Clear previous widgets

    for order in orders:
        buyer_name = order.get("customer", {}).get("display_name", "Unknown Buyer")
        buyer_id = order.get("customer", {}).get("id", "N/A")

        # Create a frame for each order
        order_frame = ttk.Frame(scrollable_frame, padding="10")
        order_frame.pack(fill='x', expand=True, padx=10, pady=10, anchor="n")

        # Order header
        tk.Label(order_frame, text=f"Buyer: {buyer_name} - ID: {buyer_id}", font=('Helvetica', 16, 'bold')).pack(side="top", fill="x")

        # Treeview for line items
        columns = ('SKU', 'Ship Tag', 'Product Name', 'Unit Multiplier', 'Base 3.50', 'Base 7.00', 'Base 28.00', 'Base 448.00', 'Is Sample')
        tree = ttk.Treeview(order_frame, columns=columns, show="headings", height=5)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", stretch=tk.YES)  # Allow columns to stretch
        tree.pack(expand=True, fill='both')

        # Populate tree with line items
        for item in order.get("line_items", []):
            product_info = item.get("frozen_data", {}).get("product", {})
            is_sample = "Yes" if item.get("is_sample", False) else "No"

            # Initialize empty strings for specialized base unit columns
            base_3_50 = base_7_00 = base_28_00 = base_448_00 = ""
            unit_multiplier_display = item.get("unit_multiplier", "-")  # Default display value for unit multiplier

            # Check base units and format quantity without decimals
            base_units = float(product_info.get('base_units_per_unit', 0))
            if base_units == 3.50:
                base_3_50 = str(int(float(item.get("quantity", "N/A")))) if item.get("quantity", "N/A") != "N/A" else "-"
            elif base_units == 7.00:
                base_7_00 = str(int(float(item.get("quantity", "N/A")))) if item.get("quantity", "N/A") != "N/A" else "-"
            elif base_units == 28.00:
                base_28_00 = str(int(float(item.get("quantity", "N/A")))) if item.get("quantity", "N/A") != "N/A" else "-"
            elif base_units == 448.00:
                base_448_00 = str(int(float(item.get("quantity", "N/A")))) if item.get("quantity", "N/A") != "N/A" else "-"

            # Format all columns to show '-' if they are empty
            values = (
                product_info.get("sku", "N/A") or "-",
                "",  # Ship Tag left empty
                product_info.get("name", "N/A") or "-",
                unit_multiplier_display,
                base_3_50 or "-",
                base_7_00 or "-",
                base_28_00 or "-",
                base_448_00 or "-",
                is_sample
            )

            tree.insert('', 'end', values=values)

        # Copy to Clipboard Button for this order
        copy_button = tk.Button(order_frame, text="Copy Order to Clipboard", command=lambda tr=tree: copy_to_clipboard(tr))
        copy_button.pack(pady=10)

def copy_to_clipboard(tree):
    """Copies all items in the specified Treeview to the clipboard."""
    tree.selection_set(tree.get_children())
    selected_items = tree.selection()
    clipboard_data = '\n'.join('\t'.join(tree.item(item, 'values')) for item in selected_items)
    root.clipboard_clear()
    root.clipboard_append(clipboard_data)
    messagebox.showinfo("Success", "All order data copied to clipboard!")

def validate_pin(scrollable_frame):
    """Validates the entered PIN and fetches data if correct."""
    entered_pin = pin_entry.get()
    if entered_pin == CORRECT_PIN:
        orders = fetch_orders()
        if orders:
            populate_treeview(orders, scrollable_frame)
        else:
            messagebox.showinfo("Information", "No submitted orders to process.")
    else:
        messagebox.showerror("Error", "Invalid PIN")

def refresh_orders(scrollable_frame):
    """Refreshes and fetches new orders to display."""
    orders = fetch_orders()
    if orders:
        populate_treeview(orders, scrollable_frame)
    else:
        messagebox.showinfo("Information", "No new submitted orders to process.")

def create_gui():
    global root, pin_entry
    root = tk.Tk()
    root.title("LeafLink Order Viewer")
    root.geometry('1200x800')  # Adjust size as needed

    tk.Label(root, text="Enter PIN:", font=('Helvetica', 14, 'bold')).pack(pady=10)
    pin_entry = tk.Entry(root, font=('Helvetica', 14), show="*")
    pin_entry.pack(pady=5)

    submit_button = tk.Button(root, text="Submit", command=lambda: validate_pin(scrollable_frame))
    submit_button.pack(pady=10)

    # Refresh button setup
    refresh_button = tk.Button(root, text="Refresh", command=lambda: refresh_orders(scrollable_frame))
    refresh_button.pack(pady=10)

    # Scrollable frame setup
    canvas = tk.Canvas(root)
    scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollable_frame = ttk.Frame(canvas)
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.pack(side="left", fill="both", expand=True)

    root.mainloop()

if __name__ == "__main__":
    create_gui()