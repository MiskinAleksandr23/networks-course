from flask import Flask, request, jsonify

app = Flask(__name__)

products = []
NotFoundError = "Not found"

def find_product(product_id):
    return next((p for p in products if p["id"] == product_id), None)

@app.route('/products', methods=['GET'])
def get_products():
    return jsonify(products), 200

@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = find_product(product_id)
    if product:
        return jsonify(product), 200
    else:
        return jsonify({"error": NotFoundError }), 404

@app.route('/products', methods=['POST'])
def create_product():
    data = request.get_json()

    if not data or 'name' not in data or 'description' not in data:
        return jsonify({"error": "Name and description are required"}), 400
    
    new_id = max(p["id"] for p in products) + 1 if products else 1
    
    new_product = {
        "id": new_id,
        "name": data['name'],
        "description": data['description']
    }
    products.append(new_product)
    
    return jsonify(new_product), 201


@app.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    product = find_product(product_id)
    if not product:
        return jsonify({"error": NotFoundError }), 404
    
    data = request.get_json()
    if not data or 'name' not in data or 'description' not in data:
        return jsonify({"error": "Name and description are required"}), 400
    
    product['name'] = data['name']
    product['description'] = data['description']
    
    return jsonify(product), 200

@app.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    global products
    
    product = find_product(product_id)
    if not product:
        return jsonify({"error": NotFoundError }), 404
    
    products = [p for p in products if p['id'] != product_id]
    
    return jsonify({"message": "Deleted"}), 200

if __name__ == '__main__':
    app.run(debug = False)