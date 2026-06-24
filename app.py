# ==========================================
# File: app.py
# Mô tả: File chính khởi chạy Flask Server
#         - Khởi tạo Flask app
#         - Kết nối MySQL
#         - Đăng ký các Blueprint (modules)
#         - Định nghĩa các route chính
# ==========================================

from flask import Flask, render_template, redirect, url_for
from flask_mysqldb import MySQL
from config import Config
from models.database import init_database
from routes.auth import auth_bp, login_required
from routes.ingredients import ingredients_bp
from routes.orders import orders_bp

# ==========================================
# KHỞI TẠO FLASK APP
# ==========================================
app = Flask(__name__)

# Load cấu hình từ class Config
app.config.from_object(Config)

# ==========================================
# KHỞI TẠO MySQL
# ==========================================
mysql = MySQL(app)
app.extensions['mysql'] = mysql  # Lưu vào extensions để các module khác dùng

# ==========================================
# ĐĂNG KÝ BLUEPRINT (CÁC MODULE)
# ==========================================
app.register_blueprint(auth_bp)           # Module xác thực (login, register, logout)
app.register_blueprint(ingredients_bp)    # Module quản lý nguyên liệu
app.register_blueprint(orders_bp)         # Module quản lý đơn hàng

# ==========================================
# ROUTE CHÍNH - TRANG CHỦ / DASHBOARD
# ==========================================
@app.route('/')
def home():
    """Trang chủ - chuyển hướng về dashboard nếu đã đăng nhập, ngược lại về login."""
    from flask import session
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))


# Tạo Blueprint cho trang chính (dashboard)
from flask import Blueprint
main_bp = Blueprint('main', __name__)

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Trang dashboard - hiển thị thống kê tổng quan.
    Yêu cầu đăng nhập.
    """
    from flask import session
    cur = mysql.connection.cursor()

    # Thống kê tổng quan
    cur.execute("SELECT COUNT(*) as total FROM ingredients")
    total_ingredients = cur.fetchone()['total']

    cur.execute("SELECT COUNT(*) as total FROM orders")
    total_orders = cur.fetchone()['total']

    cur.execute("SELECT COUNT(*) as total FROM orders WHERE status = 'pending'")
    pending_orders = cur.fetchone()['total']

    cur.execute("SELECT COUNT(*) as total FROM products")
    total_products = cur.fetchone()['total']

    cur.close()

    return render_template('dashboard.html',
                           username=session.get('username'),
                           total_ingredients=total_ingredients,
                           total_orders=total_orders,
                           pending_orders=pending_orders,
                           total_products=total_products)

app.register_blueprint(main_bp)


# ==========================================
# CHẠY ỨNG DỤNG
# ==========================================
if __name__ == '__main__':
    # Khởi tạo database (tạo bảng nếu chưa có)
    with app.app_context():
        init_database(mysql)

    # Chạy Flask server ở chế độ debug
    # - host='0.0.0.0': cho phép truy cập từ máy khác trong mạng
    # - port=5000: cổng chạy
    # - debug=True: tự reload khi code thay đổi
    app.run(host='0.0.0.0', port=5000, debug=True)
