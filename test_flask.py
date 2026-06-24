"""
==========================================
File: test_flask.py
Mô tả: Test Flask - English version
        Run: python test_flask.py
        Visit: http://localhost:5000
==========================================
"""

from flask import Flask, render_template_string

app = Flask(__name__)

# Home page test
@app.route('/')
def home():
    return render_template_string('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <title>Flask Test</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
        </head>
        <body class="bg-light">
            <div class="container mt-5">
                <div class="card shadow-lg">
                    <div class="card-body p-5 text-center">
                        <i class="bi bi-cup-hot-fill" style="font-size: 4rem; color: #6F4E37;"></i>
                        <h1 class="text-success mt-3">
                            <i class="bi bi-check-circle-fill"></i> Flask is working!
                        </h1>
                        <p class="lead mt-3">If you see this page, Flask has been installed successfully.</p>
                        <hr>
                        <h3>System Information</h3>
                        <p><strong>Python version:</strong> 3.11.9</p>
                        <p><strong>Flask version:</strong> 3.1.1</p>
                        <a href="/login-page" class="btn btn-primary mt-3">
                            <i class="bi bi-box-arrow-in-right"></i> View Login Page Sample
                        </a>
                    </div>
                </div>
            </div>
        </body>
        </html>
    ''')


# Login page sample
@app.route('/login-page')
def login_page():
    return render_template_string('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Login - Coffee Shop</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
            <style>
                body {
                    background: linear-gradient(135deg, #f5f7fa 0%, #FFF8E7 100%);
                    min-height: 100vh;
                }
                .login-card { border-radius: 20px; }
                .coffee-icon { font-size: 4rem; color: #6F4E37; }
                .btn-coffee {
                    background: #6F4E37;
                    color: white;
                    border: none;
                }
                .btn-coffee:hover {
                    background: #4B3621;
                    color: white;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="row justify-content-center">
                    <div class="col-md-5 col-lg-4">
                        <div class="card login-card shadow-lg border-0 mt-5">
                            <div class="card-body p-5">
                                <div class="text-center mb-4">
                                    <i class="bi bi-cup-hot-fill coffee-icon"></i>
                                    <h3 class="fw-bold mt-3">COFFEE SHOP</h3>
                                    <p class="text-muted">Sign in to your account</p>
                                </div>

                                <form method="POST" action="#">
                                    <div class="mb-3">
                                        <label class="form-label">
                                            <i class="bi bi-person"></i> Username
                                        </label>
                                        <input type="text" name="username" class="form-control form-control-lg"
                                               placeholder="Enter your username" required>
                                    </div>

                                    <div class="mb-3">
                                        <label class="form-label">
                                            <i class="bi bi-lock"></i> Password
                                        </label>
                                        <input type="password" name="password" class="form-control form-control-lg"
                                               placeholder="Enter your password" required>
                                    </div>

                                    <div class="form-check mb-4">
                                        <input class="form-check-input" type="checkbox" id="remember">
                                        <label class="form-check-label" for="remember">
                                            Remember me for 7 days
                                        </label>
                                    </div>

                                    <button type="submit" class="btn btn-coffee w-100 btn-lg">
                                        <i class="bi bi-box-arrow-in-right"></i> Sign In
                                    </button>
                                </form>

                                <div class="text-center mt-4">
                                    <small class="text-muted">Don't have an account?</small>
                                    <a href="#" class="text-decoration-none fw-bold"> Sign up</a>
                                </div>
                                <div class="text-center mt-3">
                                    <a href="/" class="text-decoration-none text-muted">← Back to home</a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
    ''')


if __name__ == '__main__':
    print("=" * 50)
    print(" TEST FLASK - Coffee Shop (English)")
    print("=" * 50)
    print(" Server running at: http://localhost:5000")
    print(" Press Ctrl+C to stop")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=False)
