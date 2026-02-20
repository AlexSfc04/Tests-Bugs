from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from bookapp import views

urlpatterns = [
    path('form', views.BookCreate.as_view(), name='form'),
    path('list', views.book_list, name='book_list'),
    path('<int:pk>/detail', views.BookDetail.as_view(), name='book_detail'),
    path('<int:pk>/edit', views.BookUpdate.as_view(), name='book_edit'),
    path('<int:pk>/delete', views.BookDelete.as_view(), name='book_delete'),
    path('stats', views.stats, name='stats'),
    path('register', views.register, name='register'),
    path('login', LoginView.as_view(template_name='bookapp/form.html', redirect_authenticated_user=True), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
]
