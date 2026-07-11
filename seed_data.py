# ==========================================
# File: seed_data.py
# Mô tả: Script chèn dữ liệu mẫu vào database
#         Chạy: python seed_data.py
# ==========================================

from app import app, mysql
from models.database import init_database
from werkzeug.security import generate_password_hash


def seed():
    """Chèn dữ liệu mẫu vào tất cả các bảng."""
    with app.app_context():
        # Đảm bảo các bảng đã tồn tại
        init_database(mysql)

        cur = mysql.connection.cursor()

        # ------------------------------------------
        # 1. SEED USERS - Tài khoản mẫu
        # ------------------------------------------
        print("[*] Seeding users...")
        users = [
            ('admin', 'admin@coffeeshop.com', generate_password_hash('admin123'), 'admin'),
            ('staff1', 'staff1@coffeeshop.com', generate_password_hash('staff123'), 'staff'),
            ('staff2', 'staff2@coffeeshop.com', generate_password_hash('staff123'), 'staff'),
        ]

        for username, email, password, role in users:
            cur.execute("SELECT id FROM users WHERE username = %s", (username,))
            if not cur.fetchone():
                cur.execute(
                    "INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)",
                    (username, email, password, role)
                )
                print(f"    + Added user: {username} ({role})")
            else:
                print(f"    - User '{username}' already exists, skipped.")

        mysql.connection.commit()

        # ------------------------------------------
        # 2. SEED INGREDIENTS - Nguyên liệu mẫu
        # ------------------------------------------
        print("[*] Seeding ingredients...")
        ingredients = [
            ('Cà phê Robusta', 10.0, 'kg', 150000, 'Đắk Lắk Coffee Co.'),
            ('Cà phê Arabica', 5.0, 'kg', 280000, 'Lâm Đồng Farm'),
            ('Sữa đặc', 20.0, 'hộp', 18000, 'Vinamilk'),
            ('Sữa tươi', 15.0, 'lít', 32000, 'TH True Milk'),
            ('Đường trắng', 8.0, 'kg', 22000, 'Biên Hòa Sugar'),
            ('Đá viên', 50.0, 'kg', 5000, 'Ice Factory'),
            ('Trà xanh Thái Nguyên', 3.0, 'kg', 200000, 'Thái Nguyên Tea'),
            ('Bột cacao', 2.0, 'kg', 180000, 'Van Houten'),
            ('Syrup caramel', 5.0, 'chai', 85000, 'Monin'),
            ('Syrup vanilla', 4.0, 'chai', 85000, 'Monin'),
            ('Whipping cream', 6.0, 'hộp', 65000, 'Anchor'),
            ('Dừa tươi', 30.0, 'trái', 12000, 'Bến Tre Coconut'),
        ]

        for name, qty, unit, price, supplier in ingredients:
            cur.execute("SELECT id FROM ingredients WHERE name = %s", (name,))
            if not cur.fetchone():
                cur.execute(
                    "INSERT INTO ingredients (name, quantity, unit, price, supplier) VALUES (%s, %s, %s, %s, %s)",
                    (name, qty, unit, price, supplier)
                )
                print(f"    + Added ingredient: {name}")
            else:
                print(f"    - Ingredient '{name}' already exists, skipped.")

        mysql.connection.commit()

        # ------------------------------------------
        # 3. SEED PRODUCTS - Sản phẩm cà phê mẫu
        # ------------------------------------------
        print("[*] Seeding products...")
        products = [
            ('Cà phê đen đá', 'Cà phê đen truyền thống pha phin với đá', 25000, 'Cà phê', True),
            ('Cà phê sữa đá', 'Cà phê sữa đá thơm béo', 30000, 'Cà phê', True),
            ('Bạc xỉu', 'Cà phê ít, sữa nhiều - thơm ngọt', 32000, 'Cà phê', True),
            ('Cappuccino', 'Espresso với sữa nóng và foam mịn', 45000, 'Cà phê', True),
            ('Latte', 'Espresso với sữa tươi nóng', 45000, 'Cà phê', True),
            ('Americano', 'Espresso pha loãng với nước nóng', 40000, 'Cà phê', True),
            ('Trà đào cam sả', 'Trà đào thơm mát với cam và sả', 35000, 'Trà', True),
            ('Trà sen vàng', 'Trà hoa sen thanh mát', 30000, 'Trà', True),
            ('Cacao nóng', 'Cacao nóng thơm béo với sữa', 35000, 'Cacao', True),
            ('Cacao đá xay', 'Cacao đá xay mát lạnh', 40000, 'Cacao', True),
            ('Sinh tố bơ', 'Sinh tố bơ béo ngậy', 40000, 'Sinh tố', True),
            ('Nước dừa tươi', 'Nước dừa tươi nguyên chất', 25000, 'Nước ép', True),
        ]

        for name, desc, price, category, available in products:
            cur.execute("SELECT id FROM products WHERE name = %s", (name,))
            if not cur.fetchone():
                cur.execute(
                    "INSERT INTO products (name, description, price, category, is_available) VALUES (%s, %s, %s, %s, %s)",
                    (name, desc, price, category, available)
                )
                print(f"    + Added product: {name} - {price:,.0f} VNĐ")
            else:
                print(f"    - Product '{name}' already exists, skipped.")

        mysql.connection.commit()

        # ------------------------------------------
        # 4. SEED ORDERS - Đơn hàng mẫu
        # ------------------------------------------
        print("[*] Seeding orders...")

        # Lấy user_id của admin
        cur.execute("SELECT id FROM users WHERE username = 'admin'")
        admin = cur.fetchone()
        admin_id = admin['id'] if admin else 1

        # Lấy user_id của staff1
        cur.execute("SELECT id FROM users WHERE username = 'staff1'")
        staff1 = cur.fetchone()
        staff1_id = staff1['id'] if staff1 else 2

        orders = [
            ('Nguyễn Văn A', '0901234567', 85000, 'completed', 'Ít đá', admin_id),
            ('Trần Thị B', '0912345678', 70000, 'completed', '', staff1_id),
            ('Lê Văn C', '0923456789', 45000, 'processing', 'Thêm đường', staff1_id),
            ('Phạm Thị D', '0934567890', 120000, 'pending', 'Mang đi', admin_id),
            ('Hoàng Văn E', '0945678901', 55000, 'pending', '', staff1_id),
        ]

        cur.execute("SELECT COUNT(*) as total FROM orders")
        order_count = cur.fetchone()['total']

        if order_count == 0:
            for customer_name, phone, total, status, note, created_by in orders:
                cur.execute(
                    """INSERT INTO orders (customer_name, customer_phone, total_amount, status, note, created_by)
                       VALUES (%s, %s, %s, %s, %s, %s)""",
                    (customer_name, phone, total, status, note, created_by)
                )
                print(f"    + Added order: {customer_name} - {total:,.0f} VNĐ ({status})")

            mysql.connection.commit()

            # ------------------------------------------
            # 5. SEED ORDER_ITEMS - Chi tiết đơn hàng
            # ------------------------------------------
            print("[*] Seeding order items...")

            # Lấy danh sách product IDs
            cur.execute("SELECT id, name, price FROM products ORDER BY id")
            all_products = cur.fetchall()

            # Lấy danh sách order IDs
            cur.execute("SELECT id FROM orders ORDER BY id")
            all_orders = cur.fetchall()

            if all_orders and all_products:
                # Đơn 1: Cà phê sữa đá x2 + Bạc xỉu x1
                order_items_data = [
                    (all_orders[0]['id'], all_products[1]['id'], 2, all_products[1]['price']),  # Cà phê sữa đá x2
                    (all_orders[0]['id'], all_products[2]['id'], 1, all_products[2]['price']),  # Bạc xỉu x1
                    # Đơn 2: Trà đào cam sả x2
                    (all_orders[1]['id'], all_products[6]['id'], 2, all_products[6]['price']),
                    # Đơn 3: Cappuccino x1
                    (all_orders[2]['id'], all_products[3]['id'], 1, all_products[3]['price']),
                    # Đơn 4: Latte x1 + Cacao đá xay x1 + Sinh tố bơ x1
                    (all_orders[3]['id'], all_products[4]['id'], 1, all_products[4]['price']),
                    (all_orders[3]['id'], all_products[9]['id'], 1, all_products[9]['price']),
                    (all_orders[3]['id'], all_products[10]['id'], 1, all_products[10]['price']),
                    # Đơn 5: Cà phê đen đá x1 + Nước dừa tươi x1
                    (all_orders[4]['id'], all_products[0]['id'], 1, all_products[0]['price']),
                    (all_orders[4]['id'], all_products[11]['id'], 1, all_products[11]['price']),
                ]

                for order_id, product_id, qty, unit_price in order_items_data:
                    cur.execute(
                        "INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (%s, %s, %s, %s)",
                        (order_id, product_id, qty, unit_price)
                    )

                mysql.connection.commit()
                print(f"    + Added {len(order_items_data)} order items.")
        else:
            print(f"    - Orders already exist ({order_count} orders), skipped.")

        cur.close()
        print("\n[OK] Seed data completed successfully!")
        print("=" * 50)
        print("Tài khoản đăng nhập:")
        print("  Admin:  username='admin'   password='admin123'")
        print("  Staff:  username='staff1'  password='staff123'")
        print("  Staff:  username='staff2'  password='staff123'")
        print("=" * 50)


if __name__ == '__main__':
    seed()
