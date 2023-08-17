from django import forms
from .models import ContactForm, Comment, UserProfile, ProfilePost
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactForm
        fields = ['email', 'question']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']  # Include only the 'content' field in the form


class RegisterForm(UserCreationForm):
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    phone_number = forms.CharField(max_length=15)
    city = forms.CharField(max_length=100)
    country = forms.CharField(max_length=100)
    postal_code = forms.CharField(max_length=20)
    address = forms.CharField(max_length=255)

    class Meta:
        model = User  # Use the default Django User model
        fields = [
            'username', 'email', 'password1', 'password2', 'first_name', 'last_name',
            'date_of_birth', 'phone_number', 'city', 'country', 'postal_code', 'address',
        ]
    

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'bio']  # Add other fields if needed
        


class ProfilePostForm(forms.ModelForm):
    class Meta:
        model = ProfilePost
        fields = ['caption', 'image', 'video']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].widget.attrs.update({'accept': 'image/*'})
        self.fields['video'].widget.attrs.update({'accept': 'video/*'})
        self.fields['image'].required = False
        self.fields['video'].required = False
        self.fields['caption'].required = True
        self.fields['caption'].widget.attrs.update({'placeholder': 'Write your caption here...'})

    def clean(self):
        cleaned_data = super().clean()
        image = cleaned_data.get('image')
        video = cleaned_data.get('video')

        if not image and not video:
            raise forms.ValidationError("At least one of 'image' or 'video' fields must be filled.")

        return cleaned_data

class UserSearchForm(forms.Form):
    search_query = forms.CharField(label='Search for users', max_length=100)
