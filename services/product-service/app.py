from flask import Flask, jsonify, request
import os
import redis
import json
import psycopg
from psycopg.rows import dict_row

app = Flask(__name__)

# -------------------------
# Redis Configuration
# -------------------------

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


# -------------------------
# PostgreSQL Configuration
# -------------------------

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", 5432))
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")


def get_db_connection():
    return psycopg.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        row_factory=dict_row
    )


# -------------------------
# Health Check
# -------------------------

@app.get("/health")
def health():
    return {"status": "healthy"}


# -------------------------
# Get Products
# -------------------------

@app.get("/products")
def get_products():

    # Pagination
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 20, type=int)

    # Search / Filter
    search = request.args.get("search", "", type=str)
    color = request.args.get("color", "", type=str)

    page = max(page, 1)
    limit = min(max(limit, 1), 100)

    offset = (page - 1) * limit

    # Every query gets its own Redis cache key
    cache_key = (
        f"products:page:{page}:limit:{limit}:"
        f"search:{search}:color:{color}"
    )

    # -------------------------
    # Check Redis Cache
    # -------------------------

    try:
        cached_products = redis_client.get(cache_key)

        if cached_products:
            app.logger.info("Cache HIT for %s", cache_key)

            return {
                "source": "cache",
                "page": page,
                "limit": limit,
                "data": json.loads(cached_products)
            }

        app.logger.info("Cache MISS for %s", cache_key)

    except redis.RedisError as error:
        app.logger.warning(f"Redis cache error: {error}")


    # -------------------------
    # PostgreSQL Query
    # -------------------------

    query = """
        SELECT
            article_id,
            product_code,
            name,
            product_type,
            product_group,
            color,
            department,
            section,
            garment_group,
            description
        FROM products
        WHERE (%s = '' OR name ILIKE %s)
          AND (%s = '' OR color = %s)
        ORDER BY article_id
        LIMIT %s OFFSET %s
    """

    search_pattern = f"%{search}%"

    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:

                cursor.execute(
                    query,
                    (
                        search,
                        search_pattern,
                        color,
                        color,
                        limit,
                        offset
                    )
                )

                products = cursor.fetchall()

    except psycopg.Error as error:
        app.logger.error(f"PostgreSQL error: {error}")

        return {
            "error": "Database unavailable"
        }, 503


    # -------------------------
    # Save Result to Redis
    # -------------------------

    try:
        redis_client.set(
            cache_key,
            json.dumps(products),
            ex=CACHE_TTL
        )

    except redis.RedisError as error:
        app.logger.warning(f"Redis cache error: {error}")


    return {
        "source": "database",
        "page": page,
        "limit": limit,
        "data": products
    }


# -------------------------
# Get Single Product
# -------------------------

@app.get("/products/<article_id>")
def get_product(article_id):

    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT
                        article_id,
                        product_code,
                        name,
                        product_type,
                        product_group,
                        color,
                        department,
                        section,
                        garment_group,
                        description
                    FROM products
                    WHERE article_id = %s
                    """,
                    (article_id,)
                )

                product = cursor.fetchone()

    except psycopg.Error as error:
        app.logger.error(f"PostgreSQL error: {error}")

        return {
            "error": "Database unavailable"
        }, 503

    if product is None:
        return {
            "error": "Product not found"
        }, 404

    return jsonify(product)


# -------------------------
# Start Application
# -------------------------

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5001
    )