from django.urls import path
from inventory.views import *
urlpatterns = [
    path('', InventoryListCreateView.as_view(), name='InventoryListCreate'),
    path('<int:id>/', InventoryUpdateDeleteView.as_view(),
         name='InventoryUpdateDelete')
]