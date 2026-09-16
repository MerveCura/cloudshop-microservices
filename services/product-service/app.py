from flask import Flask, jsonify
import os
import redis
import json

app = Flask(__name__)
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
CACHE_TTL = int(os.getenv("CACHE_TTL", 60))

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True,
    socket_connect_timeout=1,
    socket_timeout=1
)

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
    try:
        cached_products = redis_client.get("products")
        
        if cached_products:
            app.logger.info("Cache HIT for products")
            return {
                "source": "cache",
                "data": json.loads(cached_products)
            }
            
        app.logger.info("Cache MISS for products")
        
        redis_client.set("products", json.dumps(products), ex=CACHE_TTL)
        
    except redis.RedisError as error:
        app.logger.warning(f"Redis cache error: {error}")
        
    return {
        "source": "application",
        "data": products
    }
  

@app.get("/products/<int:product_id>")
def get_product(product_id):
    for product in products:
        if product["id"] == product_id:
            return jsonify(product)
        
    return {"error": "Product not found"}, 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)