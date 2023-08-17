from django.contrib.auth import login
from django.shortcuts import render, redirect
from .models import  Comment, Frequently_asked, UserProfile, ProfilePost, News
from .forms import ContactForm, CommentForm, RegisterForm, UserProfileForm, ProfilePostForm, UserSearchForm
from django.core.mail import EmailMessage
import os
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.http import HttpResponse, Http404
from django.db.models import Q

def about(request):
    return render(request, 'about.html')

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('explore')  # Redirect to the homepage after form submission
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})


def frequently_asked(request):
    questions = Frequently_asked.objects.all()
    return render(request, 'frequently_asked.html', {'questions': questions})


def custom_login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # The form uses your custom authentication backend to authenticate the user
            user = form.get_user()  # The user object returned by the form (if credentials are valid)
            if user is not None:
                login(request, user)
                return redirect('explore')
            else:
                form.add_error(None, "Invalid username or password.")
    else:
        form = AuthenticationForm(request)
    return render(request, 'login.html', {'form': form})


def custom_logout_view(request):
    logout(request)
    return redirect('explore')

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # Create a new User instance with the cleaned form data
            new_user = User(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
            )
            new_user.set_password(form.cleaned_data['password1'])  # Set the user's password securely
            new_user.save()  # Save the user to the database

            # Create a new UserProfile instance with the additional data
            date_of_birth = form.cleaned_data['date_of_birth']
            phone_number = form.cleaned_data['phone_number']
            city = form.cleaned_data['city']
            country = form.cleaned_data['country']
            postal_code = form.cleaned_data['postal_code']
            address = form.cleaned_data['address']
            user_profile = UserProfile(
                user=new_user,
                date_of_birth=date_of_birth,
                phone_number=phone_number,
                city=city,
                country=country,
                postal_code=postal_code,
                address=address,
            )
            user_profile.save()

            # You can add any additional logic here, e.g., send a welcome email to the user.

            return redirect('explore')  # Redirect to the home page after successful registration
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

@login_required
def update_profile(request):
    user_profile = request.user.userprofile  # Get the user's profile

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('user_profile', username=request.user.username)  # Redirect to the profile page after saving
    else:
        form = UserProfileForm(instance=user_profile)

    return render(request, 'update_profile.html', {'form': form})


def personal_trainers(request):
    personal_trainers = UserProfile.objects.filter(personal_trainer=True)
    return render(request, 'personal_trainers.html', {'personal_trainers': personal_trainers})

def users(request):
    users = UserProfile.objects.all()
    return render(request, 'users.html', {'users':users})

#@login_required
#def create_profile_post(request):
    if request.method == 'POST':
        form = ProfilePostForm(request.POST, request.FILES, prefix='profile_post_form')
        if form.is_valid():
            form.instance.user = request.user.userprofile
            form.save()
            messages.success(request, "Profile post created successfully!")
            return redirect('user_profile', username=request.user.username)
    else:
        form = ProfilePostForm(prefix='profile_post_form')
    
    return render(request, 'user_profile.html', {'form': form})

@login_required
def create_profile_post(request):
    form = ProfilePostForm(prefix='profile_post_form')

    if request.method == 'POST':
        form = ProfilePostForm(request.POST, request.FILES, prefix='profile_post_form')
        if form.is_valid():
            form.instance.user = request.user.userprofile
            form.save()
            messages.success(request, "Profile post created successfully!")
            return redirect('user_profile', username=request.user.username)

    # Check the template being rendered and conditionally include the form in the context
    template_name = 'create_profile_post.html' if 'create_profile_post' in request.path else 'user_profile.html'
    context = {'form': form}

    return render(request, template_name, context)

def explore(request):
    # Get the latest 20 posts
    latest_posts = ProfilePost.objects.order_by('-created_at')[:20]
    # Prepare the data for JSON response
    data = {
        'posts': [
            {
                'caption': post.caption,
                'image': post.image.url if post.image else None,
                'video': post.video.url if post.video else None,
                'username': post.user.user.username,
                'profile_picture': get_profile_picture_url(post.user),
            }
            for post in latest_posts
        ]
    }

    # If the request is AJAX (based on the header), return JSON response
    if request.headers.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        return JsonResponse(data)

    # For non-AJAX requests, render the explore.html template
    return render(request, 'explore.html', {'latest_posts': latest_posts})

#def explore(request):
    # Get the latest 20 posts
    latest_posts = ProfilePost.objects.order_by('-created_at')[:20]

    # Prepare the data for JSON response
    data = {
        'posts': [
            {
                'caption': post.caption,
                'image': post.image.url if post.image else None,
                'video': post.video.url if post.video else None,
                'username': post.user.user.username,
                'profile_picture': get_profile_picture_url(post.user),
            }
            for post in latest_posts
        ]
    }

    # If the request is AJAX, return JSON response
    if request.is_ajax():
        return JsonResponse(data)

    # For non-AJAX requests, render the explore.html template
    return render(request, 'explore.html', {'latest_posts': latest_posts})


def get_profile_picture_url(user):
    try:
        return user.userprofile.profile_picture.url
    except AttributeError:
        return None
    
def submit_comment(request, post_id):
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.user = request.user

            post_type = request.POST.get('post_type')
            if post_type == 'profile':
                profile_post = get_object_or_404(ProfilePost, id=post_id)
                comment.profile_post = profile_post

            comment.save()

            # Redirect back to the appropriate page based on the post type
            if post_type == 'profile':
                return redirect('user_profile', username=request.user.username)

    return redirect('explore')  # Redirect back to the home page if the request method is not POST


def user_profile(request, username):
    user_profile = get_object_or_404(UserProfile, user__username=username)
    profile_posts = ProfilePost.objects.filter(user=user_profile).order_by('-created_at')
    comment_form = CommentForm()
    profile_comments = Comment.objects.filter(profile_post__user=user_profile, parent_comment=None)

    if request.method == 'POST':
        profile_post_id = request.POST.get('profile_post_id')
        profile_post = ProfilePost.objects.get(id=profile_post_id)
        comment_form = CommentForm(request.POST)

        if comment_form.is_valid():
            parent_comment_id = request.POST.get('parent_comment_id')
            parent_comment = None
            if parent_comment_id:
                parent_comment = Comment.objects.get(id=parent_comment_id)

            comment = comment_form.save(commit=False)
            comment.user = request.user
            comment.profile_post = profile_post
            comment.parent_comment = parent_comment
            comment.save()
            return redirect('user_profile', username=username)  

    return render(request, 'user_profile.html', {
        'user_profile': user_profile,
        'profile_posts': profile_posts,
        'comment_form': comment_form,
        'profile_comments': profile_comments,
    })

def user_search_view(request):
    form = UserSearchForm(request.GET)
    search_results = []
    
    if form.is_valid():
        search_query = form.cleaned_data['search_query']
        search_results = User.objects.filter(username__icontains=search_query)
    
    return render(request, 'search_results.html', {'form': form, 'search_results': search_results})


def news(request):
    news_posts = News.objects.order_by('-create_date')[:5]
    data = {
        'news': [
            {
                'title': news.title,
                'body': news.body,  # Fix the syntax error here
                'create_date': news.create_date.strftime('%Y-%m-%d %H:%M:%S'),
            }
            for news in news_posts
        ] 
    }
    
    if request.headers.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        return JsonResponse(data)

    return render(request, 'news.html', {'news_posts': news_posts})
