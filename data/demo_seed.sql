INSERT INTO cooperatives (name, region, founded_year) VALUES
    ('Kigali Growers', 'Kigali', 2015),
    ('Musanze Highlands', 'Musanze', 2012),
    ('Huye Valley Farmers', 'Huye', 2018);

INSERT INTO members (cooperative_id, full_name, role, joined_at) VALUES
    (1, 'Alice Uwase', 'chair', '2015-03-01'),
    (1, 'Beatrice Mukamana', 'member', '2016-07-14'),
    (1, 'Claude Habimana', 'treasurer', '2017-01-20'),
    (2, 'Diane Ingabire', 'chair', '2012-05-10'),
    (2, 'Eric Nshimiyimana', 'member', '2019-09-02'),
    (3, 'Grace Umutoni', 'chair', '2018-02-11'),
    (3, 'Henri Bizimana', 'member', '2020-11-30');

INSERT INTO products (name, category, unit_price) VALUES
    ('Arabica Coffee 1kg', 'coffee', 12.50),
    ('Robusta Coffee 1kg', 'coffee', 9.00),
    ('Dried Beans 1kg', 'legumes', 3.20),
    ('Honey 500g', 'honey', 6.75),
    ('Avocado Crate', 'produce', 15.00);

INSERT INTO orders (member_id, total_amount, status, created_at) VALUES
    (1, 62.50, 'fulfilled', '2026-05-01 10:00:00'),
    (2, 27.00, 'fulfilled', '2026-05-03 14:30:00'),
    (3, 15.00, 'pending', '2026-06-10 09:15:00'),
    (4, 90.00, 'fulfilled', '2026-06-15 11:45:00'),
    (5, 6.75, 'fulfilled', '2026-06-20 16:00:00'),
    (6, 45.00, 'pending', '2026-07-01 08:30:00'),
    (7, 12.50, 'fulfilled', '2026-07-03 13:20:00');

INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
    (1, 1, 5, 12.50),
    (2, 2, 3, 9.00),
    (3, 5, 1, 15.00),
    (4, 1, 4, 12.50),
    (4, 3, 10, 3.20),
    (5, 4, 1, 6.75),
    (6, 1, 2, 12.50),
    (6, 3, 6, 3.20),
    (7, 1, 1, 12.50);

INSERT INTO payments (order_id, amount, method, paid_at) VALUES
    (1, 62.50, 'mobile_money', '2026-05-01 10:05:00'),
    (2, 27.00, 'cash', '2026-05-03 14:35:00'),
    (4, 60.00, 'bank_transfer', '2026-06-15 12:00:00'),
    (5, 6.75, 'mobile_money', '2026-06-20 16:05:00'),
    (7, 12.50, 'cash', '2026-07-03 13:25:00');
