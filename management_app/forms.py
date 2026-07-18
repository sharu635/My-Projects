from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Project, Task, Comment

class CustomUserCreationForm(UserCreationForm):
    full_name = forms.CharField(max_length=255, required=False, help_text="Enter your full name.")
    email = forms.EmailField(required=True, help_text="Required. Enter a valid email address.")
    role = forms.ChoiceField(choices=CustomUser.ROLE_CHOICES, required=True)
    profile_picture = forms.ImageField(required=False)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('full_name', 'email', 'role', 'profile_picture')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field_name == 'role':
                field.widget.attrs['class'] = 'form-select'

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('full_name', 'email', 'role', 'profile_picture')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field_name == 'role':
                field.widget.attrs['class'] = 'form-select'

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('name', 'description', 'start_date', 'end_date', 'status', 'members')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'members': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name == 'status':
                field.widget.attrs['class'] = 'form-select'
            elif field_name == 'members':
                # Custom styling for multiple checkboxes
                field.widget.attrs['class'] = 'form-check-input'
            else:
                field.widget.attrs['class'] = 'form-control'

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ('title', 'description', 'assigned_user', 'priority', 'status', 'due_date', 'labels', 'progress')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'progress': forms.NumberInput(attrs={'min': 0, 'max': 100}),
        }

    def __init__(self, project=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if project:
            # Only allow assigning task to members of the specific project
            self.fields['assigned_user'].queryset = project.members.all()
        for field_name, field in self.fields.items():
            if field_name in ['assigned_user', 'priority', 'status']:
                field.widget.attrs['class'] = 'form-select'
            else:
                field.widget.attrs['class'] = 'form-control'

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Write a comment... Mention users using @username'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['text'].widget.attrs['class'] = 'form-control'
