"""
==========================================
File: test_app.py
Mô tả: Full Coffee Shop Management System
        - Login/Register/Logout
        - Ingredients Management (CRUD)
        - Orders Management (Create, Update Status, Delete)

        Modules:
        1. Authentication (Login, Register, Logout)
        2. Ingredients (Cà phê, Sữa, Đường, ...)
        3. Orders (Đơn hàng từ khách)

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

# Bảng USERS: {username: {email, password, role, created_at}}
users_db = {}

# Bảng INGREDIENTS: {ingredient_id: {name, quantity, unit, price, supplier, updated_at}}
ingredients_db = {}
ingredient_id_counter = 1

# Bảng PRODUCTS: {product_id: {name, price, category, description, is_available}}
products_db = {}
product_id_counter = 1

# Bảng ORDERS: {order_id: {customer_name, customer_phone, total_amount, status, items, note, created_by, created_at}}
orders_db = {}
order_id_counter = 1


# ==========================================
# DECORATOR: Yêu cầu đăng nhập
# ==========================================
def login_required(f):
    """Decorator kiểm tra user đã đăng nhập chưa."""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# ==========================================
# HÀM HỖ TRỢ
# ==========================================
def is_valid_email(email):
    """Kiểm tra định dạng email bằng regex."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def mask_password(password):
    """Ẩn password: 2 ký tự đầu + dấu *."""
    if len(password) <= 2:
        return '*' * len(password)
    return password[:2] + '*' * (len(password) - 2)


# ==========================================
# MODULE 1: AUTHENTICATION
# ==========================================

# -------- LOGIN --------
@app.route('/', methods=['GET', 'POST'])
def login():
    """Trang đăng nhập."""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Please enter both username and password.', 'warning')
            return render_template('login.html', username=username,
                remembered_username=username, remembered_password='', remembered=False)

        if username in users_db:
            user_data = users_db[username]
            if user_data['password'] == password:
                session['user_id'] = username
                session['username'] = username
                session['email'] = user_data['email']
                session['role'] = user_data.get('role', 'staff')
                flash(f'Welcome back, {username}!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid password. Please try again.', 'danger')
        else:
            flash(f'Username "{username}" does not exist.', 'danger')

        return render_template('login.html', username=username,
            remembered_username=username, remembered_password='', remembered=False)

    return render_template('login.html', username='',
        remembered_username='', remembered_password='', remembered=False)


# -------- REGISTER --------
@app.route('/register', methods=['GET', 'POST'])
def register():
    """Đăng ký tài khoản mới."""
    global users_db

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not username:
            flash('Username is required.', 'danger')
            return render_template('register.html', username=username, email=email)

        if len(username) < 3 or len(username) > 50:
            flash('Username must be between 3 and 50 characters.', 'danger')
            return render_template('register.html', username=username, email=email)

        if username in users_db:
            flash(f'Username "{username}" is already taken.', 'danger')
            return render_template('register.html', username=username, email=email)

        if not email or not is_valid_email(email):
            flash('Invalid email format.', 'danger')
            return render_template('register.html', username=username, email=email)

        for user_data in users_db.values():
            if user_data['email'] == email:
                flash(f'Email "{email}" is already registered.', 'danger')
                return render_template('register.html', username=username, email=email)

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('register.html', username=username, email=email)

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html', username=username, email=email)

        users_db[username] = {
            'email': email,
            'password': password,
            'role': 'staff',
            'created_at': datetime.now()
        }

        flash(f'Account "{username}" created successfully!', 'success')
        return redirect(url_for('register'))

    return render_template('register.html', username='', email='')


# -------- DASHBOARD --------
@app.route('/dashboard')
@login_required
def dashboard():
    """Trang chủ sau khi đăng nhập."""
    return render_template('dashboard.html',
        username=session.get('username'),
        email=session.get('email'),
        role=session.get('role', 'staff'),
        total_ingredients=len(ingredients_db),
        total_products=len(products_db),
        total_orders=len(orders_db),
        pending_orders=sum(1 for o in orders_db.values() if o['status'] == 'pending'))


# -------- LOGOUT --------
@app.route('/logout')
def logout():
    """Đăng xuất."""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


# -------- VIEW USERS --------
@app.route('/users')
@login_required
def view_users():
    """Hiển thị danh sách users."""
    users_list = []
    for username, data in users_db.items():
        users_list.append({
            'username': username,
            'email': data['email'],
            'masked_password': mask_password(data['password']),
            'role': data.get('role', 'staff'),
            'created_at': data.get('created_at', datetime.now())
        })
    users_list.sort(key=lambda x: x['created_at'], reverse=True)

    latest_time = users_list[0]['created_at'].strftime("%H:%M:%S") if users_list else "—"

    return render_template('users.html', users=users_list, latest_user_time=latest_time)


@app.route('/users/delete/<username>', methods=['POST'])
@login_required
def delete_user(username):
    """Xóa user."""
    if username in users_db:
        del users_db[username]
        flash(f'User "{username}" deleted.', 'success')
    return redirect(url_for('view_users'))


# ==========================================
# MODULE 2: INGREDIENTS (Quản lý nguyên liệu)
# ==========================================

@app.route('/ingredients')
@login_required
def list_ingredients():
    """Danh sách nguyên liệu."""
    ingredients_list = []
    for ing_id, data in ingredients_db.items():
        ingredients_list.append({
            'id': ing_id,
            'name': data['name'],
            'quantity': data['quantity'],
            'unit': data['unit'],
            'price': data['price'],
            'supplier': data.get('supplier', ''),
            'updated_at': data.get('updated_at', datetime.now())
        })
    # Sắp xếp theo tên
    ingredients_list.sort(key=lambda x: x['name'].lower())

    return render_template('ingredients.html', ingredients=ingredients_list)


@app.route('/ingredients/add', methods=['POST'])
@login_required
def add_ingredient():
    """Thêm nguyên liệu mới."""
    global ingredient_id_counter

    name = request.form.get('name', '').strip()
    quantity = request.form.get('quantity', '0')
    unit = request.form.get('unit', '').strip()
    price = request.form.get('price', '0')
    supplier = request.form.get('supplier', '').strip()

    if not name or not unit:
        flash('Name and unit are required.', 'danger')
        return redirect(url_for('list_ingredients'))

    try:
        quantity = float(quantity)
        price = float(price)
        if quantity < 0 or price < 0:
            raise ValueError
    except ValueError:
        flash('Quantity and price must be positive numbers.', 'danger')
        return redirect(url_for('list_ingredients'))

    ingredients_db[ingredient_id_counter] = {
        'name': name,
        'quantity': quantity,
        'unit': unit,
        'price': price,
        'supplier': supplier,
        'updated_at': datetime.now()
    }
    ingredient_id_counter += 1

    flash(f'Ingredient "{name}" added successfully!', 'success')
    return redirect(url_for('list_ingredients'))


@app.route('/ingredients/edit/<int:ing_id>', methods=['POST'])
@login_required
def edit_ingredient(ing_id):
    """Sửa nguyên liệu."""
    if ing_id not in ingredients_db:
        flash('Ingredient not found.', 'danger')
        return redirect(url_for('list_ingredients'))

    name = request.form.get('name', '').strip()
    quantity = request.form.get('quantity', '0')
    unit = request.form.get('unit', '').strip()
    price = request.form.get('price', '0')
    supplier = request.form.get('supplier', '').strip()

    if not name or not unit:
        flash('Name and unit are required.', 'danger')
        return redirect(url_for('list_ingredients'))

    try:
        quantity = float(quantity)
        price = float(price)
    except ValueError:
        flash('Invalid number format.', 'danger')
        return redirect(url_for('list_ingredients'))

    ingredients_db[ing_id].update({
        'name': name,
        'quantity': quantity,
        'unit': unit,
        'price': price,
        'supplier': supplier,
        'updated_at': datetime.now()
    })

    flash(f'Ingredient "{name}" updated successfully!', 'success')
    return redirect(url_for('list_ingredients'))


@app.route('/ingredients/delete/<int:ing_id>', methods=['POST'])
@login_required
def delete_ingredient(ing_id):
    """Xóa nguyên liệu."""
    if ing_id in ingredients_db:
        name = ingredients_db[ing_id]['name']
        del ingredients_db[ing_id]
        flash(f'Ingredient "{name}" deleted.', 'success')
    return redirect(url_for('list_ingredients'))


# ==========================================
# MODULE 3: PRODUCTS (Sản phẩm cà phê)
# ==========================================

@app.route('/products')
@login_required
def list_products():
    """Danh sách sản phẩm."""
    products_list = []
    for prod_id, data in products_db.items():
        products_list.append({
            'id': prod_id,
            'name': data['name'],
            'price': data['price'],
            'category': data.get('category', ''),
            'description': data.get('description', ''),
            'is_available': data.get('is_available', True)
        })
    products_list.sort(key=lambda x: x['name'].lower())
    return render_template('products.html', products=products_list)


@app.route('/products/add', methods=['POST'])
@login_required
def add_product():
    """Thêm sản phẩm mới."""
    global product_id_counter

    name = request.form.get('name', '').strip()
    price = request.form.get('price', '0')
    category = request.form.get('category', '').strip()
    description = request.form.get('description', '').strip()

    if not name:
        flash('Product name is required.', 'danger')
        return redirect(url_for('list_products'))

    try:
        price = float(price)
        if price < 0:
            raise ValueError
    except ValueError:
        flash('Price must be a positive number.', 'danger')
        return redirect(url_for('list_products'))

    products_db[product_id_counter] = {
        'name': name,
        'price': price,
        'category': category,
        'description': description,
        'is_available': True
    }
    product_id_counter += 1

    flash(f'Product "{name}" added successfully!', 'success')
    return redirect(url_for('list_products'))


@app.route('/products/delete/<int:prod_id>', methods=['POST'])
@login_required
def delete_product(prod_id):
    """Xóa sản phẩm."""
    if prod_id in products_db:
        name = products_db[prod_id]['name']
        del products_db[prod_id]
        flash(f'Product "{name}" deleted.', 'success')
    return redirect(url_for('list_products'))


# ==========================================
# MODULE 4: ORDERS (Quản lý đơn hàng)
# ==========================================

@app.route('/orders')
@login_required
def list_orders():
    """Danh sách đơn hàng."""
    status_filter = request.args.get('status', '')

    orders_list = []
    for order_id, data in orders_db.items():
        if not status_filter or data['status'] == status_filter:
            orders_list.append({
                'id': order_id,
                'customer_name': data['customer_name'],
                'customer_phone': data.get('customer_phone', ''),
                'total_amount': data['total_amount'],
                'status': data['status'],
                'note': data.get('note', ''),
                'created_by': data['created_by'],
                'created_at': data['created_at'],
                'item_count': len(data.get('items', []))
            })

    # Sắp xếp theo thời gian (mới nhất trước)
    orders_list.sort(key=lambda x: x['created_at'], reverse=True)

    # Lấy danh sách sản phẩm có sẵn để hiển thị trong form tạo đơn
    available_products = []
    for prod_id, data in products_db.items():
        if data.get('is_available', True):
            available_products.append({
                'id': prod_id,
                'name': data['name'],
                'price': data['price']
            })

    return render_template('orders.html',
        orders=orders_list,
        products=available_products,
        status_filter=status_filter)


@app.route('/orders/create', methods=['POST'])
@login_required
def create_order():
    """Tạo đơn hàng mới."""
    global order_id_counter

    customer_name = request.form.get('customer_name', '').strip()
    customer_phone = request.form.get('customer_phone', '').strip()
    note = request.form.get('note', '').strip()
    product_ids = request.form.getlist('product_ids')
    quantities = request.form.getlist('quantities')

    # -------- VALIDATE 1: Customer Name --------
    if not customer_name:
        flash('Customer name is required.', 'danger')
        return redirect(url_for('list_orders'))

    # -------- VALIDATE 2: Phone (server-side) --------
    # Phone chỉ chấp nhận số 0-9, tổng cộng 10 số
    if customer_phone:
        if not customer_phone.isdigit():
            flash('Phone must contain only numbers (0-9). Letters and special characters are not allowed.', 'danger')
            return redirect(url_for('list_orders'))
        if len(customer_phone) != 10:
            flash('Phone must be exactly 10 digits.', 'danger')
            return redirect(url_for('list_orders'))

    if not product_ids:
        flash('Please select at least one product.', 'danger')
        return redirect(url_for('list_orders'))

    # Tính tổng tiền và danh sách sản phẩm
    total_amount = 0
    order_items = []

    for i, prod_id in enumerate(product_ids):
        try:
            qty = int(quantities[i]) if i < len(quantities) else 1
        except (ValueError, TypeError):
            qty = 1

        if qty <= 0:
            continue

        prod_id = int(prod_id)
        if prod_id in products_db:
            product = products_db[prod_id]
            item_total = product['price'] * qty
            total_amount += item_total
            order_items.append({
                'product_id': prod_id,
                'product_name': product['name'],
                'quantity': qty,
                'unit_price': product['price'],
                'subtotal': item_total
            })

    if not order_items:
        flash('No valid products in order.', 'danger')
        return redirect(url_for('list_orders'))

    # Tạo đơn hàng
    orders_db[order_id_counter] = {
        'customer_name': customer_name,
        'customer_phone': customer_phone,
        'total_amount': total_amount,
        'status': 'pending',
        'note': note,
        'items': order_items,
        'created_by': session.get('username'),
        'created_at': datetime.now()
    }
    order_id_counter += 1

    flash(f'Order #{order_id_counter - 1} created! Total: {total_amount:,.0f} VND', 'success')
    return redirect(url_for('list_orders'))


@app.route('/orders/update-status/<int:order_id>', methods=['POST'])
@login_required
def update_order_status(order_id):
    """Cập nhật trạng thái đơn hàng."""
    new_status = request.form.get('status', '')

    valid_statuses = ['pending', 'processing', 'completed', 'cancelled']
    if new_status not in valid_statuses:
        flash('Invalid status.', 'danger')
        return redirect(url_for('list_orders'))

    if order_id in orders_db:
        orders_db[order_id]['status'] = new_status
        status_msg = {
            'pending': 'Pending',
            'processing': 'Processing',
            'completed': 'Completed',
            'cancelled': 'Cancelled'
        }
        flash(f'Order #{order_id} status: {status_msg[new_status]}', 'success')

    return redirect(url_for('list_orders'))


@app.route('/orders/delete/<int:order_id>', methods=['POST'])
@login_required
def delete_order(order_id):
    """Xóa đơn hàng."""
    if order_id in orders_db:
        if orders_db[order_id]['status'] in ['pending', 'cancelled']:
            del orders_db[order_id]
            flash(f'Order #{order_id} deleted.', 'success')
        else:
            flash('Only pending or cancelled orders can be deleted.', 'warning')
    return redirect(url_for('list_orders'))


# ==========================================
# CHẠY SERVER
# ==========================================
if __name__ == '__main__':
    print("=" * 60)
    print(" COFFEE SHOP MANAGEMENT SYSTEM (Full Version)")
    print("=" * 60)
    print(" Server: http://localhost:5000")
    print(" Modules:")
    print("   [Auth]")
    print("     /                  : Login")
    print("     /register          : Register")
    print("     /logout            : Logout")
    print("     /users             : Users list")
    print("   [Ingredients]")
    print("     /ingredients       : List ingredients")
    print("     /ingredients/add   : Add ingredient")
    print("     /ingredients/edit/<id> : Edit ingredient")
    print("     /ingredients/delete/<id> : Delete ingredient")python
    print("   [Products]")
    print("     /products          : List products")
    print("     /products/add      : Add product")
    print("     /products/delete/<id> : Delete product")
    print("   [Orders]")
    print("     /orders            : List orders")
    print("     /orders/create     : Create order")
    print("     /orders/update-status/<id> : Update status")
    print("     /orders/delete/<id> : Delete order")
    print("=" * 60)
    print(" Data: In-memory (reset on restart)")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=False)