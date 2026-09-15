from flask import Flask, jsonify

app = Flask(__name__)

products = [
    {
        "id": 1,
        "name": "Wireless Headphones",
        "price": 2499.90
    },
    {
        "id": 2,
        "name": "Mechanical Keyboard",
        "price": 1899.90
    },
    {
        "id": 3,
        "name": "Gaming Mouse",
        "price": 999.90
    }
]

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/products")
def get_products():
    return jsonify(products)

@app.get("/products/<int:product_id>")
def get_product(product_id):
    for product in products:
        if product["id"] == product_id:
            return jsonify(product)
        
    return {"error": "Product not found"}, 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)