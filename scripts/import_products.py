import os
import psycopg
import csv
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

CSV_PATH = Path.home() / "Downloads" / "articles.csv" / "articles.csv"

connection = psycopg.connect(
    host="localhost",
    port=5432,
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD")
)

print("PostgreSQL connection successful!")

with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as file:
    reader = csv.DictReader(file)

    with connection.cursor() as cursor:
        for row in reader:

            product = {
                "article_id": row["article_id"],
                "product_code": row["product_code"],
                "name": row["prod_name"],
                "product_type": row["product_type_name"],
                "product_group": row["product_group_name"],
                "color": row["colour_group_name"],
                "department": row["department_name"],
                "section": row["section_name"],
                "garment_group": row["garment_group_name"],
                "description": row["detail_desc"]
            }

            cursor.execute(
                """
                INSERT INTO products (
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
                )
                VALUES (
                    %(article_id)s,
                    %(product_code)s,
                    %(name)s,
                    %(product_type)s,
                    %(product_group)s,
                    %(color)s,
                    %(department)s,
                    %(section)s,
                    %(garment_group)s,
                    %(description)s
                )
                ON CONFLICT (article_id) DO NOTHING
                """,
                product
            )

connection.commit()
connection.close()

print("Products imported successfully!")