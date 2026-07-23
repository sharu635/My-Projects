import re
import csv
from datetime import date, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Q, Avg
from django.utils import timezone

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import CustomUser, Project, Task, TaskAttachment, Comment, Notification, ActivityLog
from .forms import CustomUserCreationForm, UserProfileForm, ProjectForm, TaskForm, CommentForm

# Helper to send real-time WebSocket updates
def send_ws_update(group_name, message_dict):
    try:
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(group_name, message_dict)
    except Exception as e:
        print(f"WebSocket send error: {e}")

# Helper to create activity logs
def log_activity(user, action):
    ActivityLog.objects.create(user=user, action=action)

# Helper to notify a user
def notify_user(user, message):
    Notification.objects.create(user=user, message=message)
    send_ws_update(f"user_notifications_{user.id}", {
        "type": "send_notification",
        "message": message,
        "unread_count": Notification.objects.filter(user=user, read_status=False).count()
    })

# --- Authentication Views ---

from django.contrib.auth.forms import AuthenticationForm

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            log_activity(user, "Logged in.")
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    if request.user.is_authenticated:
        log_activity(request.user, "Logged out.")
        logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('login')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            log_activity(user, "Registered and logged in.")
            messages.success(request, "Registration successful! Welcome to the Project Management Tool.")
            return redirect('dashboard')
        else:
            messages.error(request, "Failed to register. Please check the details.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

# Profile Management
@login_required
def profile_view(request):
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        password_form = PasswordChangeForm(request.user, request.POST)
        
        # Determine which form is being submitted
        if 'update_profile' in request.POST:
            if profile_form.is_valid():
                profile_form.save()
                log_activity(request.user, "Updated profile information.")
                messages.success(request, "Profile updated successfully.")
                return redirect('profile')
            else:
                messages.error(request, "Error updating profile.")
        elif 'change_password' in request.POST:
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                log_activity(request.user, "Changed password.")
                messages.success(request, "Password updated successfully.")
                return redirect('profile')
            else:
                messages.error(request, "Error changing password. Check details.")
    else:
        profile_form = UserProfileForm(instance=request.user)
        password_form = PasswordChangeForm(request.user)
        
    return render(request, 'profile.html', {
        'profile_form': profile_form,
        'password_form': password_form
    })

# --- Dashboard View ---

@login_required
def dashboard_view(request):
    user = request.user
    
    # Filter projects based on user membership
    user_projects = Project.objects.filter(members=user)
    total_projects = user_projects.count()
    active_projects = user_projects.filter(status='ACTIVE').count()
    completed_projects = user_projects.filter(status='COMPLETED').count()
    
    # Tasks assigned to user
    assigned_tasks = Task.objects.filter(assigned_user=user).order_by('-due_date')
    total_tasks = assigned_tasks.count()
    todo_tasks = assigned_tasks.filter(status='TODO').count()
    in_progress_tasks = assigned_tasks.filter(status='IN_PROGRESS').count()
    review_tasks = assigned_tasks.filter(status='REVIEW').count()
    completed_tasks = assigned_tasks.filter(status='COMPLETED').count()
    
    # Task statistics
    completion_rate = int((completed_tasks / total_tasks * 100)) if total_tasks > 0 else 0
    
    # Upcoming Deadlines
    upcoming_tasks = Task.objects.filter(
        Q(assigned_user=user) | Q(project__members=user),
        due_date__gte=date.today(),
        due_date__lte=date.today() + timedelta(days=7)
    ).exclude(status='COMPLETED').order_by('due_date')[:5]
    
    # Recent activity logs for user's projects
    recent_activities = ActivityLog.objects.filter(
        Q(user=user) | Q(user__in=CustomUser.objects.filter(projects__in=user_projects))
    ).distinct().order_by('-datetime')[:8]
    
    context = {
        'total_projects': total_projects,
        'active_projects': active_projects,
        'completed_projects': completed_projects,
        'total_tasks': total_tasks,
        'todo_tasks': todo_tasks,
        'in_progress_tasks': in_progress_tasks,
        'review_tasks': review_tasks,
        'completed_tasks': completed_tasks,
        'completion_rate': completion_rate,
        'upcoming_tasks': upcoming_tasks,
        'recent_activities': recent_activities,
        'assigned_tasks': assigned_tasks[:5]
    }
    return render(request, 'dashboard.html', context)

# --- Project Management Views ---

@login_required
def projects_list_view(request):
    query = request.GET.get('search', '')
    projects = Project.objects.filter(members=request.user)
    if query:
        projects = projects.filter(name__icontains=query)
    
    # Add stats to projects
    for project in projects:
        total_tasks = project.tasks.count()
        completed_tasks = project.tasks.filter(status='COMPLETED').count()
        project.progress = int((completed_tasks / total_tasks * 100)) if total_tasks > 0 else 0
        
    return render(request, 'projects.html', {'projects': projects, 'search_query': query})

@login_required
def create_project_view(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            project.save()
            form.save_m2m() # Save Many-to-Many members
            
            # Ensure creator is always a member
            project.members.add(request.user)
            log_activity(request.user, f"Created project '{project.name}'")
            messages.success(request, "Project created successfully!")
            return redirect('project_detail', project_id=project.id)
    else:
        form = ProjectForm()
    return render(request, 'create_project.html', {'form': form, 'title': 'Create Project'})

@login_required
def edit_project_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if project.created_by != request.user and request.user.role != 'ADMIN':
        messages.error(request, "You do not have permission to edit this project.")
        return redirect('project_detail', project_id=project.id)
        
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            project = form.save()
            project.members.add(project.created_by) # Ensure creator remains
            log_activity(request.user, f"Updated project '{project.name}' details.")
            messages.success(request, "Project details updated!")
            return redirect('project_detail', project_id=project.id)
    else:
        form = ProjectForm(instance=project)
    return render(request, 'create_project.html', {'form': form, 'title': f'Edit Project: {project.name}', 'project': project})

@login_required
def delete_project_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if project.created_by != request.user and request.user.role != 'ADMIN':
        messages.error(request, "Only the project creator or admin can delete this project.")
        return redirect('project_detail', project_id=project.id)
        
    if request.method == 'POST':
        log_activity(request.user, f"Deleted project '{project.name}'")
        project.delete()
        messages.success(request, "Project deleted successfully.")
        return redirect('projects')
    return render(request, 'project_confirm_delete.html', {'project': project})

@login_required
def project_detail_view(request, project_id):
    project = get_object_or_404(Project, id=project_id, members=request.user)
    total_tasks = project.tasks.count()
    completed_tasks = project.tasks.filter(status='COMPLETED').count()
    progress_percentage = int((completed_tasks / total_tasks * 100)) if total_tasks > 0 else 0
    
    # Task priority distribution
    low_priority = project.tasks.filter(priority='LOW').count()
    med_priority = project.tasks.filter(priority='MEDIUM').count()
    high_priority = project.tasks.filter(priority='HIGH').count()
    
    # Status count
    todo_count = project.tasks.filter(status='TODO').count()
    progress_count = project.tasks.filter(status='IN_PROGRESS').count()
    review_count = project.tasks.filter(status='REVIEW').count()
    done_count = completed_tasks
    
    # Recent logs for this project
    recent_logs = ActivityLog.objects.filter(action__icontains=project.name).order_by('-datetime')[:5]
    
    context = {
        'project': project,
        'progress_percentage': progress_percentage,
        'low_priority': low_priority,
        'med_priority': med_priority,
        'high_priority': high_priority,
        'todo_count': todo_count,
        'progress_count': progress_count,
        'review_count': review_count,
        'done_count': done_count,
        'recent_logs': recent_logs,
    }
    return render(request, 'project_detail.html', context)

# Invite/Add Members to Project
@login_required
def invite_members_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if project.created_by != request.user and request.user.role != 'ADMIN':
        messages.error(request, "You do not have permission to manage members.")
        return redirect('project_detail', project_id=project.id)
        
    if request.method == 'POST':
        user_ids = request.POST.getlist('members')
        project.members.set(user_ids)
        project.members.add(project.created_by) # creator must stay
        log_activity(request.user, f"Updated member roster for '{project.name}'")
        messages.success(request, "Members updated successfully.")
        return redirect('project_detail', project_id=project.id)
        
    users = CustomUser.objects.all().exclude(id=project.created_by.id)
    return render(request, 'invite_members.html', {'project': project, 'users': users})

# --- Kanban Board & Task Drag-Drop ---

@login_required
def project_board_view(request, project_id):
    project = get_object_or_404(Project, id=project_id, members=request.user)
    
    # Filter search and parameters
    search_query = request.GET.get('search', '')
    priority_filter = request.GET.get('priority', '')
    assignee_filter = request.GET.get('assignee', '')
    
    tasks = project.tasks.all()
    
    if search_query:
        tasks = tasks.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query) | Q(labels__icontains=search_query))
    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)
    if assignee_filter:
        tasks = tasks.filter(assigned_user_id=assignee_filter)
        
    todo_tasks = tasks.filter(status='TODO')
    inprogress_tasks = tasks.filter(status='IN_PROGRESS')
    review_tasks = tasks.filter(status='REVIEW')
    completed_tasks = tasks.filter(status='COMPLETED')
    
    # Pass modal forms
    task_form = TaskForm(project=project)
    
    context = {
        'project': project,
        'todo_tasks': todo_tasks,
        'inprogress_tasks': inprogress_tasks,
        'review_tasks': review_tasks,
        'completed_tasks': completed_tasks,
        'task_form': task_form,
        'priority_filter': priority_filter,
        'assignee_filter': assignee_filter,
        'search_query': search_query,
    }
    return render(request, 'board.html', context)

# Ajax View for Card Drag and Drop updates
@login_required
def update_task_status_api(request):
    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        new_status = request.POST.get('status')
        task = get_object_or_404(Task, id=task_id, project__members=request.user)
        
        # Verify access
        old_status = task.get_status_display()
        task.status = new_status
        
        # Automatically update progress if completed
        if new_status == 'COMPLETED':
            task.progress = 100
        elif old_status == 'Completed' and new_status != 'COMPLETED':
            task.progress = 50
            
        task.save()
        
        action_msg = f"Moved task '{task.title}' status to '{task.get_status_display()}'"
        log_activity(request.user, action_msg)
        
        # Notify Assignee (if someone else moved it)
        if task.assigned_user and task.assigned_user != request.user:
            notify_user(task.assigned_user, f"{request.user.username} updated status of '{task.title}' to {task.get_status_display()}")
            
        # Send WebSockets board update
        send_ws_update(f"project_board_{task.project.id}", {
            "type": "board_update",
            "task_id": task.id,
            "status": new_status,
            "user": request.user.username,
            "action": action_msg
        })
        
        return JsonResponse({"status": "success", "message": "Task status updated."})
    return JsonResponse({"status": "error", "message": "Invalid Request"}, status=400)

# --- Task Management Views ---

@login_required
def create_task_view(request, project_id):
    project = get_object_or_404(Project, id=project_id, members=request.user)
    if request.method == 'POST':
        form = TaskForm(project, request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.save()
            
            # File uploads
            files = request.FILES.getlist('attachments')
            for f in files:
                TaskAttachment.objects.create(task=task, file=f)
                
            log_activity(request.user, f"Created task '{task.title}' in project '{project.name}'")
            
            if task.assigned_user:
                notify_user(task.assigned_user, f"You have been assigned to task '{task.title}' in '{project.name}'")
                
            # WebSocket Broadcast
            send_ws_update(f"project_board_{project.id}", {
                "type": "task_created",
                "task_id": task.id,
                "title": task.title,
                "status": task.status
            })
            
            messages.success(request, f"Task '{task.title}' created.")
            return redirect('project_board', project_id=project.id)
    return redirect('project_board', project_id=project.id)

@login_required
def edit_task_view(request, task_id):
    task = get_object_or_404(Task, id=task_id, project__members=request.user)
    project = task.project
    
    if request.method == 'POST':
        form = TaskForm(project, request.POST, instance=task)
        if form.is_valid():
            task = form.save()
            
            # Handle attachment uploads
            files = request.FILES.getlist('attachments')
            for f in files:
                TaskAttachment.objects.create(task=task, file=f)
                
            log_activity(request.user, f"Edited task '{task.title}'")
            
            # Notify assignee
            if task.assigned_user and task.assigned_user != request.user:
                notify_user(task.assigned_user, f"Task '{task.title}' has been modified by {request.user.username}")
                
            # WebSocket Broadcast
            send_ws_update(f"project_board_{project.id}", {
                "type": "task_updated",
                "task_id": task.id
            })
            
            messages.success(request, "Task updated successfully.")
            return redirect('task_detail', task_id=task.id)
    else:
        form = TaskForm(project, instance=task)
        
    return render(request, 'edit_task.html', {'form': form, 'task': task})

@login_required
def delete_task_view(request, task_id):
    task = get_object_or_404(Task, id=task_id, project__members=request.user)
    project = task.project
    if request.method == 'POST':
        log_activity(request.user, f"Deleted task '{task.title}'")
        
        # WebSocket Broadcast
        send_ws_update(f"project_board_{project.id}", {
            "type": "task_deleted",
            "task_id": task.id
        })
        
        task.delete()
        messages.success(request, "Task deleted.")
        return redirect('project_board', project_id=project.id)
    return render(request, 'task_confirm_delete.html', {'task': task})

@login_required
def task_detail_view(request, task_id):
    task = get_object_or_404(Task, id=task_id, project__members=request.user)
    comments = task.comments.all().order_by('created_date')
    comment_form = CommentForm()
    
    # Handle direct comment submission on task detail page
    if request.method == 'POST':
        if 'add_comment' in request.POST:
            c_form = CommentForm(request.POST)
            if c_form.is_valid():
                comment = c_form.save(commit=False)
                comment.task = task
                comment.user = request.user
                comment.save()
                
                log_activity(request.user, f"Commented on task '{task.title}'")
                
                # Mentions extraction (@username)
                mentions = re.findall(r'@(\w+)', comment.text)
                for uname in mentions:
                    try:
                        mentioned_user = CustomUser.objects.get(username=uname)
                        if mentioned_user != request.user:
                            notify_user(mentioned_user, f"{request.user.username} mentioned you in comments on '{task.title}'")
                    except CustomUser.DoesNotExist:
                        pass
                
                # Notify Assignee (if they aren't the commentator)
                if task.assigned_user and task.assigned_user != request.user:
                    notify_user(task.assigned_user, f"{request.user.username} commented on your task '{task.title}'")
                
                # Real-time WebSockets comment sync
                send_ws_update(f"task_comments_{task.id}", {
                    "type": "new_comment",
                    "comment_id": comment.id,
                    "user": comment.user.username,
                    "avatar": comment.user.profile_picture.url if comment.user.profile_picture else "",
                    "text": comment.text,
                    "created_date": comment.created_date.strftime('%b %d, %Y, %I:%M %p')
                })
                
                messages.success(request, "Comment added.")
                return redirect('task_detail', task_id=task.id)
                
    return render(request, 'task_detail.html', {
        'task': task,
        'comments': comments,
        'comment_form': comment_form
    })

# Delete attachment
@login_required
def delete_attachment_view(request, attachment_id):
    attachment = get_object_or_404(TaskAttachment, id=attachment_id, task__project__members=request.user)
    task_id = attachment.task.id
    log_activity(request.user, f"Deleted attachment '{attachment.filename()}' from '{attachment.task.title}'")
    attachment.delete()
    messages.success(request, "Attachment removed.")
    return redirect('task_detail', task_id=task_id)

# --- Comment Editing and Deletion ---

@login_required
def edit_comment_view(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.user != request.user:
        messages.error(request, "You can edit only your own comments.")
        return redirect('task_detail', task_id=comment.task.id)
        
    if request.method == 'POST':
        text = request.POST.get('text', '')
        if text.strip():
            comment.text = text
            comment.save()
            log_activity(request.user, f"Edited their comment on task '{comment.task.title}'")
            messages.success(request, "Comment updated.")
        return redirect('task_detail', task_id=comment.task.id)
    return render(request, 'edit_comment.html', {'comment': comment})

@login_required
def delete_comment_view(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.user != request.user:
        messages.error(request, "You can delete only your own comments.")
        return redirect('task_detail', task_id=comment.task.id)
        
    task_id = comment.task.id
    log_activity(request.user, f"Deleted their comment on task '{comment.task.title}'")
    comment.delete()
    messages.success(request, "Comment deleted.")
    return redirect('task_detail', task_id=task_id)

# --- Notifications Center ---

@login_required
def notifications_view(request):
    notifications = request.user.notifications.all().order_by('-created_date')
    return render(request, 'notifications.html', {'notifications': notifications})

@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.read_status = True
    notification.save()
    return JsonResponse({"status": "success", "unread_count": request.user.notifications.filter(read_status=False).count()})

@login_required
def mark_all_notifications_read(request):
    request.user.notifications.filter(read_status=False).update(read_status=True)
    messages.success(request, "All notifications marked as read.")
    return redirect('notifications')

# --- Export Tasks to CSV ---

@login_required
def export_project_tasks_csv(request, project_id):
    project = get_object_or_404(Project, id=project_id, members=request.user)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{project.name.replace(" ", "_")}_tasks.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Task Title', 'Description', 'Assigned To', 'Priority', 'Status', 'Due Date', 'Labels', 'Progress (%)', 'Created Date'])
    
    tasks = project.tasks.all()
    for task in tasks:
        assignee = task.assigned_user.username if task.assigned_user else "Unassigned"
        writer.writerow([
            task.title,
            task.description,
            assignee,
            task.get_priority_display(),
            task.get_status_display(),
            task.due_date,
            task.labels,
            task.progress,
            task.created_date.strftime('%Y-%m-%d %H:%M:%S')
        ])
        
    log_activity(request.user, f"Exported tasks for project '{project.name}' as CSV.")
    return response

# --- Activity Timeline View ---

@login_required
def activity_log_view(request):
    logs = ActivityLog.objects.filter(
        Q(user=request.user) | Q(user__in=CustomUser.objects.filter(projects__in=request.user.projects.all()))
    ).distinct().order_by('-datetime')[:50]
    return render(request, 'activity_logs.html', {'logs': logs})
