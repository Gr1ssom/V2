# leaflink_api.py
import requests

# Constants for API access
API_KEY = 'a5756636f561105935c17d86f8c657306c6b9f0a609997c2b7f361ffa9df3985'
API_URL = 'https://www.leaflink.com/api/v2/orders-received/'

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
    response = requests.get(API_URL, headers=headers, params=params)
    if response.status_code == 200:
        print("API call successful.")
        orders = response.json()['results']
        print(f"Found {len(orders)} submitted orders with line item details.")
        return orders
    else:
        print(f"API Error: {response.status_code} - {response.text}")
        return []
