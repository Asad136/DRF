from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('register/', views.signup, name='register'),
    path('login/', views.loginuser, name='login'),
    path('products/', views.productlist, name='product-list'),
    path('products/create/', views.productcreate, name='product-create'),
    path('products/<int:pk>/', views.productdetail, name='product-detail'),
    path('products/<int:pk>/update/', views.productupdate, name='product-update'),
    path('products/<int:pk>/delete/', views.productdelete, name='product-delete'),
    path('products/csv/', views.downloadcsv, name='download-products-csv'),
    path('logout/', views.logout, name='logout'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
