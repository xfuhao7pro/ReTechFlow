from django.urls import path
from apps.goods.views import (
    AIEvaluationView,
    AIEvaluationResultView,
    GoodsCreateView,
    GoodsDraftView,
    ImageUploadView,
    CategoryListView,
    GoodsListView,
    MyGoodsListView,
    GoodsDetailView, ToggleLikeView, MyLikeListView, GoodsStatusUpdateView, GoodsDeleteView
)

app_name = 'goods'

urlpatterns = [
    path('ai-evaluation/', AIEvaluationView.as_view(), name='ai-evaluation'),
    path('ai-evaluation/<str:task_id>/', AIEvaluationResultView.as_view(), name='ai-evaluation-result'),
    path('create/', GoodsCreateView.as_view(), name='goods-create'),
    path('draft/', GoodsDraftView.as_view(), name='goods-draft'),
    path('up-image/', ImageUploadView.as_view(), name='up-image'),

    path('categories/', CategoryListView.as_view(), name='category-list'),

    path('list/', GoodsListView.as_view(), name='goods-list'),

    path('my-list/', MyGoodsListView.as_view(), name='my-goods-list'),

    path('like/toggle/', ToggleLikeView.as_view(), name='like-toggle'),

    path('like/list/', MyLikeListView.as_view(), name='like-list'),

    path('status-update/', GoodsStatusUpdateView.as_view(), name='goods-status-update'),

    path('delete/', GoodsDeleteView.as_view(), name='goods-delete'),

    path('<str:pk>/', GoodsDetailView.as_view(), name='goods-detail'),
]
