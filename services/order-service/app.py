from flask import Flask, jsonify

app = Flask(__name__)

orders = [
    {
        "id": 1,
        "user_id": 1,
        "product_id": 2,
        "quantity": 1,
        "status": "created"
        
    },
    {
        "id": 2,
        "user_id": 1,
        "product_id": 3,
        "quantity": 2,
        "status": "shipped"
        
    }
]

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/orders")
def get_orders():
    return jsonify(orders)

@app.get("/orders/<int:order_id>")
def get_order(order_id):
    for order in orders:
        if order["id"] == order_id:
            return jsonify(order)
    return {"error": "Order not found"}, 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)