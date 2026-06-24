# ==========================================
# File: routes/orders.py
# Mô tả: Module quản lý đơn hàng
#         - Xem danh sách đơn hàng
#         - Tạo đơn hàng mới
#         - Cập nhật trạng thái đơn hàng
#         - Xem chi tiết đơn hàng
#         - Hủy đơn hàng
# ==========================================

from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from routes.auth import login_required

# Tạo Blueprint cho module đơn hàng
orders_bp = Blueprint('orders', __name__)


def get_mysql():
    """Lấy đối tượng mysql từ app context."""
    from flask import current_app
    return current_app.extensions['mysql']


# ==========================================
# XEM DANH SÁCH ĐƠN HÀNG
# ==========================================
@orders_bp.route('/orders')
@login_required
def list_orders():
    """
    Hiển thị danh sách đơn hàng.
    Hỗ trợ lọc theo trạng thái.
    """
    mysql = get_mysql()
    cur = mysql.connection.cursor()

    # Lấy bộ lọc trạng thái (nếu có)
    status_filter = request.args.get('status', '').strip()

    if status_filter:
        # Lọc đơn hàng theo trạng thái
        cur.execute(
            """SELECT o.*, u.username as staff_name
               FROM orders o
               LEFT JOIN users u ON o.created_by = u.id
               WHERE o.status = %s
               ORDER BY o.created_at DESC""",
            (status_filter,)
        )
    else:
        # Lấy tất cả đơn hàng, mới nhất trước
        cur.execute(
            """SELECT o.*, u.username as staff_name
               FROM orders o
               LEFT JOIN users u ON o.created_by = u.id
               ORDER BY o.created_at DESC"""
        )

    orders = cur.fetchall()

    # Lấy danh sách sản phẩm để hiển thị trong form tạo đơn
    cur.execute("SELECT * FROM products WHERE is_available = TRUE ORDER BY name")
    products = cur.fetchall()

    cur.close()

    return render_template('orders.html', orders=orders, products=products, status_filter=status_filter)


# ==========================================
# TẠO ĐƠN HÀNG MỚI
# ==========================================
@orders_bp.route('/orders/create', methods=['POST'])
@login_required
def create_order():
    """
    Tạo đơn hàng mới.
    Nhận thông tin khách hàng và danh sách sản phẩm từ form.
    """
    # Lấy thông tin khách hàng
    customer_name = request.form.get('customer_name', '').strip()
    customer_phone = request.form.get('customer_phone', '').strip()
    note = request.form.get('note', '').strip()

    # Lấy danh sách sản phẩm đã chọn
    product_ids = request.form.getlist('product_ids')       # Danh sách ID sản phẩm
    quantities = request.form.getlist('quantities')         # Số lượng tương ứng

    # --- Validate dữ liệu ---
    if not customer_name:
        flash('Tên khách hàng không được để trống!', 'danger')
        return redirect(url_for('orders.list_orders'))

    if not product_ids:
        flash('Vui lòng chọn ít nhất một sản phẩm!', 'danger')
        return redirect(url_for('orders.list_orders'))

    mysql = get_mysql()
    cur = mysql.connection.cursor()

    # --- Tính tổng tiền đơn hàng ---
    total_amount = 0
    order_items = []  # Lưu tạm chi tiết đơn hàng

    for i, product_id in enumerate(product_ids):
        # Lấy số lượng, mặc định là 1
        qty = int(quantities[i]) if i < len(quantities) and quantities[i] else 1

        if qty <= 0:
            continue  # Bỏ qua sản phẩm có số lượng <= 0

        # Lấy giá sản phẩm từ database
        cur.execute("SELECT id, name, price FROM products WHERE id = %s", (product_id,))
        product = cur.fetchone()

        if product:
            item_total = product['price'] * qty
            total_amount += item_total
            order_items.append({
                'product_id': product['id'],
                'quantity': qty,
                'unit_price': product['price']
            })

    if not order_items:
        flash('Không có sản phẩm hợp lệ trong đơn hàng!', 'danger')
        cur.close()
        return redirect(url_for('orders.list_orders'))

    # --- Tạo đơn hàng ---
    cur.execute(
        """INSERT INTO orders (customer_name, customer_phone, total_amount, note, created_by)
           VALUES (%s, %s, %s, %s, %s)""",
        (customer_name, customer_phone, total_amount, note, session['user_id'])
    )
    mysql.connection.commit()

    # Lấy ID đơn hàng vừa tạo
    order_id = cur.lastrowid

    # --- Thêm chi tiết đơn hàng ---
    for item in order_items:
        cur.execute(
            """INSERT INTO order_items (order_id, product_id, quantity, unit_price)
               VALUES (%s, %s, %s, %s)""",
            (order_id, item['product_id'], item['quantity'], item['unit_price'])
        )

    mysql.connection.commit()
    cur.close()

    flash(f'Đã tạo đơn hàng #{order_id} thành công! Tổng: {total_amount:,.0f} VNĐ', 'success')
    return redirect(url_for('orders.list_orders'))


# ==========================================
# XEM CHI TIẾT ĐƠN HÀNG
# ==========================================
@orders_bp.route('/orders/<int:id>')
@login_required
def order_detail(id):
    """
    Xem chi tiết một đơn hàng.

    Args:
        id (int): ID của đơn hàng
    """
    mysql = get_mysql()
    cur = mysql.connection.cursor()

    # Lấy thông tin đơn hàng
    cur.execute(
        """SELECT o.*, u.username as staff_name
           FROM orders o
           LEFT JOIN users u ON o.created_by = u.id
           WHERE o.id = %s""",
        (id,)
    )
    order = cur.fetchone()

    if not order:
        flash('Không tìm thấy đơn hàng!', 'danger')
        cur.close()
        return redirect(url_for('orders.list_orders'))

    # Lấy chi tiết các sản phẩm trong đơn
    cur.execute(
        """SELECT oi.*, p.name as product_name
           FROM order_items oi
           JOIN products p ON oi.product_id = p.id
           WHERE oi.order_id = %s""",
        (id,)
    )
    items = cur.fetchall()
    cur.close()

    return render_template('order_detail.html', order=order, items=items)


# ==========================================
# CẬP NHẬT TRẠNG THÁI ĐƠN HÀNG
# ==========================================
@orders_bp.route('/orders/update-status/<int:id>', methods=['POST'])
@login_required
def update_order_status(id):
    """
    Cập nhật trạng thái đơn hàng.
    Các trạng thái: pending -> processing -> completed / cancelled

    Args:
        id (int): ID của đơn hàng
    """
    new_status = request.form.get('status', '').strip()

    # Kiểm tra trạng thái hợp lệ
    valid_statuses = ['pending', 'processing', 'completed', 'cancelled']
    if new_status not in valid_statuses:
        flash('Trạng thái không hợp lệ!', 'danger')
        return redirect(url_for('orders.list_orders'))

    mysql = get_mysql()
    cur = mysql.connection.cursor()

    # Cập nhật trạng thái
    cur.execute(
        "UPDATE orders SET status = %s WHERE id = %s",
        (new_status, id)
    )
    mysql.connection.commit()
    cur.close()

    # Thông báo tiếng Việt cho từng trạng thái
    status_messages = {
        'pending': 'Chờ xử lý',
        'processing': 'Đang pha chế',
        'completed': 'Hoàn thành',
        'cancelled': 'Đã hủy'
    }

    flash(f'Đơn hàng #{id} đã chuyển sang: {status_messages[new_status]}', 'success')
    return redirect(url_for('orders.list_orders'))


# ==========================================
# XÓA ĐƠN HÀNG
# ==========================================
@orders_bp.route('/orders/delete/<int:id>', methods=['POST'])
@login_required
def delete_order(id):
    """
    Xóa đơn hàng (chỉ xóa đơn đã hủy hoặc chờ xử lý).

    Args:
        id (int): ID của đơn hàng cần xóa
    """
    mysql = get_mysql()
    cur = mysql.connection.cursor()

    # Kiểm tra đơn hàng tồn tại và trạng thái cho phép xóa
    cur.execute("SELECT status FROM orders WHERE id = %s", (id,))
    order = cur.fetchone()

    if not order:
        flash('Không tìm thấy đơn hàng!', 'danger')
        cur.close()
        return redirect(url_for('orders.list_orders'))

    # Chỉ cho phép xóa đơn chờ xử lý hoặc đã hủy
    if order['status'] not in ('pending', 'cancelled'):
        flash('Chỉ có thể xóa đơn hàng đang chờ hoặc đã hủy!', 'warning')
        cur.close()
        return redirect(url_for('orders.list_orders'))

    # Xóa đơn hàng (order_items sẽ tự xóa nhờ ON DELETE CASCADE)
    cur.execute("DELETE FROM orders WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()

    flash(f'Đã xóa đơn hàng #{id} thành công!', 'success')
    return redirect(url_for('orders.list_orders'))
