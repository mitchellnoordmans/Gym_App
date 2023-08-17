
from django.contrib import admin
from django.urls import path, include
from core.views import (
    contact , about, 
    custom_login_view, custom_logout_view, submit_comment, frequently_asked, register, 
    update_profile, user_profile, explore, personal_trainers, users, create_profile_post, user_search_view,
    news
    )
from django.conf import settings
from django.conf.urls.static import static


app_name = 'core'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', explore, name='explore'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    path('login/', custom_login_view, name='login'),
    path('logout/', custom_logout_view, name='logout'),
    path('frequently_asked/', frequently_asked, name='frequently_asked'),
    path('register/', register, name='register'),
    path('personal_trainers/', personal_trainers, name='personal_trainers'),
    path('users/', users, name='users'),
    path('search/', user_search_view, name='user_search'),
    path('news/', news, name='news'),
    path('create_profile_post/', create_profile_post, name='create_profile_post'),
    path('update_profile/', update_profile, name='update_profile'),
    path('rooms/', include('room.urls')),
    path('submit_comment/<int:post_id>/', submit_comment, name='submit_comment'),
    path('<str:username>/', user_profile, name='user_profile'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)