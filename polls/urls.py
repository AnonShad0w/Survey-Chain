from django.urls import path

from . import views

app_name = 'polls'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    path('<int:question_id>/vote/', views.vote, name='vote'),
    # page for adding a new poll
    path('new/', views.new_poll, name='new'),
    path('blockchain/', views.blockchain_info, name='blockchain'),
    path('<int:question_id>/transaction/', views.transaction_detail, name='transaction'),
]
