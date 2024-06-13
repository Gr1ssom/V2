import requests

# Constants for API access
API_KEY = '8ac014b8788268a5fcd1028ac22b948ce29c11e7267d098fdb13c9f3ca2face6'
API_URL = 'https://www.leaflink.com/api/v2/orders-received/'

def fetch_orders(status):
    """Fetches orders with the specified status from the LeafLink API and includes line item details."""
    headers = {
        'Authorization': f'App {API_KEY}',
        'Content-Type': 'application/json'
    }
    params = {
        'status': status,
        'include_children': 'line_items'
    }
    try:
        response = requests.get(API_URL, headers=headers, params=params)
        response.raise_for_status()
        print("API call successful.")
        orders = response.json()['results']
        print(f"Found {len(orders)} {status.lower()} orders with line item details.")
        return orders
    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")
        return []

def update_order_status(order_id, new_status):
    """Updates the status of an order."""
    headers = {
        'Authorization': f'App {API_KEY}',
        'Content-Type': 'application/json'
    }
    data = {
        'status': new_status
    }
    try:
        response = requests.patch(f"{API_URL}{order_id}/", headers=headers, json=data)
        response.raise_for_status()
        print(f"Order {order_id} status updated to {new_status}.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")
        return False
