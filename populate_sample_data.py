import os
import django
from datetime import date, timedelta

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_management.settings')
django.setup()

from django.contrib.auth import get_user_model
from management_app.models import Project, Task, Comment, Notification, ActivityLog

CustomUser = get_user_model()

def create_sample_data():
    print("Populating sample data...")
    
    # 1. Create Users
    users_data = [
        {'username': 'manager', 'password': 'managerpassword', 'email': 'manager@example.com', 'role': 'PROJECT_MANAGER', 'full_name': 'Alice Manager'},
        {'username': 'dev1', 'password': 'dev1password', 'email': 'dev1@example.com', 'role': 'TEAM_MEMBER', 'full_name': 'Bob Developer'},
        {'username': 'dev2', 'password': 'dev2password', 'email': 'dev2@example.com', 'role': 'TEAM_MEMBER', 'full_name': 'Charlie Tester'},
    ]
    
    users = {}
    for ud in users_data:
        user, created = CustomUser.objects.get_or_create(
            username=ud['username'],
            defaults={
                'email': ud['email'],
                'role': ud['role'],
                'full_name': ud['full_name']
            }
        )
        if created:
            user.set_password(ud['password'])
            user.save()
            print(f"Created user: {ud['username']}")
        else:
            print(f"User already exists: {ud['username']}")
        users[ud['username']] = user
        
    admin_user = CustomUser.objects.filter(is_superuser=True).first()
    if admin_user:
        users['admin'] = admin_user
    else:
        # Fallback if no superuser was found
        admin_user, _ = CustomUser.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@example.com', 'role': 'ADMIN', 'full_name': 'System Administrator'}
        )
        admin_user.set_password('adminpassword')
        admin_user.save()
        users['admin'] = admin_user

    # 2. Create Projects
    today = date.today()
    
    # Alpha Project
    p_alpha, created_alpha = Project.objects.get_or_create(
        name='Alpha Project',
        defaults={
            'description': 'Main product development run. Includes full stack development, deployment, and QA validation.',
            'created_by': users['admin'],
            'start_date': today,
            'end_date': today + timedelta(days=30),
            'status': 'ACTIVE'
        }
    )
    if created_alpha:
        # Add members
        p_alpha.members.add(users['admin'], users['manager'], users['dev1'], users['dev2'])
        print("Created Project: Alpha Project")
        ActivityLog.objects.create(user=users['admin'], action="Created project 'Alpha Project'")
    else:
        print("Project Alpha already exists")
        
    # Beta Project
    p_beta, created_beta = Project.objects.get_or_create(
        name='Beta Project',
        defaults={
            'description': 'Exploratory pipeline project. Planning system integrations and mobile app wireframing.',
            'created_by': users['manager'],
            'start_date': today + timedelta(days=10),
            'end_date': today + timedelta(days=45),
            'status': 'PLANNING'
        }
    )
    if created_beta:
        p_beta.members.add(users['manager'], users['dev1'])
        print("Created Project: Beta Project")
        ActivityLog.objects.create(user=users['manager'], action="Created project 'Beta Project'")
    else:
        print("Project Beta already exists")

    # 3. Create Tasks in Alpha Project
    tasks_alpha = [
        {
            'title': 'Setup Django Server & Channels',
            'description': 'Configure Django routing, Channels routing, ASGI integration, and setup channel layers.',
            'assigned_user': users['dev1'],
            'priority': 'HIGH',
            'status': 'COMPLETED',
            'due_date': today + timedelta(days=2),
            'labels': 'Backend, Config',
            'progress': 100
        },
        {
            'title': 'Design Database Models & Relations',
            'description': 'Draft model structure for CustomUser, Projects, Tasks, Comments, and Notifications. Apply initial migrations.',
            'assigned_user': users['manager'],
            'priority': 'HIGH',
            'status': 'COMPLETED',
            'due_date': today + timedelta(days=5),
            'labels': 'Database',
            'progress': 100
        },
        {
            'title': 'Implement Drag-and-Drop Board View',
            'description': 'Code HTML5 drag-and-drop mechanics in JS, hook up status updates API, and sync other users using board WebSocket connections.',
            'assigned_user': users['dev1'],
            'priority': 'MEDIUM',
            'status': 'IN_PROGRESS',
            'due_date': today + timedelta(days=10),
            'labels': 'Frontend, WebSockets',
            'progress': 60
        },
        {
            'title': 'Integrate Chart.js Statistics on Detail Pages',
            'description': 'Create priority bar charts and completion progress donut wheels in project and task details.',
            'assigned_user': users['manager'],
            'priority': 'MEDIUM',
            'status': 'REVIEW',
            'due_date': today + timedelta(days=7),
            'labels': 'Frontend, Stats',
            'progress': 85
        },
        {
            'title': 'Perform QA Testing & Build Unit Tests',
            'description': 'Write django tests for permissions verification, comments edit control, and drag status update endpoint validation.',
            'assigned_user': users['dev2'],
            'priority': 'LOW',
            'status': 'TODO',
            'due_date': today + timedelta(days=15),
            'labels': 'QA',
            'progress': 0
        }
    ]

    for td in tasks_alpha:
        task, created = Task.objects.get_or_create(
            project=p_alpha,
            title=td['title'],
            defaults={
                'description': td['description'],
                'assigned_user': td['assigned_user'],
                'priority': td['priority'],
                'status': td['status'],
                'due_date': td['due_date'],
                'labels': td['labels'],
                'progress': td['progress']
            }
        )
        if created:
            print(f"Created task: {td['title']}")
            ActivityLog.objects.create(user=users['admin'], action=f"Created task '{task.title}' in '{p_alpha.name}'")
            if task.assigned_user:
                Notification.objects.create(user=task.assigned_user, message=f"You have been assigned to task '{task.title}' in '{p_alpha.name}'")
        else:
            print(f"Task already exists: {td['title']}")

    # 4. Create Tasks in Beta Project
    task_beta, created_t_beta = Task.objects.get_or_create(
        project=p_beta,
        title='Draft Wireframes & Initial Architecture',
        defaults={
            'description': 'Draft Figma screens and outline dependencies. Set planning timeline.',
            'assigned_user': users['manager'],
            'priority': 'MEDIUM',
            'status': 'TODO',
            'due_date': today + timedelta(days=12),
            'labels': 'Design',
            'progress': 0
        }
    )
    if created_t_beta:
        print("Created task for Beta Project")
        ActivityLog.objects.create(user=users['manager'], action=f"Created task '{task_beta.title}' in '{p_beta.name}'")
        Notification.objects.create(user=users['manager'], message=f"You have been assigned to task '{task_beta.title}' in '{p_beta.name}'")

    # 5. Add Comments to board task
    drag_task = Task.objects.filter(project=p_alpha, title='Implement Drag-and-Drop Board View').first()
    if drag_task:
        c1, _ = Comment.objects.get_or_create(
            task=drag_task,
            user=users['manager'],
            text="Hey @dev1, how is the HTML5 drag and drop interface coming along? Make sure to use the new Bootstrap classes.",
            defaults={'created_date': today - timedelta(days=1)}
        )
        c2, _ = Comment.objects.get_or_create(
            task=drag_task,
            user=users['dev1'],
            text="It is looking good! I am binding the websocket consumer to update cards in real-time, it works without page refresh.",
            defaults={'created_date': today}
        )
        print("Added sample comments on drag and drop task card")

    print("Sample data populated successfully!")

if __name__ == "__main__":
    create_sample_data()
