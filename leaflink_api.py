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
    response = requests.get(API_URL, headers=headers, params=params)
    if response.status_code == 200:
        print("API call successful.")
        orders = response.json()['results']
        print(f"Found {len(orders)} {status.lower()} orders with line item details.")
        return orders
    else:
        print(f"API Error: {response.status_code} - {response.text}")
        return []
