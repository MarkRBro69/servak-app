from django.urls import path

from posts_app.views import *

urlpatterns = [
    # Posts
    path('', read_posts, name='post_list'),
    path('post/', create_post, name='create_post'),
    path('<int:post_id>/', read_post, name='post_detail'),
    path('<int:post_id>/put/', update_post, name='update_post'),
    path('<int:post_id>/delete/', delete_post, name='delete_post'),
    path('find_by_author/', find_posts_by_author, name='find_posts_by_author'),
    path('find_by_date/', find_posts_by_date, name='find_posts_by_date'),

    # Comments
    path('<int:post_id>/comments/post/', create_comment, name='create_comment'),
    path('<int:post_id>/comments/<int:comment_id>/', read_comment, name='comment_detail'),
    path('<int:post_id>/comments/<int:comment_id>/put/', update_comment, name='update_comment'),
    path('<int:post_id>/comments/<int:comment_id>/delete/', delete_comment, name='delete_comment'),

    # Post likes
    path('<int:post_id>/post_likes/add/', add_post_like, name='add_post_like'),
    path('<int:post_id>/post_likes/remove/', delete_post_like, name='delete_post_like'),

    # # # Comment likes
    # path('posts/<int:post_id>/comments/<int:comment_id>/comment_like/', delete_comment_like, name='delete_comment_like'),
    # path('posts/<int:post_id>/comments/<int:comment_id>/comments_like/', delete_comment_like, name='delete_comment_like'),
]
