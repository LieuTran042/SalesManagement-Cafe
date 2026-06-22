# ==========================================
# File: routes/auth.py
# Mô tả: Module xử lý đăng nhập và đăng ký tài khoản
# ==========================================

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from functools import wraps

# Tạo Blueprint cho module auth (xác thực)
auth_bp = Blueprint('auth', __name__)


def get_mysql():
    """Lấy đối tượng mysql từ app context."""
    from flask import current_app
    return current_app.extensions['mysql']


# ==========================================
# ĐĂNG KÝ TÀI KHOẢN
# ==========================================
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Xử lý đăng ký tài khoản mới.
    - GET: Hiển thị form đăng ký
    - POST: Xử lý dữ liệu form và tạo tài khoản
    """
    if request.method == 'POST':
        # Lấy dữ liệu từ form
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # --- Validate dữ liệu ---
        # Kiểm tra các trường không được để trống
        if not username or not email or not password:
            flash('Vui lòng điền đầy đủ thông tin!', 'danger')
            return redirect(url_for('auth.register'))

        # Kiểm tra mật khẩu xác nhận
        if password != confirm_password:
            flash('Mật khẩu xác nhận không khớp!', 'danger')
            return redirect(url_for('auth.register'))

        # Kiểm tra độ dài mật khẩu
        if len(password) < 6:
            flash('Mật khẩu phải có ít nhất 6 ký tự!', 'danger')
            return redirect(url_for('auth.register'))

        # --- Kiểm tra trùng lặp trong database ---
        mysql = get_mysql()
        cur = mysql.connection.cursor()

        # Kiểm tra username đã tồn tại chưa
        cur.execute("SELECT id FROM users WHERE username = %s", (username,))
        if cur.fetchone():
            flash('Tên đăng nhập đã tồn tại!', 'danger')
            cur.close()
            return redirect(url_for('auth.register'))

        # Kiểm tra email đã tồn tại chưa
        cur.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cur.fetchone():
            flash('Email đã được sử dụng!', 'danger')
            cur.close()
            return redirect(url_for('auth.register'))

        # --- Tạo tài khoản mới ---
        # Mã hóa mật khẩu bằng werkzeug (bcrypt-like)
        hashed_password = generate_password_hash(password)

        cur.execute(
            "INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)",
            (username, email, hashed_password, 'staff')
        )
        mysql.connection.commit()
        cur.close()

        flash('Đăng ký thành công! Vui lòng đăng nhập.', 'success')
        return redirect(url_for('auth.login'))

    # GET request: hiển thị trang đăng ký
    return render_template('register.html')


# ==========================================
# ĐĂNG NHẬP
# ==========================================
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Xử lý đăng nhập.
    - GET: Hiển thị form đăng nhập
    - POST: Xác thực tài khoản và tạo session
    """
    if request.method == 'POST':
        # Lấy dữ liệu từ form
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        # Kiểm tra dữ liệu không rỗng
        if not username or not password:
            flash('Vui lòng nhập đầy đủ thông tin!', 'danger')
            return redirect(url_for('auth.login'))

        # --- Truy vấn user từ database ---
        mysql = get_mysql()
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()

        # Kiểm tra user tồn tại và mật khẩu đúng
        if user and check_password_hash(user['password'], password):
            # Lưu thông tin user vào session
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']

            flash(f'Chào mừng {user["username"]}!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Tên đăng nhập hoặc mật khẩu không đúng!', 'danger')
            return redirect(url_for('auth.login'))

    # GET request: hiển thị trang đăng nhập
    return render_template('login.html')


# ==========================================
# ĐĂNG XUẤT
# ==========================================
@auth_bp.route('/logout')
def logout():
    """Xóa session và đăng xuất người dùng."""
    session.clear()
    flash('Đã đăng xuất thành công!', 'info')
    return redirect(url_for('auth.login'))


# ==========================================
# DECORATOR: Yêu cầu đăng nhập
# ==========================================
def login_required(f):
    """
    Decorator kiểm tra người dùng đã đăng nhập chưa.
    Nếu chưa đăng nhập -> chuyển hướng về trang login.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Vui lòng đăng nhập để tiếp tục!', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """
    Decorator kiểm tra người dùng có phải admin không.
    Chỉ admin mới được truy cập các chức năng quản lý.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Vui lòng đăng nhập để tiếp tục!', 'warning')
            return redirect(url_for('auth.login'))
        if session.get('role') != 'admin':
            flash('Bạn không có quyền truy cập!', 'danger')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function
