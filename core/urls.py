from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from  .import views

urlpatterns = [
    path('admin/', admin.site.urls),
]

urlpatterns += [
    path('', views.loginView, name='home'),
    path('login/', views.loginView, name='login'),
    path('register/', views.registerView, name='register'),
    path('logout/', views.LogoutView, name='logout'),
    path('app/', include(('app.urls', 'app'), namespace='app')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)