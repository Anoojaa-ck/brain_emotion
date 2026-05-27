"""
URL configuration for brainemotion project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from myapp import views

urlpatterns = [
      path('loginpage_get/',views.loginpage_get),
      path('loginpage_post/',views.loginpage_post),
      path('logout_get/',views.logout_get),
      path('adminhomepage_get/',views.adminhomepage_get),
      path('viewusers_get/',views.viewusers_get),
      path('viewreview_get/',views.viewreview_get),
      path('changepassword_get/',views. changepassword_get),
      path('changepassword_post/',views.changepassword_post),
      path('forgotpass_get/',views.forgotpass_get),
      path('forgotpass_post/',views.forgotpass_post),
      path('android_forget_password_post/',views.android_forget_password_post),

      path('userlogin_post/',views.userlogin_post),
      path('usersignup_post/', views.usersignup_post),
      path('userprofile_post/',views.userprofile_post),
      path('usereditprofile_post/',views.usereditprofile_post),
      path('user_sendreview_post/',views.user_sendreview_post),
      path('user_changepassword_post/',views.user_changepassword_post),
      path('user_upload_text_post/',views.user_upload_text_post),
      path('diarycontents/',views.diarycontents),
      path('viewdiarycontent/',views.viewdiarycontent),
      path('editdiarycontent/', views.editdiarycontent),
      path('editcontent/', views.editcontent),
      path('deletediarycontent/', views.deletediarycontent),
      path('user_emotion_count/', views.user_emotion_count),
      path('view_emotiongraph/', views.view_emotiongraph),
      path('user_emotion_count_daily/', views.user_emotion_count_daily),

      path('admin_view_user_overall_graph/<id>', views.admin_view_user_overall_graph),
      path('get_user_graph_data/<id>/', views.get_user_graph_data),




]


