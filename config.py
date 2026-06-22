# ==========================================
# File: config.py
# Mô tả: Cấu hình ứng dụng Flask và kết nối MySQL
# ==========================================

import os


class Config:
    """Lớp cấu hình chính cho ứng dụng Flask."""

    # Khóa bí mật dùng cho session và CSRF protection
    SECRET_KEY = os.environ.get('SECRET_KEY', 'coffee-shop-secret-key-2024')

    # ==========================================
    # Cấu hình kết nối MySQL
    # ==========================================
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')       # Địa chỉ server MySQL
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')            # Tên user MySQL
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')         # Mật khẩu MySQL
    MYSQL_DB = os.environ.get('MYSQL_DB', 'coffee_shop_db')      # Tên database
    MYSQL_CURSORCLASS = 'DictCursor'                             # Trả kết quả dạng dict
