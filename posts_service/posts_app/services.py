from django.shortcuts import get_object_or_404

from posts_app.models import *


class PostService:
    @staticmethod
    def get_all_posts():
        posts = Post.objects.all()
        return posts

    @staticmethod
    def get_post(post_id):
        post = get_object_or_404(Post, id=post_id)
        return post

    @staticmethod
    def get_posts_by_author(author_id):
        posts = Post.objects.filter(author_id=author_id)
        return posts

    @staticmethod
    def get_posts_by_date(start_date, end_date):
        posts = Post.objects.filter(create_time__gte=start_date, create_time__lte=end_date)
        return posts


class CommentService:
    @staticmethod
    def get_comment(comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        return comment

    @staticmethod
    def get_comment_detail(comment_id):
        comment = Comment.objects.get(id=comment_id)
        comments = Comment.objects.filter(parent__pk=comment_id)
        return comment, comments

    @staticmethod
    def get_comments_by_post(post_id):
        comments = Comment.objects.filter(post_id=post_id, parent__isnull=True)
        return comments


class PostLikeService:
    @staticmethod
    def create_post_like(author_id, post_id):
        post = PostService.get_post(post_id)

        if PostLike.objects.filter(author_id=author_id, content=post).exists():
            return

        post.like_count += 1
        post.save()

        PostLike.objects.create(author_id=author_id, content=post)

    @staticmethod
    def delete_post_like(author_id, post_id):
        post = PostService.get_post(post_id)
        post_like = PostLike.objects.filter(author_id=author_id, content=post).first()
        if post_like:
            post.like_count -= 1
            post.save()
            post_like.delete()

