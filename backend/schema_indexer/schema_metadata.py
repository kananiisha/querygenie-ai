"""
Describes the database schema in natural language so it can be embedded
and semantically searched by the Schema Retriever Agent.

Each entry = one table, written as a descriptive chunk that a sentence
embedding model can match against a user's natural-language question.
"""

SCHEMA_METADATA = [
    {
        "table": "customers",
        "columns": ["customer_id", "name", "email", "city", "signup_date"],
        "description": (
            "Table: customers. Stores customer details including name, email, "
            "the city they live in, and the date they signed up. "
            "Use this table for questions about who customers are, where they "
            "are located, or when they joined."
        ),
    },
    {
        "table": "products",
        "columns": ["product_id", "name", "category", "price"],
        "description": (
            "Table: products. Stores product catalog details including name, "
            "category (Electronics, Clothing, Home, Books), and price. "
            "Use this table for questions about what products exist, their "
            "categories, or their prices."
        ),
    },
    {
        "table": "orders",
        "columns": ["order_id", "customer_id", "order_date", "status"],
        "description": (
            "Table: orders. Stores each order placed by a customer, including "
            "the order date and status (placed, shipped, delivered, cancelled). "
            "Links to customers via customer_id. "
            "Use this table for questions about how many orders were placed, "
            "when, or their status."
        ),
    },
    {
        "table": "order_items",
        "columns": ["order_item_id", "order_id", "product_id", "quantity", "unit_price"],
        "description": (
            "Table: order_items. Stores individual product line items within "
            "an order, including quantity and unit price. Links orders to "
            "products. Use this table for questions about which products "
            "were bought in which orders, quantities, or revenue per product."
        ),
    },
    {
        "table": "payments",
        "columns": ["payment_id", "order_id", "amount", "payment_method", "payment_date", "status"],
        "description": (
            "Table: payments. Stores payment records for orders, including "
            "amount, payment method (upi, card, netbanking, cod), and payment "
            "status (success, failed, pending). Use this table for questions "
            "about revenue, payment methods, or failed/pending payments."
        ),
    },
]
