-- ============================================
-- QueryGenie AI — Sample Business Database
-- Domain: E-commerce
-- ============================================

-- ---------- SCHEMA ----------

CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    email       VARCHAR(100) UNIQUE NOT NULL,
    city        VARCHAR(50),
    signup_date DATE NOT NULL
);

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    category    VARCHAR(50) NOT NULL,
    price       NUMERIC(10,2) NOT NULL
);

CREATE TABLE orders (
    order_id     SERIAL PRIMARY KEY,
    customer_id  INTEGER NOT NULL REFERENCES customers(customer_id),
    order_date   DATE NOT NULL,
    status       VARCHAR(20) NOT NULL CHECK (status IN ('placed','shipped','delivered','cancelled'))
);

CREATE TABLE order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id      INTEGER NOT NULL REFERENCES orders(order_id),
    product_id    INTEGER NOT NULL REFERENCES products(product_id),
    quantity      INTEGER NOT NULL CHECK (quantity > 0),
    unit_price    NUMERIC(10,2) NOT NULL
);

CREATE TABLE payments (
    payment_id     SERIAL PRIMARY KEY,
    order_id       INTEGER NOT NULL REFERENCES orders(order_id),
    amount         NUMERIC(10,2) NOT NULL,
    payment_method VARCHAR(20) NOT NULL CHECK (payment_method IN ('upi','card','netbanking','cod')),
    payment_date   DATE NOT NULL,
    status         VARCHAR(20) NOT NULL CHECK (status IN ('success','failed','pending'))
);

-- ---------- SEED DATA ----------

INSERT INTO customers (name, email, city, signup_date) VALUES
('Priya Sharma', 'priya.sharma@mail.com', 'Ahmedabad', '2025-01-12'),
('Rohan Mehta', 'rohan.mehta@mail.com', 'Mumbai', '2025-02-03'),
('Sneha Patel', 'sneha.patel@mail.com', 'Ahmedabad', '2025-02-20'),
('Arjun Verma', 'arjun.verma@mail.com', 'Delhi', '2025-03-05'),
('Kavya Nair', 'kavya.nair@mail.com', 'Bangalore', '2025-03-18'),
('Vivek Joshi', 'vivek.joshi@mail.com', 'Pune', '2025-04-02'),
('Anjali Desai', 'anjali.desai@mail.com', 'Surat', '2025-04-15'),
('Karan Singh', 'karan.singh@mail.com', 'Delhi', '2025-05-01'),
('Meera Iyer', 'meera.iyer@mail.com', 'Chennai', '2025-05-22'),
('Aditya Rao', 'aditya.rao@mail.com', 'Bangalore', '2025-06-10');

INSERT INTO products (name, category, price) VALUES
('Wireless Earbuds', 'Electronics', 1499.00),
('Smartwatch', 'Electronics', 2999.00),
('Bluetooth Speaker', 'Electronics', 1799.00),
('Cotton T-Shirt', 'Clothing', 499.00),
('Denim Jacket', 'Clothing', 1999.00),
('Running Shoes', 'Clothing', 2499.00),
('Non-stick Pan', 'Home', 899.00),
('LED Desk Lamp', 'Home', 699.00),
('Bedsheet Set', 'Home', 1299.00),
('Fiction Novel', 'Books', 349.00),
('Self-Help Book', 'Books', 299.00),
('Notebook Set', 'Books', 199.00);

INSERT INTO orders (customer_id, order_date, status) VALUES
(1, '2025-04-01', 'delivered'),
(2, '2025-04-03', 'delivered'),
(3, '2025-04-10', 'cancelled'),
(1, '2025-04-15', 'delivered'),
(4, '2025-04-20', 'shipped'),
(5, '2025-05-02', 'delivered'),
(6, '2025-05-05', 'delivered'),
(2, '2025-05-10', 'placed'),
(7, '2025-05-14', 'delivered'),
(8, '2025-05-20', 'delivered'),
(3, '2025-05-25', 'delivered'),
(9, '2025-06-01', 'shipped'),
(10, '2025-06-05', 'delivered'),
(4, '2025-06-08', 'placed'),
(5, '2025-06-12', 'delivered');

INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
(1, 1, 1, 1499.00),
(1, 4, 2, 499.00),
(2, 2, 1, 2999.00),
(3, 6, 1, 2499.00),
(4, 7, 1, 899.00),
(4, 8, 1, 699.00),
(5, 5, 1, 1999.00),
(6, 1, 2, 1499.00),
(7, 9, 1, 1299.00),
(8, 3, 1, 1799.00),
(9, 10, 3, 349.00),
(10, 2, 1, 2999.00),
(10, 11, 1, 299.00),
(11, 6, 1, 2499.00),
(12, 1, 1, 1499.00),
(13, 4, 3, 499.00),
(13, 12, 2, 199.00),
(14, 5, 1, 1999.00),
(15, 3, 2, 1799.00);

INSERT INTO payments (order_id, amount, payment_method, payment_date, status) VALUES
(1, 2497.00, 'upi', '2025-04-01', 'success'),
(2, 2999.00, 'card', '2025-04-03', 'success'),
(3, 2499.00, 'upi', '2025-04-10', 'failed'),
(4, 1598.00, 'card', '2025-04-20', 'success'),
(5, 1999.00, 'netbanking', '2025-04-20', 'success'),
(6, 2998.00, 'upi', '2025-05-02', 'success'),
(7, 1299.00, 'cod', '2025-05-05', 'success'),
(8, 1799.00, 'card', '2025-05-14', 'success'),
(9, 1047.00, 'upi', '2025-06-01', 'success'),
(10, 3298.00, 'card', '2025-06-05', 'success'),
(11, 2499.00, 'upi', '2025-05-25', 'success'),
(12, 1499.00, 'cod', '2025-06-01', 'pending'),
(13, 1895.00, 'upi', '2025-06-08', 'success'),
(14, 1999.00, 'netbanking', '2025-06-08', 'success'),
(15, 3598.00, 'card', '2025-06-12', 'success');
