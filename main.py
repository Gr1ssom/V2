import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from leaflink_api import fetch_orders

# Constants
CORRECT_PIN = '1234'

def populate_treeview(data_frame):
    # Clear existing data in the Treeview
    for i in tree.get_children():
        tree.delete(i)
    # Adding new data to the Treeview
    for row in data_frame.itertuples(index=False):
        tree.insert('', 'end', values=row)

def copy_to_clipboard():
    # Get selected items
    selected_items = tree.selection()
    if not selected_items:
        messagebox.showinfo("Copy to Clipboard", "No item selected.")
        return
    # Extract data from each selected item
    rows = [tree.item(item, 'values') for item in selected_items]
    # Convert rows to a string and copy to clipboard
    clipboard_data = '\n'.join('\t'.join(map(str, row)) for row in rows)
    root.clipboard_clear()
    root.clipboard_append(clipboard_data)
    messagebox.showinfo("Success", "Data copied to clipboard!")

def validate_pin():
    entered_pin = pin_entry.get()
    if entered_pin == CORRECT_PIN:
        orders = fetch_orders()
        if orders:
            data_frame = pd.DataFrame(orders)
            populate_treeview(data_frame)
        else:
            messagebox.showinfo("Information", "No submitted orders to process.")
    else:
        messagebox.showerror("Error", "Invalid PIN")

def create_gui():
    global root, pin_entry, tree
    root = tk.Tk()
    root.title("LeafLink Order Fetcher")
    root.geometry('1000x600')

    tk.Label(root, text="Enter PIN:").pack(pady=10)
    pin_entry = tk.Entry(root, show="*")
    pin_entry.pack(pady=5)

    submit_button = tk.Button(root, text="Submit", command=validate_pin)
    submit_button.pack(pady=10)

    # Treeview setup
    tree = ttk.Treeview(root, columns=('Order ID', 'Status', 'Customer', 'Total Items'), show="headings", height=15)
    tree.pack(expand=True, fill='both', padx=10, pady=10)
    for col in tree['columns']:
        tree.heading(col, text=col)

    # Copy to clipboard button
    copy_button = tk.Button(root, text="Copy Selected to Clipboard", command=copy_to_clipboard)
    copy_button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
