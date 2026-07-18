// Main JavaScript helper for Project Management Tool

document.addEventListener('DOMContentLoaded', function() {
    // 1. Dark Mode Toggle Setup
    const themeToggleBtn = document.getElementById('theme-toggle-btn');
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', function() {
            document.body.classList.toggle('dark-mode');
            const isDark = document.body.classList.contains('dark-mode');
            localStorage.setItem('theme', isDark ? 'dark' : 'light');
            updateThemeToggleButtonIcon(isDark);
        });
    }

    // Apply stored theme on load
    const storedTheme = localStorage.getItem('theme');
    if (storedTheme === 'dark') {
        document.body.classList.add('dark-mode');
        updateThemeToggleButtonIcon(true);
    } else {
        document.body.classList.remove('dark-mode');
        updateThemeToggleButtonIcon(false);
    }

    function updateThemeToggleButtonIcon(isDark) {
        if (!themeToggleBtn) return;
        const icon = themeToggleBtn.querySelector('i');
        if (icon) {
            if (isDark) {
                icon.className = 'bi bi-sun-fill text-warning';
            } else {
                icon.className = 'bi bi-moon-stars-fill text-secondary';
            }
        }
    }

    // Toggle Mobile Sidebar
    const mobileSidebarToggle = document.getElementById('mobile-sidebar-toggle');
    const appSidebar = document.querySelector('.app-sidebar');
    if (mobileSidebarToggle && appSidebar) {
        mobileSidebarToggle.addEventListener('click', function() {
            appSidebar.classList.toggle('show-mobile');
        });
    }

    // 2. Drag & Drop for Kanban Board
    const boardContainer = document.getElementById('kanban-board');
    if (boardContainer) {
        const projectId = boardContainer.dataset.projectId;
        setupKanbanDragAndDrop(boardContainer, projectId);
        setupBoardWebSocket(projectId);
    }

    // 3. Real-Time Task Comments WebSockets
    const taskDetailsContainer = document.getElementById('task-details-container');
    if (taskDetailsContainer) {
        const taskId = taskDetailsContainer.dataset.taskId;
        setupTaskCommentsWebSocket(taskId);
    }

    // 4. Live Global Notifications WebSockets
    setupGlobalNotificationsWebSocket();

    // 5. AJAX Notifications read buttons
    setupNotificationReadButtons();
});

// Helper for CSRF token extraction
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Show live notification Toast
function showToastNotification(message) {
    let toastContainer = document.getElementById('toast-container-custom');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container-custom';
        toastContainer.className = 'toast-container-custom';
        document.body.appendChild(toastContainer);
    }

    const toastId = 'toast_' + Date.now();
    const toastHTML = `
        <div id="${toastId}" class="toast align-items-center text-white bg-primary border-0 show" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="bi bi-bell-fill me-2"></i> ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;
    toastContainer.insertAdjacentHTML('beforeend', toastHTML);

    const toastElement = document.getElementById(toastId);
    setTimeout(() => {
        if (toastElement) {
            toastElement.classList.remove('show');
            setTimeout(() => toastElement.remove(), 500);
        }
    }, 5000);
}

// Notification AJAX Read actions
function setupNotificationReadButtons() {
    document.querySelectorAll('.mark-read-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const notificationId = this.dataset.id;
            const notificationItem = document.getElementById(`notification_${notificationId}`);
            
            fetch(`/notifications/${notificationId}/read/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json'
                }
            })
            .then(res => res.json())
            .then(data => {
                if (data.status === 'success') {
                    if (notificationItem) {
                        notificationItem.classList.remove('unread');
                        const dot = notificationItem.querySelector('.notification-item-unread-dot');
                        if (dot) dot.remove();
                    }
                    this.remove(); // remove the mark read button
                    
                    // Update badge count
                    updateUnreadNotificationCount(data.unread_count);
                }
            })
            .catch(err => console.error("Error reading notification:", err));
        });
    });
}

function updateUnreadNotificationCount(count) {
    const badges = document.querySelectorAll('.notification-badge');
    badges.forEach(badge => {
        if (count > 0) {
            badge.innerText = count;
            badge.style.display = 'inline-block';
        } else {
            badge.style.display = 'none';
        }
    });
}

// WebSockets logic for Global Notifications
function setupGlobalNotificationsWebSocket() {
    const wsScheme = window.location.protocol === "https:" ? "wss" : "ws";
    const wsUrl = `${wsScheme}://${window.location.host}/ws/notifications/`;
    
    // Only connect if user is authenticated (indicated by existence of notification-badge element)
    if (!document.querySelector('.notification-badge')) return;

    const socket = new WebSocket(wsUrl);

    socket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        if (data.type === 'send_notification') {
            // Update unread badge count
            updateUnreadNotificationCount(data.unread_count);
            // Show custom toast alert
            showToastNotification(data.message);
        }
    };

    socket.onclose = function(e) {
        // Reconnect after 3 seconds
        setTimeout(setupGlobalNotificationsWebSocket, 3000);
    };
}

// WebSockets logic for Task Comments detail view
function setupTaskCommentsWebSocket(taskId) {
    const wsScheme = window.location.protocol === "https:" ? "wss" : "ws";
    const wsUrl = `${wsScheme}://${window.location.host}/ws/task/${taskId}/comments/`;
    const socket = new WebSocket(wsUrl);

    socket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        if (data.type === 'new_comment') {
            appendCommentToUI(data);
        }
    };

    socket.onclose = function(e) {
        setTimeout(() => setupTaskCommentsWebSocket(taskId), 3000);
    };

    function appendCommentToUI(commentData) {
        const commentsList = document.getElementById('comments-list');
        if (!commentsList) return;

        // Check if comment already exists in the list
        if (document.getElementById(`comment_${commentData.comment_id}`)) return;

        const commentHTML = `
            <div class="card mb-3 shadow-sm border-0" id="comment_${commentData.comment_id}">
                <div class="card-body p-3">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <div class="d-flex align-items-center gap-2">
                            <div class="user-avatar-initials" style="width: 28px; height: 28px; font-size: 0.75rem;">
                                ${commentData.user.substring(0, 2).toUpperCase()}
                            </div>
                            <span class="fw-semibold text-dark">${commentData.user}</span>
                        </div>
                        <small class="text-muted">${commentData.created_date}</small>
                    </div>
                    <p class="card-text text-secondary mb-0" style="white-space: pre-wrap;">${commentData.text}</p>
                </div>
            </div>
        `;
        commentsList.insertAdjacentHTML('beforeend', commentHTML);
    }
}

// Kanban Drag & Drop Implementation
function setupKanbanDragAndDrop(board, projectId) {
    const cards = board.querySelectorAll('.task-card');
    const lists = board.querySelectorAll('.board-cards-list');

    cards.forEach(card => {
        card.addEventListener('dragstart', function() {
            card.classList.add('dragging');
        });

        card.addEventListener('dragend', function() {
            card.classList.remove('dragging');
        });
    });

    lists.forEach(list => {
        list.addEventListener('dragover', function(e) {
            e.preventDefault();
            const draggingCard = board.querySelector('.dragging');
            if (draggingCard) {
                list.appendChild(draggingCard);
            }
        });

        list.addEventListener('dragenter', function() {
            this.closest('.board-column').classList.add('drag-over');
        });

        list.addEventListener('dragleave', function() {
            this.closest('.board-column').classList.remove('drag-over');
        });

        list.addEventListener('drop', function() {
            const column = this.closest('.board-column');
            column.classList.remove('drag-over');
            
            const draggingCard = board.querySelector('.dragging');
            if (draggingCard) {
                const taskId = draggingCard.dataset.taskId;
                const newStatus = column.dataset.status;
                
                // Call API backend to save drag status
                saveTaskStatusChange(taskId, newStatus);
            }
        });
    });
}

function saveTaskStatusChange(taskId, newStatus) {
    const formData = new FormData();
    formData.append('task_id', taskId);
    formData.append('status', newStatus);

    fetch('/tasks/status/update/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'success') {
            console.log(`Task ${taskId} moved to status ${newStatus}`);
            // Update counts on frontend columns
            updateBoardColumnCounts();
        } else {
            console.error("Failed to update status on server:", data.message);
        }
    })
    .catch(err => console.error("Error updates task status:", err));
}

function updateBoardColumnCounts() {
    const columns = document.querySelectorAll('.board-column');
    columns.forEach(col => {
        const badge = col.querySelector('.column-badge');
        const cardsCount = col.querySelectorAll('.task-card').length;
        if (badge) {
            badge.innerText = cardsCount;
        }
    });
}

// WebSockets logic for Project Board drag updates
let boardSocket = null;
function setupBoardWebSocket(projectId) {
    const wsScheme = window.location.protocol === "https:" ? "wss" : "ws";
    const wsUrl = `${wsScheme}://${window.location.host}/ws/project/${projectId}/board/`;
    boardSocket = new WebSocket(wsUrl);

    boardSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        
        // Handle incoming live broadcast of card movements by other users
        if (data.type === 'board_update' && data.user !== getCurrentUserName()) {
            syncBoardCardPosition(data.task_id, data.status);
            showToastNotification(data.action);
        } else if (data.type === 'task_created' || data.type === 'task_deleted' || data.type === 'task_updated') {
            // Reload page on major board additions/removals to sync complete details
            window.location.reload();
        }
    };

    boardSocket.onclose = function(e) {
        setTimeout(() => setupBoardWebSocket(projectId), 3000);
    };

    function syncBoardCardPosition(taskId, status) {
        const card = document.querySelector(`.task-card[data-task-id="${taskId}"]`);
        const targetList = document.querySelector(`.board-column[data-status="${status}"] .board-cards-list`);
        if (card && targetList) {
            targetList.appendChild(card);
            updateBoardColumnCounts();
        }
    }

    function getCurrentUserName() {
        const profileDropdown = document.getElementById('userProfileDropdown');
        return profileDropdown ? profileDropdown.innerText.trim() : "";
    }
}
