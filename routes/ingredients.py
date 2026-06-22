# ==========================================
# File: routes/ingredients.py
# Mô tả: Module quản lý nguyên liệu (CRUD)
#         - Xem danh sách nguyên liệu
#         - Thêm nguyên liệu mới
#         - Sửa thông tin nguyên liệu
#         - Xóa nguyên liệu
# ==========================================

from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.auth import login_required

# Tạo Blueprint cho module nguyên liệu
ingredients_bp = Blueprint('ingredients', __name__)


def get_mysql():
    """Lấy đối tượng mysql từ app context."""
    from flask import current_app
    return current_app.extensions['mysql']


# ==========================================
# XEM DANH SÁCH NGUYÊN LIỆU
# ==========================================
@ingredients_bp.route('/ingredients')
@login_required
def list_ingredients():
    """
    Hiển thị danh sách tất cả nguyên liệu.
    Hỗ trợ tìm kiếm theo tên nguyên liệu.
    """
    mysql = get_mysql()
    cur = mysql.connection.cursor()

    # Lấy từ khóa tìm kiếm (nếu có)
    search = request.args.get('search', '').strip()

    if search:
        # Tìm kiếm theo tên nguyên liệu (LIKE %keyword%)
        cur.execute(
            "SELECT * FROM ingredients WHERE name LIKE %s ORDER BY name",
            (f'%{search}%',)
        )
    else:
        # Lấy tất cả nguyên liệu, sắp xếp theo tên
        cur.execute("SELECT * FROM ingredients ORDER BY name")

    ingredients = cur.fetchall()
    cur.close()

    return render_template('ingredients.html', ingredients=ingredients, search=search)


# ==========================================
# THÊM NGUYÊN LIỆU MỚI
# ==========================================
@ingredients_bp.route('/ingredients/add', methods=['POST'])
@login_required
def add_ingredient():
    """
    Thêm một nguyên liệu mới vào kho.
    Dữ liệu nhận từ form POST.
    """
    # Lấy dữ liệu từ form
    name = request.form.get('name', '').strip()
    quantity = request.form.get('quantity', 0)
    unit = request.form.get('unit', '').strip()
    price = request.form.get('price', 0)
    supplier = request.form.get('supplier', '').strip()

    # Validate dữ liệu bắt buộc
    if not name or not unit:
        flash('Tên nguyên liệu và đơn vị không được để trống!', 'danger')
        return redirect(url_for('ingredients.list_ingredients'))

    # Validate số lượng và giá phải >= 0
    try:
        quantity = float(quantity)
        price = float(price)
        if quantity < 0 or price < 0:
            raise ValueError
    except (ValueError, TypeError):
        flash('Số lượng và giá phải là số không âm!', 'danger')
        return redirect(url_for('ingredients.list_ingredients'))

    # Thêm vào database
    mysql = get_mysql()
    cur = mysql.connection.cursor()
    cur.execute(
        """INSERT INTO ingredients (name, quantity, unit, price, supplier)
           VALUES (%s, %s, %s, %s, %s)""",
        (name, quantity, unit, price, supplier)
    )
    mysql.connection.commit()
    cur.close()

    flash(f'Đã thêm nguyên liệu "{name}" thành công!', 'success')
    return redirect(url_for('ingredients.list_ingredients'))


# ==========================================
# SỬA THÔNG TIN NGUYÊN LIỆU
# ==========================================
@ingredients_bp.route('/ingredients/edit/<int:id>', methods=['POST'])
@login_required
def edit_ingredient(id):
    """
    Cập nhật thông tin nguyên liệu theo ID.

    Args:
        id (int): ID của nguyên liệu cần sửa
    """
    # Lấy dữ liệu từ form
    name = request.form.get('name', '').strip()
    quantity = request.form.get('quantity', 0)
    unit = request.form.get('unit', '').strip()
    price = request.form.get('price', 0)
    supplier = request.form.get('supplier', '').strip()

    # Validate dữ liệu
    if not name or not unit:
        flash('Tên nguyên liệu và đơn vị không được để trống!', 'danger')
        return redirect(url_for('ingredients.list_ingredients'))

    try:
        quantity = float(quantity)
        price = float(price)
        if quantity < 0 or price < 0:
            raise ValueError
    except (ValueError, TypeError):
        flash('Số lượng và giá phải là số không âm!', 'danger')
        return redirect(url_for('ingredients.list_ingredients'))

    # Cập nhật trong database
    mysql = get_mysql()
    cur = mysql.connection.cursor()
    cur.execute(
        """UPDATE ingredients
           SET name = %s, quantity = %s, unit = %s, price = %s, supplier = %s
           WHERE id = %s""",
        (name, quantity, unit, price, supplier, id)
    )
    mysql.connection.commit()
    cur.close()

    flash(f'Đã cập nhật nguyên liệu "{name}" thành công!', 'success')
    return redirect(url_for('ingredients.list_ingredients'))


# ==========================================
# XÓA NGUYÊN LIỆU
# ==========================================
@ingredients_bp.route('/ingredients/delete/<int:id>', methods=['POST'])
@login_required
def delete_ingredient(id):
    """
    Xóa nguyên liệu theo ID.

    Args:
        id (int): ID của nguyên liệu cần xóa
    """
    mysql = get_mysql()
    cur = mysql.connection.cursor()

    # Lấy tên nguyên liệu trước khi xóa (để hiển thị thông báo)
    cur.execute("SELECT name FROM ingredients WHERE id = %s", (id,))
    ingredient = cur.fetchone()

    if not ingredient:
        flash('Không tìm thấy nguyên liệu!', 'danger')
        cur.close()
        return redirect(url_for('ingredients.list_ingredients'))

    # Xóa nguyên liệu
    cur.execute("DELETE FROM ingredients WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()

    flash(f'Đã xóa nguyên liệu "{ingredient["name"]}" thành công!', 'success')
    return redirect(url_for('ingredients.list_ingredients'))
