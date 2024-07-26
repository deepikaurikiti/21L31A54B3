from flask import Flask, request, jsonify
import requests
import uuid

app = Flask(__name__)


BASE_URL = "http://20.244.56.144/test/companies"
COMPANIES = ["AMZ", "FLP", "SNP", "HVN", "420"]
CATEGORIES = ["Phone", "Computer", "TV", "Earphone", "Tablet", "Charger", "House", "Keypad", "Bluetooth", "Pendrive", "Remote", "Speaker", "Headset", "Laptop", "PC"]

def fetch_products(company, category, top_n, min_price, max_price):
    url = f"{BASE_URL}/{company}/categories/{category}/products/top-{top_n}?minPrice={min_price}&maxPrice={max_price}"
    try:
        response = requests.get(url, timeout=1)
        if response.status_code == 200:
            return response.json().get('products', [])
        return []
    except requests.RequestException:
        return []

def get_all_products(category, top_n, min_price, max_price):
    all_products = []
    for company in COMPANIES:
        products = fetch_products(company, category, top_n, min_price, max_price)
        if products:
            all_products.extend(products)
    return all_products

def sort_products(products, sort_by, order):
    return sorted(products, key=lambda x: x.get(sort_by, 0), reverse=(order == 'desc'))

@app.route('/categories/<category_name>/products', methods=['GET'])
def get_products(category_name):
    if category_name not in CATEGORIES:
        return jsonify({"error": "Invalid category name"}), 400

    try:
        n = int(request.args.get('n', 10))
        page = int(request.args.get('page', 1))
        min_price = float(request.args.get('minPrice', 0))
        max_price = float(request.args.get('maxPrice', float('inf')))
        sort_by = request.args.get('sortBy', 'rating')
        order = request.args.get('order', 'desc')

        if n > 10 and not page:
            return jsonify({"error": "Page parameter is required for pagination when n > 10"}), 400

        products = get_all_products(category_name, n, min_price, max_price)

        if sort_by in ['rating', 'price', 'company', 'discount']:
            products = sort_products(products, sort_by, order)

        start = (page - 1) * n
        end = start + n
        paginated_products = products[start:end]

        response = {
            "products": [{"id": str(uuid.uuid4()), **product} for product in paginated_products],
            "page": page,
            "perPage": n,
            "totalProducts": len(products)
        }
        return jsonify(response)
    except ValueError:
        return jsonify({"error": "Invalid query parameter value"}), 400

@app.route('/categories/<category_name>/products/<product_id>', methods=['GET'])
def get_product_details(category_name, product_id):
    if category_name not in CATEGORIES:
        return jsonify({"error": "Invalid category name"}), 400

   
    products = get_all_products(category_name, 100, 0, float('inf'))
    product = next((p for p in products if str(uuid.uuid4()) == product_id), None)

    if not product:
        return jsonify({"error": "Product not found"}), 404

    return jsonify({"product": product})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9876)
