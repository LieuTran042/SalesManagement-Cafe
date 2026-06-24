# ==========================================
# File: routes/auth.py
# Mô tả: Module xử lý đăng nhập, đăng ký và Remember Me
# ==========================================

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from functools import wraps

# Tạo Blueprint cho module auth (xác thực)
auth_bp = Blueprint('auth', __name__)


def get_mysql():
    """Lấy đối tượng mysql từ app context."""
    from flask import current_app
    return current_app.extensions['mysql']


# ==========================================
# HÀM HỖ TRỢ REMEMBER ME
# ==========================================
def set_remember_me(response, username, password):
    """
The user wants me to apply the suggested edit to the original code. The original code is just a comment "Lưu username và password vào cookie với thời hạn 7 ngày." and the suggested edit replaces it with the full implementation.

    Args:
        response: Đối tượng response của Flask
        username: Tên đăng nhập
        password: Mật khẩu (lưu ý: chỉ nên dùng cho demo,
                  production nên mã hóa thêm)
    """
    # Thời hạn cookie: 7 ngày = 7 * 24 * 3600 giây
    expires = datetime.now() + timedelta(days=7)

    # Set cookie 'remember_username'
    response.set_cookie(
        'remember_username',
        username,
        max_age=7 * 24 * 60 * 60,        # 7 ngày (giây)
        expires=expires,
        path='/',
        httponly=True,                    # Không cho JS truy cập (bảo mật)
        samesite='Lax'
    )

    # Set cookie 'remember_password'
    response.set_cookie(
        'remember_password',
        password,
        max_age=7 * 24 * 60 * 60,        # 7 ngày
        expires=expires,
        path='/',
        httponly=True,
        samesite='Lax'
    )

    return response


def clear_remember_me(response):
    """Xóa cookie remember me khi user bỏ tick hoặc đăng xuất."""
    response.delete_cookie('remember_username', path='/')
    response.delete_cookie('remember_password', path='/')
    return response


# ==========================================
# ĐĂNG KÝ TÀI KHOẢN
# ==========================================
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Xử lý đăng ký tài khoản mới.
    """
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # --- Validate dữ liệu ---
        if not username or not email or not password:
            flash('Vui lòng điền đầy đủ thông tin!', 'danger')
            return redirect(url_for('auth.register'))

        if password != confirm_password:
            flash('Mật khẩu xác nhận không khớp!', 'danger')
            return redirect(url_for('auth.register'))

        if len(password) < 6:
            flash('Mật khẩu phải có ít nhất 6 ký tự!', 'danger')
            return redirect(url_for('auth.register'))

        # --- Kiểm tra trùng lặp ---
        mysql = get_mysql()
        cur = mysql.connection.cursor()

        cur.execute("SELECT id FROM users WHERE username = %s", (username,))
        if cur.fetchone():
            flash('Tên đăng nhập đã tồn tại!', 'danger')
            cur.close()
            return redirect(url_for('auth.register'))

        cur.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cur.fetchone():
            flash('Email đã được sử dụng!', 'danger')
            cur.close()
            return redirect(url_for('auth.register'))

        # --- Tạo tài khoản mới ---
        hashed_password = generate_password_hash(password)

        cur.execute(
            "INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)",
            (username, email, hashed_password, 'staff')
        )
        mysql.connection.commit()
        cur.close()

        flash('Đăng ký thành công! Vui lòng đăng nhập.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


# ==========================================
# ĐĂNG NHẬP (có Remember Me)
# ==========================================
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Xử lý đăng nhập.
    - Hỗ trợ Remember Me: lưu cookie username/password trong 7 ngày
    - Tự động điền username/password nếu đã lưu trước đó
    """
    if request.method == 'POST':
        # Lấy dữ liệu từ form
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember')  # 'on' nếu tick, None nếu không

        # Kiểm tra dữ liệu
        if not username or not password:
            flash('Vui lòng nhập đầy đủ thông tin!', 'danger')
            return redirect(url_for('auth.login'))

        # --- Truy vấn user ---
        mysql = get_mysql()
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()

        # --- Xác thực ---
        if user and check_password_hash(user['password'], password):
            # Lưu session
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']

            # Tạo response chuyển hướng
            response = make_response(redirect(url_for('main.dashboard')))

            # Xử lý Remember Me
            if remember == 'on':
                # User tick Remember Me -> Lưu cookie 7 ngày
                set_remember_me(response, username, password)
                flash(f'Chào mừng {username}! Đã lưu đăng nhập trong 7 ngày.', 'success')
            else:
                # Không tick -> Xóa cookie cũ (nếu có)
                clear_remember_me(response)
                flash(f'Chào mừng {username}!', 'success')

            return response
        else:
            flash('Tên đăng nhập hoặc mật khẩu không đúng!', 'danger')
            return redirect(url_for('auth.login'))

    # --- GET: Hiển thị form đăng nhập ---
    # Lấy username/password từ cookie (nếu có Remember Me)
    remembered_username = request.cookies.get('remember_username', '')
    remembered_password = request.cookies.get('remember_password', '')
    remembered = bool(remembered_username)  # Checkbox checked nếu có cookie

    return render_template(
        'login.html',
        remembered_username=remembered_username,
        remembered_password=remembered_password,
        remembered=remembered
    )


# ==========================================
# ĐĂNG XUẤT (xóa cả session và cookie Remember Me)
# ==========================================
@auth_bp.route('/logout')
def logout():
    """Xóa session và cookie remember me."""
    session.clear()

    # Tạo response redirect
    response = make_response(redirect(url_for('auth.login')))

    # Xóa cookie remember me
    clear_remember_me(response)

    flash('Đã đăng xuất thành công!', 'info')
    return response


# ==========================================
# DECORATOR: Yêu cầu đăng nhập
# ==========================================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Vui lòng đăng nhập để tiếp tục!', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
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
