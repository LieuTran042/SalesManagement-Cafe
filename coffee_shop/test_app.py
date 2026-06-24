"""
==========================================
File: test_app.py
Mô tả: Test Flask app - Login, Register, Users Management
        Sử dụng flash messages thay vì inline errors

        Routes:
        - /           : Login
        - /register   : Register new account
        - /dashboard  : Home page (after login)
        - /logout     : Logout
        - /users      : View users list

        Flash Messages:
        - success (xanh): Đăng ký/đăng nhập thành công
        - danger  (đỏ):  Lỗi validation, sai mật khẩu
        - info    (xanh dương): Thông báo chung (logout)
        - warning (vàng): Cảnh báo

        Data: In-memory dictionary (mất khi restart)
==========================================
"""

import re
from datetime import datetime
from flask import Flask, render_template, request, session, redirect, url_for, flash

app = Flask(__name__,
            template_folder='templates',
            static_folder='static')

# BẮT BUỘC phải có secret_key để dùng session và flash
app.secret_key = 'coffee-shop-secret-key-2024'

# ==========================================
# IN-MEMORY DATABASE (mô phỏng MySQL)
# ==========================================
# Cấu trúc: {username: {email, password, role, created_at}}
users_db = {}


# ==========================================
# HÀM VALIDATE EMAIL
# ==========================================
def is_valid_email(email):
    """
    Kiểm tra định dạng email bằng regex.
    Chỉ validate format, KHÔNG gửi email xác thực.
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def mask_password(password):
    """
    Ẩn password: hiện 2 ký tự đầu + dấu * cho phần còn lại.
    VD: "123456" -> "12****"
    """
    if len(password) <= 2:
        return '*' * len(password)
    return password[:2] + '*' * (len(password) - 2)


# ==========================================
# ROUTE: LOGIN (/)
# ==========================================
@app.route('/', methods=['GET', 'POST'])
def login():
    """
    Xử lý đăng nhập.
    - GET: Hiển thị form login
    - POST: Kiểm tra username/password với database
    """
    # Nếu đã đăng nhập rồi -> chuyển đến dashboard
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember')

        # Validate input
        if not username or not password:
            flash('Please enter both username and password.', 'warning')
            return render_template('login.html',
                username=username,
                remembered_username=username,
                remembered_password='',
                remembered=bool(remember))

        # ==========================================
        # KIỂM TRA VỚI DATABASE
        # ==========================================
        if username in users_db:
            user_data = users_db[username]

            # So sánh password
            if user_data['password'] == password:
                # ✅ ĐĂNG NHẬP THÀNH CÔNG
                session['user_id'] = username
                session['username'] = username
                session['email'] = user_data['email']
                session['role'] = user_data.get('role', 'staff')

                print(f"[LOGIN SUCCESS] User '{username}' logged in.")

                # Flash message sẽ hiển thị ở dashboard
                flash(f'Welcome back, {username}!', 'success')
                return redirect(url_for('dashboard'))
            else:
                # ❌ Sai password
                flash('Invalid password. Please try again.', 'danger')
                return render_template('login.html',
                    username=username,
                    remembered_username=username,
                    remembered_password='',
                    remembered=bool(remember))
        else:
            # ❌ Username không tồn tại
            flash(f'Username "{username}" does not exist. Please register first.', 'danger')
            return render_template('login.html',
                username=username,
                remembered_username=username,
                remembered_password='',
                remembered=bool(remember))

    # GET request: hiển thị form rỗng
    return render_template('login.html',
        username='',
        remembered_username='',
        remembered_password='',
        remembered=False)


# ==========================================
# ROUTE: REGISTER (/register)
# ==========================================
@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Đăng ký tài khoản mới.
    Sau khi đăng ký thành công, user được lưu vào database.
    """
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # -------- VALIDATE 1: Username --------
        if not username:
            flash('Username is required.', 'danger')
            return render_template('register.html', username=username, email=email)

        if len(username) < 3 or len(username) > 50:
            flash('Username must be between 3 and 50 characters.', 'danger')
            return render_template('register.html', username=username, email=email)

        if username in users_db:
            flash(f'Username "{username}" is already taken. Please choose another.', 'danger')
            return render_template('register.html', username=username, email=email)

        # -------- VALIDATE 2: Email --------
        if not email:
            flash('Email is required.', 'danger')
            return render_template('register.html', username=username, email=email)

        if not is_valid_email(email):
            flash(f'Invalid email format: "{email}". Example: user@gmail.com', 'danger')
            return render_template('register.html', username=username, email=email)

        # Kiểm tra email đã tồn tại chưa
        for user_data in users_db.values():
            if user_data['email'] == email:
                flash(f'Email "{email}" is already registered.', 'danger')
                return render_template('register.html', username=username, email=email)

        # -------- VALIDATE 3: Password --------
        if not password:
            flash('Password is required.', 'danger')
            return render_template('register.html', username=username, email=email)

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('register.html', username=username, email=email)

        # -------- VALIDATE 4: Confirm Password --------
        if password != confirm_password:
            flash('Passwords do not match. Please re-enter.', 'danger')
            return render_template('register.html', username=username, email=email)

        # ==========================================
        # LƯU USER VÀO DATABASE
        # ==========================================
        users_db[username] = {
            'email': email,
            'password': password,
            'role': 'staff',
            'created_at': datetime.now()
        }

        print(f"[REGISTER SUCCESS] New user '{username}' ({email}) added to database.")
        print(f"[DATABASE] Total users: {len(users_db)}")

        # ✅ Flash success message
        flash(f'Account "{username}" created successfully! You can now sign in.', 'success')
        return redirect(url_for('register'))  # Redirect để flash hiển thị

    # GET: hiển thị form rỗng
    return render_template('register.html', username='', email='')


# ==========================================
# ROUTE: DASHBOARD (/dashboard)
# ==========================================
@app.route('/dashboard')
def dashboard():
    """Trang chủ sau khi đăng nhập thành công."""
    if 'user_id' not in session:
        flash('Please login to access the dashboard.', 'warning')
        return redirect(url_for('login'))

    username = session.get('username')
    email = session.get('email')
    role = session.get('role', 'staff')

    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Dashboard - Coffee Shop</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
        <style>
            body {{
                background: linear-gradient(135deg, #f5f7fa 0%, #FFF8E7 100%);
                min-height: 100vh;
            }}
            .navbar-coffee {{
                background: linear-gradient(90deg, #6F4E37, #4B3621);
            }}
            .welcome-card {{
                border-radius: 15px;
                border: none;
            }}
        </style>
    </head>
    <body>
        <nav class="navbar navbar-dark navbar-coffee shadow-sm">
            <div class="container-fluid">
                <span class="navbar-brand fw-bold">
                    <i class="bi bi-cup-hot-fill"></i> COFFEE SHOP
                </span>
                <div class="d-flex align-items-center">
                    <span class="text-white me-3">
                        <i class="bi bi-person-circle"></i>
                        {username}
                        <span class="badge bg-warning text-dark ms-1">{role}</span>
                    </span>
                    <a href="/logout" class="btn btn-outline-light btn-sm">
                        <i class="bi bi-box-arrow-right"></i> Logout
                    </a>
                </div>
            </div>
        </nav>

        <div class="container mt-5">
            <div class="card welcome-card shadow-lg">
                <div class="card-body p-5 text-center">
                    <i class="bi bi-check-circle-fill text-success" style="font-size: 4rem;"></i>
                    <h1 class="mt-3">Welcome, {username}!</h1>
                    <p class="lead text-muted">You have successfully logged in to Coffee Shop Management System.</p>

                    <div class="row mt-4 g-3">
                        <div class="col-md-4">
                            <div class="card border-0 bg-light">
                                <div class="card-body">
                                    <i class="bi bi-person display-6 text-primary"></i>
                                    <h5 class="mt-2">Username</h5>
                                    <p class="text-muted">{username}</p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="card border-0 bg-light">
                                <div class="card-body">
                                    <i class="bi bi-envelope display-6 text-success"></i>
                                    <h5 class="mt-2">Email</h5>
                                    <p class="text-muted">{email}</p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="card border-0 bg-light">
                                <div class="card-body">
                                    <i class="bi bi-shield-check display-6 text-warning"></i>
                                    <h5 class="mt-2">Role</h5>
                                    <p class="text-muted">{role}</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="mt-4">
                        <a href="/users" class="btn btn-coffee btn-lg" style="background: #6F4E37; color: white;">
                            <i class="bi bi-people"></i> View Users List
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''


# ==========================================
# ROUTE: LOGOUT (/logout)
# ==========================================
@app.route('/logout')
def logout():
    """Đăng xuất - xóa session."""
    username = session.get('username', 'Unknown')
    session.clear()
    print(f"[LOGOUT] User '{username}' logged out.")
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))


# ==========================================
# ROUTE: VIEW USERS (/users)
# ==========================================
@app.route('/users')
def view_users():
    """Hiển thị bảng danh sách users."""
    users_list = []
    for username, data in users_db.items():
        users_list.append({
            'username': username,
            'email': data['email'],
            'masked_password': mask_password(data['password']),
            'created_at': data.get('created_at', datetime.now())
        })

    # Sắp xếp theo thời gian tạo (mới nhất trước)
    users_list.sort(key=lambda x: x['created_at'], reverse=True)

    if users_list:
        latest = users_list[0]['created_at']
        latest_time = latest.strftime("%H:%M:%S")
    else:
        latest_time = "—"

    return render_template('users.html',
        users=users_list,
        latest_user_time=latest_time)


# ==========================================
# ROUTE: DELETE USER
# ==========================================
@app.route('/users/delete/<username>', methods=['POST'])
def delete_user(username):
    """Xóa user theo username."""
    if username in users_db:
        del users_db[username]
        print(f"[DELETE] User '{username}' deleted.")
        flash(f'User "{username}" has been deleted.', 'success')
    else:
        flash(f'User "{username}" not found.', 'danger')
    return redirect(url_for('view_users'))


# ==========================================
# CHẠY SERVER
# ==========================================
if __name__ == '__main__':
    print("=" * 60)
    print(" COFFEE SHOP - Login & Register Test App (with Flash)")
    print("=" * 60)
    print(" Server: http://localhost:5000")
    print(" Routes:")
    print("   - /           : Login")
    print("   - /register   : Register")
    print("   - /dashboard  : Dashboard (after login)")
    print("   - /users      : Users list")
    print("   - /logout     : Logout")
    print("=" * 60)
    print(" Flash Messages enabled:")
    print("   - success (green)  : Welcome, Account created")
    print("   - danger  (red)    : Validation errors")
    print("   - info    (blue)   : Logout notification")
    print("   - warning (yellow) : Login required")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=False)