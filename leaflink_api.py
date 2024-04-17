import requests
import logging

# Constants for API access
API_KEY = '8ac014b8788268a5fcd1028ac22b948ce29c11e7267d098fdb13c9f3ca2face6'
API_URL = 'https://www.leaflink.com/api/v2/orders-received/?include_children=line_items'

def fetch_orders():
    """Fetches orders with 'Submitted' status from the LeafLink API and includes line item details."""
    headers = {
        'Authorization': f'App {API_KEY}',
        'Content-Type': 'application/json'
    }
    params = {
        'status': 'Submitted',
        'include_children': 'line_items'
    }
    try:
        response = requests.get(API_URL, headers=headers, params=params)
        response.raise_for_status()  # This will raise an exception for HTTP errors
        orders = response.json().get('results', [])
        logging.info(f"API call successful. Found {len(orders)} submitted orders with line item details.")
        return orders
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP Error: {e.response.status_code} - {e.response.text}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching orders: {str(e)}")
    except ValueError as e:
        logging.error("Error decoding JSON response")
    return []

# Set up basic logging
logging.basicConfig(level=logging.INFO)

# Example call to fetch_orders to check functionality
if __name__ == '__main__':
    orders = fetch_orders()
    print(orders)
