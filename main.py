import tkinter as tk
from tkinter import ttk, messagebox
from leaflink_api import fetch_orders

# Constants
CORRECT_PIN = '1234'

def populate_treeview(orders):
    """Populates the treeview with detailed order and line item data in separate sections, each with a copy button."""
    for widget in main_frame.winfo_children():
        widget.destroy()  # Clear previous widgets

    for order in orders:
        buyer_name = order.get("customer", {}).get("display_name", "Unknown Buyer")
        buyer_id = order.get("customer", {}).get("id", "N/A")

        # Create a frame for each order
        order_frame = ttk.Frame(main_frame, padding="10")
        order_frame.pack(fill='x', expand=True, padx=10, pady=10, anchor="n")

        # Order header
        tk.Label(order_frame, text=f"Buyer: {buyer_name} - ID: {buyer_id}", font=('Helvetica', 16, 'bold')).pack(side="top", fill="x")

        # Treeview for line items
        columns = ('SRC PKG', 'PKG TAG', 'ITEM NAME', '0.5G', '1G/2PK', '5PK', '3.5G', '7G', '28G', '1LB', 'SAMPLES', 'QTY 1', 'QTY 2', 'PRICE')
        tree = ttk.Treeview(order_frame, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            if col == 'ITEM NAME':
                tree.column(col, anchor="center", stretch=tk.YES, width=200)  # Wider column for ITEM NAME
            else:
                tree.column(col, anchor="center", stretch=tk.YES, width=100)  # Default width for other columns

        # Define tag for samples
        tree.tag_configure('sample', background='lightblue')

        # Adding the scrollbar
        scrollbar = ttk.Scrollbar(order_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        tree.pack(expand=True, fill='both')

        # Populate tree with line items
        for item in order.get("line_items", []):
            product_info = item.get("frozen_data", {}).get("product", {})
            is_sample = "Yes" if item.get("is_sample", False) else "No"
            if is_sample == "Yes":
                price = "$0.01"
            else:
                sale_price = item.get("sale_price", {}).get("amount", 0)
                price = f"${sale_price:.2f}" if sale_price > 0 else f"${item.get('ordered_unit_price', {}).get('amount', 0):.2f}"

            # Initialize empty strings for specialized base unit columns
            base_0_5g = base_1_00 = base_2_5g = base_3_50 = base_7_00 = base_28_00 = base_448_00 = ""

            # Check base units and format quantity without decimals
            base_units = float(product_info.get('base_units_per_unit', 0))
            calculated_qty_1 = ""
            calculated_qty_2 = ""
            if base_units == 0.5:
                base_0_5g = str(int(float(item.get("quantity", "N/A")))) if item.get("quantity", "N/A") != "N/A" else "-"
            elif base_units == 1.00:
                base_1_00 = str(int(float(item.get("quantity", "N/A")))) if item.get("quantity", "N/A") != "N/A" else "-"
            elif base_units == 2.5:
                base_2_5g = str(int(float(item.get("quantity", "N/A")))) if item.get("quantity", "N/A") != "N/A" else "-"
            elif base_units == 3.50:
                base_3_50 = str(int(float(item.get("quantity", "N/A")))) if item.get("quantity", "N/A") != "N/A" else "-"
                calculated_qty_1 = str(float(item.get("quantity", 0)) * 3.6)
                calculated_qty_2 = str(float(item.get("quantity", 0)) * 3.5)
            elif base_units == 7.00:
                base_7_00 = str(int(float(item.get("quantity", "N/A")))) if item.get("quantity", "N/A") != "N/A" else "-"
                if calculated_qty_1 == "":
                    calculated_qty_1 = str(float(item.get("quantity", 0)) * 7.2)
                if calculated_qty_2 == "":
                    calculated_qty_2 = str(float(item.get("quantity", 0)) * 7.0)
            elif base_units == 28.00:
                base_28_00 = str(int(float(item.get("quantity", "N/A")))) if item.get("quantity", "N/A") != "N/A" else "-"
            elif base_units == 448.00:
                base_448_00 = str(int(float(item.get("quantity", "N/A")))) if item.get("quantity", "N/A") != "N/A" else "-"

            values = (
                product_info.get("sku", "N/A") or "-",
                "",  # PKG TAG left empty
                product_info.get("name", "N/A") or "-",
                base_0_5g or "-",
                base_1_00 or "-",
                base_2_5g or "-",
                base_3_50 or "-",
                base_7_00 or "-",
                base_28_00 or "-",
                base_448_00 or "-",
                is_sample,
                calculated_qty_1 or "-",
                calculated_qty_2 or "-",
                price
            )

            # Insert item with sample tag if applicable
            if item.get("is_sample", False):
                tree.insert('', 'end', values=values, tags=('sample',))
            else:
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

def validate_pin():
    """Validates the entered PIN and fetches data if correct."""
    entered_pin = pin_entry.get()
    if entered_pin == CORRECT_PIN:
        pin_label.pack_forget()
        pin_entry.pack_forget()
        submit_button.pack_forget()
        refresh_button.pack(pady=10)  # Show the refresh button after successful PIN validation
        orders = fetch_orders()
        if orders:
            populate_treeview(orders)
        else:
            messagebox.showinfo("Information", "No submitted orders to process.")
    else:
        messagebox.showerror("Error", "Invalid PIN")

def refresh_orders():
    """Refreshes and fetches new orders to display."""
    orders = fetch_orders()
    if orders:
        populate_treeview(orders)
    else:
        messagebox.showinfo("Information", "No new submitted orders to process.")

def create_gui():
    global root, pin_label, pin_entry, submit_button, refresh_button, main_frame
    root = tk.Tk()
    root.title("LeafLink Order Viewer by Grissom")

    # Set the window size to 80% of 1920x1080
    window_width = int(root.winfo_screenwidth() * 0.8)
    window_height = int(root.winfo_screenheight() * 0.8)
    root.geometry(f'{window_width}x{window_height}')

    pin_label = tk.Label(root, text="Enter PIN:", font=('Helvetica', 14, 'bold'))
    pin_label.pack(pady=10)
    pin_entry = tk.Entry(root, font=('Helvetica', 14), show="*")
    pin_entry.pack(pady=5)

    submit_button = tk.Button(root, text="Submit", command=validate_pin)
    submit_button.pack(pady=10)

    # Refresh button setup
    refresh_button = tk.Button(root, text="Refresh", command=refresh_orders)
    refresh_button.pack_forget()  # Initially hide the refresh button

    # Main frame setup with scrollbar
    canvas = tk.Canvas(root)
    canvas.pack(side="left", fill="both", expand=True)
    
    scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    canvas.configure(yscrollcommand=scrollbar.set)
    main_frame = ttk.Frame(canvas)
    canvas.create_window((0, 0), window=main_frame, anchor="nw")

    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    main_frame.bind("<Configure>", on_frame_configure)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
