# ConnectSphere – Modern Social Networking Platform

A full-stack social networking platform built with Python Django, featuring a modern dark-mode UI with glassmorphism design.

## 🚀 Features

- **User Authentication** – Register, login, logout with session-based auth
- **User Profiles** – Profile pictures, bio, follower/following counts
- **News Feed** – View posts from all users, newest first
- **Create Posts** – Share thoughts with optional image uploads
- **Like System** – Like/unlike posts with real-time AJAX updates
- **Comment System** – Add, edit, and delete comments
- **Follow System** – Follow/unfollow users with AJAX toggle
- **User Search** – Search users by username or name
- **Dashboard** – View your posts, liked posts, followers, and following
- **Admin Panel** – Full content management via Django admin
- **Responsive Design** – Mobile-friendly layout with Bootstrap 5

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | HTML5, CSS3, JavaScript, Bootstrap 5 |
| Backend | Python, Django 5.x |
| Database | SQLite |
| Image Handling | Pillow |
| Icons | Bootstrap Icons |
| Font | Inter (Google Fonts) |

## 📁 Project Structure

```
connectsphere/
├── connectsphere/          # Django project settings
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── app/                    # Main application
│   ├── models.py           # Database models
│   ├── views.py            # View functions
│   ├── forms.py            # Django forms
│   ├── urls.py             # URL routing
│   ├── admin.py            # Admin configuration
│   ├── signals.py          # Auto-profile creation
│   └── management/
│       └── commands/
│           └── create_sample_data.py
├── templates/              # HTML templates
├── static/                 # CSS, JS, images
├── media/                  # User uploads
├── manage.py
├── requirements.txt
└── README.md
```

## ⚡ Installation & Setup

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd connectsphere
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 5: Create Superuser (Admin)
```bash
python manage.py createsuperuser
```

### Step 6: Load Sample Data
```bash
python manage.py create_sample_data
```

### Step 7: Start Development Server
```bash
python manage.py runserver
```

Visit http://127.0.0.1:8000 in your browser.

## 👥 Demo Credentials

| Username | Password | Role |
|----------|----------|------|
| emma_design | Connect@123 | Designer |
| alex_tech | Connect@123 | Developer |
| sophia_art | Connect@123 | Artist |
| ryan_dev | Connect@123 | Engineer |

## 🗄️ Database Models

- **Profile** – Extends User with bio, profile picture, date joined
- **Post** – User posts with optional images and captions
- **Comment** – Comments on posts
- **Like** – Like/unlike system with unique constraint
- **Follow** – Follow/unfollow with self-follow prevention

## 📱 Screenshots

> Screenshots can be added after running the application.

## 🔒 Security Features

- CSRF protection on all forms
- Session-based authentication
- Access control (users can only edit/delete their own content)
- Password validation
- Login required for all features

## 📄 License

This project is built for educational purposes.

---

**Built with ❤️ using Django | ConnectSphere © 2026**
