from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('cek-cuaca/', views.cek_cuaca, name='cek_cuaca'),
    path('weather-highlights/', views.weather_highlights, name='weather_highlights'),
    path('about-us/', views.about_us, name='about_us'),
    path('feedback/', views.feedback, name='feedback'),
    path('tips/', views.tips_list_view, name='tips_list'),
    path('tips/<int:pk>/', views.tips_detail, name='tips_detail'),

    # Galeri publik
    path('galeri/', views.galeri_list, name='galeri_list'),
    path('galeri/upload/', views.galeri_upload, name='galeri_upload'),

    # Profil user
    path('profil/', views.profil, name='profil'),

    # Peta Cuaca
    path('peta-cuaca/', views.peta_cuaca, name='peta_cuaca'),
    path('api/cuaca-lokasi/', views.api_cuaca_lokasi, name='api_cuaca_lokasi'),
    path('api/autocomplete-kota/', views.api_autocomplete_kota, name='api_autocomplete_kota'),
    path('api/geocode/', views.api_geocode, name='api_geocode'),
    path('api/rekomendasi-ai/', views.api_rekomendasi_ai, name='api_rekomendasi_ai'),

    # Dashboard admin
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/tips/', views.tips_list_dashboard, name='tips_list_dashboard'),
    path('dashboard/tips/tambah/', views.tips_create, name='tips_create'),
    path('dashboard/tips/edit/<int:pk>/', views.tips_edit, name='tips_edit'),
    path('dashboard/tips/hapus/<int:pk>/', views.tips_delete, name='tips_delete'),
    path('dashboard/feedback/', views.feedback_dashboard, name='feedback_dashboard'),
    path('dashboard/feedback/hapus/<int:pk>/', views.feedback_delete, name='feedback_delete'),
    path('dashboard/feedback/hapus/<int:pk>/', views.feedback_delete, name='feedback_delete'),
    path('dashboard/feedback/balas/<int:pk>/', views.feedback_balas, name='feedback_balas'),
    path('dashboard/users/', views.users_dashboard, name='users_dashboard'),
    path('dashboard/kategori/', views.kategori_dashboard, name='kategori_dashboard'),
    path('dashboard/kategori/tambah/', views.kategori_tambah, name='kategori_tambah'),
    path('dashboard/kategori/hapus/<int:pk>/', views.kategori_delete, name='kategori_delete'),
    path('dashboard/kategori/edit/<int:pk>/', views.kategori_edit, name='kategori_edit'),
    path('dashboard/galeri/', views.galeri_dashboard, name='galeri_dashboard'),
    path('dashboard/galeri/approve/<int:pk>/', views.galeri_approve, name='galeri_approve'),
    path('dashboard/galeri/reject/<int:pk>/', views.galeri_reject, name='galeri_reject'),
    path('dashboard/galeri/hapus/<int:pk>/', views.galeri_delete_admin, name='galeri_delete_admin'),
]