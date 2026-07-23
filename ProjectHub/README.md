# Project Management Tool

A complete Full Stack Project Management application similar to Trello or Asana, built with Python Django, Channels (WebSockets), Bootstrap 5, and SQLite. Suitable for a final-year internship project with professional code structure and aesthetics.

---

## 🚀 Features

### 1. User Authentication & Roles
- User registration, login, logout, and password updates.
- Profile management with avatar uploads.
- Role-based Access Control (RBAC) with predefined roles:
  - **Admin**: Full control over users, projects, tasks, and site activity logs.
  - **Project Manager**: Create projects, assign members, write/edit tasks.
  - **Team Member**: View assigned boards, modify card status, add comments/attachments.

### 2. Interactive Dashboard
- Statistics cards on projects and tasks counts.
- Dynamic task completion rate progress indicators.
- Upcoming deadlines (tasks ending in the next 7 days).
- Assigned tasks panel.
- Dynamic **Chart.js** donut graph showing task status distributions.
- Chronological timeline showing global activity logs.

### 3. Project & Member Management
- Create, edit, and delete projects (with description, start/end dates, and status fields).
- Manage project membership rosters (add/remove users).
- Multi-user assignments.
- Export project tasks directly to **CSV** sheets.

### 4. Kanban Board (Drag-and-Drop)
- Boards split into columns: **To Do**, **In Progress**, **Review**, and **Completed**.
- Card drag-and-drop mechanics implemented in modern JavaScript.
- Dynamic priority indicator badges (High, Medium, Low) and progress bars on each card.
- Interactive filtering by Task Priority, Assignee, or title searches.

### 5. Task Details & Attachments
- Two-column detail page layout (metadata sidebar vs text contents).
- Multiple file uploads/attachments supported.
- Threaded task commenting system.
- Mentions support using `@username` in comment text which triggers user notifications.

### 6. Notifications & WebSockets (Real-Time)
- Notifications sent for: Task assignments, task detail edits, comments, and mentions.
- Live notifications bell count badge syncing instantly without page refreshes.
- Pop-up Toast notification messages using WebSockets.
- Real-time Board sync: when another team member moves a card on their screen, the card automatically moves on your screen instantly.
- Real-time comment sync: new comments appear in the thread instantly for all active users.

### 7. Modern UI / UX & Dark Mode
- Collapsible sidebar navigation.
- Smooth transitions.
- Fully responsive layout matching desktop, tablet, and mobile displays.
- Persistent **Dark Mode** toggle stored in browser `localStorage`.

---

## 🛠️ Tech Stack
- **Backend**: Python 3.x, Django 5.x, SQLite
- **Real-Time Integration**: Django Channels 4.x, Daphne ASGI Server (using InMemoryChannelLayer)
- **Frontend**: HTML5, CSS3, JavaScript (ES6+), Bootstrap 5, Bootstrap Icons, Chart.js

---

## 📁 Workspace Structure
```
project_management/
│
├── project_management/      # Django main configurations (settings, routing, urls, asgi)
├── management_app/          # Core Django app (models, views, forms, consumers, migrations)
├── templates/               # HTML template files (base, board, dashboard, login, etc.)
│
├── static/                  # Static assets
│   ├── css/style.css        # Premium custom CSS styling
│   └── js/main.js           # AJAX operations, drag-and-drop, WebSocket handles
│
├── media/                   # User uploads (profile pics, task attachments)
├── db.sqlite3               # SQLite Database file
├── requirements.txt         # Project package dependencies
├── populate_sample_data.py  # Python population script
├── manage.py                # Django manager execution file
└── README.md                # System documentation
```

---

## 💻 Installation & Setup

Follow these steps to run the project locally:

### 1. Setup Virtual Environment
Run in your workspace directory:
```powershell
python -m venv venv
```
Activate the environment:
* **Windows (PowerShell)**: `.\venv\Scripts\Activate.ps1`
* **Windows (CMD)**: `.\venv\Scripts\activate.bat`
* **macOS / Linux**: `source venv/bin/activate`

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Database Migrations
Create database schemas:
```bash
python manage.py migrate
```

### 4. Create Superuser (Admin)
To register an administrative account:
```bash
python manage.py createsuperuser
```

### 5. Populate Sample Data
Run the custom sample data script to fill the database with users, projects, tasks, comments, and logs:
```bash
python populate_sample_data.py
```

### 6. Run Server
Start the development server (runs automatically using Daphne ASGI for WebSockets):
```bash
python manage.py runserver
```
Open **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)** in your browser.

---

## 🔑 Test Accounts
If you ran the `populate_sample_data.py` script, you can log in with these pre-configured credentials:

| Username | Password | Role | Full Name |
| :--- | :--- | :--- | :--- |
| **admin** | `adminpassword` | Admin | System Administrator |
| **manager** | `managerpassword` | Project Manager | Alice Manager |
| **dev1** | `dev1password` | Team Member | Bob Developer |
| **dev2** | `dev2password` | Team Member | Charlie Tester |

---

## 🧪 Testing Guidelines
1. **Real-time Drag-and-Drop**: Log in as `manager` in one browser window (e.g. Chrome) and `dev1` in an incognito window. Open the **Alpha Project Board**. Drag a task card from `To Do` to `In Progress`. Observe the card move instantly on the other user's screen without page reloading.
2. **Comment Synced Thread**: Click on **Implement Drag-and-Drop Board View** card from either user. Type a comment mentioning the other user: `Hello @dev1!`. Press post. It appears instantly on both screens, and a toast message/bell badge is updated for `dev1` in real-time.
3. **Dark Mode**: Click the Moon icon in the top right navbar to swap styles globally. Ensure it remains active after clicking links and page reloads.
