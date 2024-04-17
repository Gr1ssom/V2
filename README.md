# LeafLink Order Viewer by Grissom

This application provides a user interface to view and copy order data fetched from the LeafLink API.

## How to Use

1. **PIN Entry**: Enter the correct PIN to access the order data.
2. **Submit Button**: Click the submit button after entering the PIN.
3. **Order Display**: Once the correct PIN is entered, the application will display the orders along with detailed information about each order and its line items.
4. **Copy Order to Clipboard**: You can copy the entire order data to the clipboard by clicking the "Copy Order to Clipboard" button for each order.

## Requirements

- Python 3.x
- tkinter library
- leaflink_api library

## Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/Gr1ssom/V2
   ```

2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:

   ```bash
   python main.py
   ```

2. Enter the correct PIN to access the order data.
3. Click the submit button to fetch and display the orders.
4. Copy order data to the clipboard as needed.

## License

This project is licensed under the [MIT License](LICENSE).
