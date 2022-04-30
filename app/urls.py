from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('student/', views.studentRequest , name='student'),
    path('upload-file/', views.uploadFile , name='file'),
    path('admin/', views.admin , name='admin'),
    path('compute/', views.compute , name='compute'),
    path('update/', views.update , name='update'),
    path('viz/', views.viz , name='viz'),
    path('close/', views.close , name='close'),
    path('delete/<int:id>', views.delete , name='delete'),
    path('get-edit-form/<int:id>', views.edit , name='edit'),
    path('name-edit/<int:id>', views.nameEdit , name='name-edit'),
    path('name-close/', views.nameClose , name='name-close'),
    path('name-update/', views.nameUpdate , name='name-update'),
    path('name-compute/', views.nameCompute , name='name-compute'),
    path('name-delete/<int:id>', views.nameDelete , name='name-delete'),
    path('test/', views.test , name='test'),
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
