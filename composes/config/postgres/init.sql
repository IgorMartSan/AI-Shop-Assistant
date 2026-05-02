CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    price NUMERIC(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO products (name, price)
VALUES
    ('Notebook Pro 14', 6499.90),
    ('Notebook Air 13', 5299.90),
    ('Mouse Sem Fio', 89.90),
    ('Teclado Mecânico RGB', 299.90),
    ('Monitor 24 Polegadas', 799.90),
    ('Monitor Ultrawide 29', 1499.90),
    ('Headset Gamer', 249.90),
    ('Caixa de Som Bluetooth', 189.90),
    ('Webcam Full HD', 159.90),
    ('SSD 1TB NVMe', 429.90),
    ('HD Externo 2TB', 379.90),
    ('Pen Drive 128GB', 69.90),
    ('Smartphone X1', 2199.90),
    ('Smartphone X1 Pro', 3299.90),
    ('Capa para Smartphone', 39.90),
    ('Película de Vidro', 24.90),
    ('Carregador Turbo USB-C', 79.90),
    ('Fone Bluetooth', 129.90),
    ('Smartwatch Fit', 499.90),
    ('Tablet Plus 10', 1799.90),
    ('Impressora Multifuncional', 899.90),
    ('Cadeira Ergonômica', 1199.90),
    ('Mesa para Escritório', 699.90),
    ('Luminária LED', 59.90),
    ('Roteador Wi-Fi 6', 349.90),
    ('Câmera de Segurança', 229.90),
    ('Aspirador Robô', 1399.90),
    ('Cafeteira Elétrica', 249.90),
    ('Liquidificador Inox', 199.90),
    ('Air Fryer 5L', 399.90);
