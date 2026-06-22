# ==========================================
# File: models/database.py
# Mô tả: Khởi tạo database và các bảng cần thiết
# ==========================================


def init_database(mysql):
    """
    Tạo các bảng trong database nếu chưa tồn tại.

    Các bảng:
    - users: Lưu thông tin người dùng (đăng nhập/đăng ký)
    - ingredients: Lưu thông tin nguyên liệu (cà phê, sữa, đường,...)
    - products: Lưu thông tin sản phẩm (các loại cà phê bán)
    - orders: Lưu thông tin đơn hàng
    - order_items: Lưu chi tiết từng sản phẩm trong đơn hàng
    """
    cur = mysql.connection.cursor()

    # ------------------------------------------
    # Bảng USERS - Quản lý tài khoản người dùng
    # ------------------------------------------
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,           -- ID tự tăng
            username VARCHAR(50) UNIQUE NOT NULL,        -- Tên đăng nhập (duy nhất)
            email VARCHAR(100) UNIQUE NOT NULL,          -- Email (duy nhất)
            password VARCHAR(255) NOT NULL,              -- Mật khẩu đã mã hóa
            role ENUM('admin', 'staff') DEFAULT 'staff', -- Vai trò: admin hoặc nhân viên
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Ngày tạo tài khoản
        )
    ''')

    # ------------------------------------------
    # Bảng INGREDIENTS - Quản lý nguyên liệu
    # ------------------------------------------
    cur.execute('''
        CREATE TABLE IF NOT EXISTS ingredients (
            id INT AUTO_INCREMENT PRIMARY KEY,           -- ID tự tăng
            name VARCHAR(100) NOT NULL,                  -- Tên nguyên liệu
            quantity DECIMAL(10,2) DEFAULT 0,            -- Số lượng tồn kho
            unit VARCHAR(20) NOT NULL,                   -- Đơn vị (kg, lít, gói,...)
            price DECIMAL(10,2) DEFAULT 0,              -- Giá nhập (VNĐ)
            supplier VARCHAR(100),                       -- Nhà cung cấp
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP  -- Ngày cập nhật
        )
    ''')

    # ------------------------------------------
    # Bảng PRODUCTS - Sản phẩm cà phê bán ra
    # ------------------------------------------
    cur.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INT AUTO_INCREMENT PRIMARY KEY,           -- ID tự tăng
            name VARCHAR(100) NOT NULL,                  -- Tên sản phẩm (VD: Cà phê sữa đá)
            description TEXT,                            -- Mô tả sản phẩm
            price DECIMAL(10,2) NOT NULL,                -- Giá bán (VNĐ)
            category VARCHAR(50),                        -- Danh mục (cà phê, trà, sinh tố,...)
            is_available BOOLEAN DEFAULT TRUE,           -- Còn bán hay không
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Ngày tạo
        )
    ''')

    # ------------------------------------------
    # Bảng ORDERS - Đơn hàng
    # ------------------------------------------
    cur.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INT AUTO_INCREMENT PRIMARY KEY,           -- ID đơn hàng
            customer_name VARCHAR(100) NOT NULL,         -- Tên khách hàng
            customer_phone VARCHAR(15),                  -- Số điện thoại khách
            total_amount DECIMAL(10,2) DEFAULT 0,       -- Tổng tiền đơn hàng
            status ENUM('pending', 'processing', 'completed', 'cancelled')
                DEFAULT 'pending',                      -- Trạng thái đơn hàng
            note TEXT,                                   -- Ghi chú đơn hàng
            created_by INT,                             -- Nhân viên tạo đơn
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Ngày tạo đơn
            FOREIGN KEY (created_by) REFERENCES users(id)    -- Khóa ngoại tới bảng users
        )
    ''')

    # ------------------------------------------
    # Bảng ORDER_ITEMS - Chi tiết đơn hàng
    # ------------------------------------------
    cur.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            id INT AUTO_INCREMENT PRIMARY KEY,           -- ID chi tiết
            order_id INT NOT NULL,                       -- ID đơn hàng
            product_id INT NOT NULL,                     -- ID sản phẩm
            quantity INT DEFAULT 1,                      -- Số lượng
            unit_price DECIMAL(10,2) NOT NULL,           -- Đơn giá tại thời điểm đặt
            FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,   -- Xóa đơn -> xóa chi tiết
            FOREIGN KEY (product_id) REFERENCES products(id)                  -- Khóa ngoại tới sản phẩm
        )
    ''')

    # Lưu thay đổi vào database
    mysql.connection.commit()
    cur.close()
    print("[OK] Đã khởi tạo database thành công!")
