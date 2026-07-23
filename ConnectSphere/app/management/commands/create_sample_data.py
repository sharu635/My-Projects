from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from app.models import Post, Comment, Like, Follow

class Command(BaseCommand):
    help = 'Creates sample data for testing ConnectSphere'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample data...')

        # Create demo users
        users_data = [
            {'username': 'emma_design', 'email': 'emma@example.com', 'first_name': 'Emma', 'last_name': 'Johnson', 'password': 'Connect@123'},
            {'username': 'alex_tech', 'email': 'alex@example.com', 'first_name': 'Alex', 'last_name': 'Williams', 'password': 'Connect@123'},
            {'username': 'sophia_art', 'email': 'sophia@example.com', 'first_name': 'Sophia', 'last_name': 'Martinez', 'password': 'Connect@123'},
            {'username': 'ryan_dev', 'email': 'ryan@example.com', 'first_name': 'Ryan', 'last_name': 'Chen', 'password': 'Connect@123'},
        ]

        created_users = []
        for data in users_data:
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'email': data['email'],
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                }
            )
            if created:
                user.set_password(data['password'])
                user.save()
                self.stdout.write(f'  Created user: {user.username}')
            else:
                self.stdout.write(f'  User already exists: {user.username}')
            created_users.append(user)

        # Update bios
        bios = [
            'UI/UX Designer | Coffee lover | Creating beautiful digital experiences ✨',
            'Full-stack developer | Open source enthusiast | Building the future 🚀',
            'Digital artist | Photography | Capturing moments that matter 📸',
            'Software engineer | Tech blogger | Always learning something new 💡',
        ]
        for user, bio in zip(created_users, bios):
            user.profile.bio = bio
            user.profile.save()

        # Create sample posts
        posts_data = [
            {'user': created_users[0], 'caption': 'Just finished designing the new dashboard for our app! The glassmorphism effect looks stunning. What do you think? 🎨 #design #UI #creative'},
            {'user': created_users[1], 'caption': 'Deployed my first microservice architecture today. The feeling when all containers are running smoothly is unmatched! 🐳 #devops #coding'},
            {'user': created_users[2], 'caption': 'Golden hour at the beach never disappoints. Nature is the best artist. 🌅 #photography #nature #goldenhour'},
            {'user': created_users[3], 'caption': 'Just published my article on Django best practices. Link in bio! 📝 #django #python #webdev'},
            {'user': created_users[0], 'caption': 'Design tip: Less is more. Embrace whitespace and let your content breathe. 🤍 #designtips #minimal'},
            {'user': created_users[1], 'caption': 'Excited to announce that our open source project just hit 1000 stars on GitHub! Thank you all for the support! ⭐ #opensource'},
            {'user': created_users[2], 'caption': 'New digital painting completed! Spent 12 hours on this piece and I am so proud of the result. 🎨 #digitalart #illustration'},
            {'user': created_users[3], 'caption': 'Coffee + Code = Perfect morning routine. Working on an exciting new project! ☕💻 #coding #developer'},
        ]

        created_posts = []
        for data in posts_data:
            post, created = Post.objects.get_or_create(
                user=data['user'],
                caption=data['caption'],
            )
            if created:
                self.stdout.write(f'  Created post by: {post.user.username}')
            created_posts.append(post)

        # Create sample comments
        comments_data = [
            {'user': created_users[1], 'post': created_posts[0], 'text': 'This looks absolutely amazing! The glassmorphism is on point! 🔥'},
            {'user': created_users[2], 'post': created_posts[0], 'text': 'Love the color palette you chose! Very modern.'},
            {'user': created_users[0], 'post': created_posts[1], 'text': 'Congratulations! Microservices can be tricky but so rewarding.'},
            {'user': created_users[3], 'post': created_posts[2], 'text': 'Stunning capture! What camera do you use?'},
            {'user': created_users[1], 'post': created_posts[3], 'text': 'Great article! Really helped me understand Django signals better.'},
            {'user': created_users[2], 'post': created_posts[5], 'text': 'Well deserved! Your project is fantastic! 🌟'},
            {'user': created_users[0], 'post': created_posts[6], 'text': 'The colors and composition are breathtaking!'},
            {'user': created_users[3], 'post': created_posts[4], 'text': 'So true! Whitespace is underrated in design.'},
        ]

        for data in comments_data:
            comment, created = Comment.objects.get_or_create(
                user=data['user'],
                post=data['post'],
                text=data['text'],
            )
            if created:
                self.stdout.write(f'  Created comment by: {comment.user.username}')

        # Create likes
        for i, user in enumerate(created_users):
            for j, post in enumerate(created_posts):
                if post.user != user and (i + j) % 2 == 0:
                    Like.objects.get_or_create(user=user, post=post)

        self.stdout.write('  Created sample likes')

        # Create follows (everyone follows everyone except themselves)
        for follower in created_users:
            for following in created_users:
                if follower != following:
                    Follow.objects.get_or_create(follower=follower, following=following)

        self.stdout.write('  Created sample follows')

        self.stdout.write(self.style.SUCCESS('\nSample data created successfully!'))
        self.stdout.write('\nDemo Credentials:')
        self.stdout.write('  Username: emma_design  | Password: Connect@123')
        self.stdout.write('  Username: alex_tech    | Password: Connect@123')
        self.stdout.write('  Username: sophia_art   | Password: Connect@123')
        self.stdout.write('  Username: ryan_dev     | Password: Connect@123')
