# 🛍️ Shara Store — Simple E-Commerce Store

A full-stack e-commerce web application built with **Python Django**, featuring a modern purple-themed UI, user authentication, product catalog, shopping cart, and order processing.

---

## ✨ Features

### 🔐 User Authentication
- User Registration with password validation
- User Login / Logout
- Session management
- Protected routes (cart & checkout require login)

### 🏠 Home Page
- Display all available products in a responsive grid
- Product cards with image, name, price, category, and short description
- **Search bar** to filter products by name or description
- **Category filter** buttons to browse by category
- Responsive navigation bar

### 📦 Product Details Page
- Large product image
- Product name, price, and full description
- Stock availability indicator
- Quantity selector
- Add to Cart button

### 🛒 Shopping Cart
- Add products to cart
- Remove products from cart
- Update item quantities
- Display subtotal per item and total amount
- Continue Shopping & Checkout buttons

### 📋 Order Processing
- Checkout page with order summary
- Shipping address form
- Place Order button
- Orders stored in the database
- Order confirmation page with order details

### ⚙️ Admin Panel
- Django Admin at `/admin/`
- Add / Edit / Delete products and categories
- Manage users and orders
- View customer information and order history

---

## 🗂️ Folder Structure

```
secommerce/
│
├── ecommerce/              # Django project settings
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── store/                  # Main application
│   ├── __init__.py
│   ├── admin.py            # Admin panel configuration
│   ├── apps.py
│   ├── models.py           # Database models
│   ├── urls.py             # URL routing
│   ├── views.py            # View logic
│   ├── migrations/
│   └── tests.py
│
├── templates/              # HTML templates
│   ├── base.html           # Base layout (navbar + footer)
│   ├── home.html           # Product listing page
│   ├── product_detail.html # Single product view
│   ├── cart.html            # Shopping cart
│   ├── checkout.html        # Checkout page
│   ├── login.html           # Login form
│   ├── register.html        # Registration form
│   └── order_success.html   # Order confirmation
│
├── static/                 # Static assets
│   ├── css/
│   │   └── index.css       # Purple theme stylesheet
│   ├── js/
│   └── images/
│
├── media/                  # Uploaded product images
│   └── products/
│
├── venv/                   # Python virtual environment
├── db.sqlite3              # SQLite database
├── manage.py               # Django management script
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

---

## 🗄️ Database Models

| Model       | Description                                      |
|-------------|--------------------------------------------------|
| **User**    | Django's built-in User model                     |
| **Category**| Product categories (name, slug)                  |
| **Product** | Products (name, category, price, description, image, stock, created date) |
| **Cart**    | One-to-one with User                             |
| **CartItem**| Items in a cart (product, quantity)               |
| **Order**   | Placed orders (user, total, address, status, date)|
| **OrderItem**| Items in an order (product, quantity, price)     |

---

## 🛠️ Tech Stack

| Layer     | Technology              |
|-----------|-------------------------|
| Frontend  | HTML5, CSS3, JavaScript |
| Backend   | Python 3, Django 6.0    |
| Database  | SQLite (default)        |
| Imaging   | Pillow                  |

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)

### Step-by-step

```bash
# 1. Clone or navigate to the project directory
cd secommerce

# 2. Create a virtual environment
python3 -m venv venv

# 3. Activate the virtual environment
source venv/bin/activate        # Linux / macOS
# venv\Scripts\activate         # Windows

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run database migrations
python manage.py makemigrations
python manage.py migrate

# 6. Create a superuser (admin account)
python manage.py createsuperuser

# 7. Start the development server
python manage.py runserver
```

### Access the application

| URL                                  | Description           |
|--------------------------------------|-----------------------|
| http://127.0.0.1:8000/              | Home page (store)     |
| http://127.0.0.1:8000/admin/        | Django Admin panel    |
| http://127.0.0.1:8000/login/        | User login            |
| http://127.0.0.1:8000/register/     | User registration     |
| http://127.0.0.1:8000/cart/         | Shopping cart          |
| http://127.0.0.1:8000/checkout/     | Checkout page         |

---

## 📝 Testing Checklist

1. ✅ Register a new user account
2. ✅ Login with the new account
3. ✅ Browse products on the home page
4. ✅ Filter products by category
5. ✅ Search for a product
6. ✅ View product details
7. ✅ Add a product to the cart
8. ✅ Update quantity in the cart
9. ✅ Remove an item from the cart
10. ✅ Proceed to checkout
11. ✅ Enter shipping address and place order
12. ✅ View order confirmation page
13. ✅ Login to admin panel and manage products/orders
14. ✅ Logout

---

## 🎨 UI Design

- **Theme:** Modern purple color palette (`#6d28d9`)
- **Typography:** Inter (Google Fonts)
- **Layout:** Responsive CSS Grid & Flexbox
- **Interactions:** Hover effects, card shadows, smooth transitions
- **Compatible:** Desktop & mobile responsive

---

## 👤 Default Admin Credentials

> **Username:** `admin`  
> **Password:** `admin`

⚠️ *Change these credentials before deploying to production.*

---

## 📄 License

This project is for educational purposes.
