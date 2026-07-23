document.addEventListener('DOMContentLoaded', function() {
    // 5. getCookie function
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

    // 2. AJAX Like Toggle
    const likeBtns = document.querySelectorAll('.like-btn');
    likeBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const postId = this.getAttribute('data-post-id');
            const url = `/post/${postId}/like/`;
            const csrftoken = getCookie('csrftoken');

            fetch(url, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrftoken,
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if(data.liked) {
                    this.classList.add('liked');
                    this.querySelector('i').classList.remove('bi-heart');
                    this.querySelector('i').classList.add('bi-heart-fill');
                } else {
                    this.classList.remove('liked');
                    this.querySelector('i').classList.add('bi-heart');
                    this.querySelector('i').classList.remove('bi-heart-fill');
                }
                const likesCount = this.querySelector('.likes-count');
                if(likesCount) {
                    likesCount.textContent = data.likes_count;
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });

    // 3. AJAX Follow Toggle
    const followBtns = document.querySelectorAll('.follow-btn');
    followBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const username = this.getAttribute('data-username');
            const url = `/follow/${username}/`;
            const csrftoken = getCookie('csrftoken');

            fetch(url, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrftoken,
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if(data.is_following) {
                    this.textContent = 'Unfollow';
                    this.classList.remove('cs-btn-primary');
                    this.classList.add('cs-btn-outline');
                } else {
                    this.textContent = 'Follow';
                    this.classList.add('cs-btn-primary');
                    this.classList.remove('cs-btn-outline');
                }
                // Optional: update followers count on page if exists
                const followersCount = document.querySelector('.followers-count');
                if(followersCount && data.followers_count !== undefined) {
                    followersCount.textContent = data.followers_count;
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });

    // 4. Image Upload Preview
    const imageInputs = document.querySelectorAll('#id_image, #id_profile_picture');
    const imagePreview = document.getElementById('image-preview');

    imageInputs.forEach(input => {
        input.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    if (imagePreview) {
                        imagePreview.src = e.target.result;
                        imagePreview.style.display = 'block';
                    } else {
                        // Create preview if it doesn't exist
                        const img = document.createElement('img');
                        img.id = 'image-preview';
                        img.src = e.target.result;
                        img.style.maxWidth = '100%';
                        img.style.marginTop = '10px';
                        img.style.borderRadius = '8px';
                        input.parentNode.appendChild(img);
                    }
                }
                reader.readAsDataURL(this.files[0]);
            }
        });
    });

    // 6. Auto-dismiss toasts after 5 seconds
    const toasts = document.querySelectorAll('.cs-toast');
    toasts.forEach(toast => {
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }, 5000);

        const closeBtn = toast.querySelector('.cs-toast-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                toast.style.opacity = '0';
                setTimeout(() => toast.remove(), 300);
            });
        }
    });

    // 7. Comment edit toggle
    const editToggles = document.querySelectorAll('.comment-edit-toggle');
    editToggles.forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            // Assuming next sibling or somewhere close is the form.
            // Adjust traversing based on actual HTML structure
            const form = this.closest('.cs-comment').querySelector('.comment-edit-form');
            if (form) {
                if (form.style.display === 'none' || form.style.display === '') {
                    form.style.display = 'block';
                } else {
                    form.style.display = 'none';
                }
            }
        });
    });

    // 8. Delete confirmation
    const deleteForms = document.querySelectorAll('.confirm-delete');
    deleteForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!confirm('Are you sure you want to delete this?')) {
                e.preventDefault();
            }
        });
    });
});
