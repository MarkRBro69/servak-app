import logging
from datetime import datetime as dt

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from kafka_moule.async_kafka_producer import produce_post_notification
from posts_app.forms import *
from posts_app.services import *
from posts_app.utils import get_authenticated_user, set_tokens


logger = logging.getLogger('posts_service')


def read_posts(request):
    if request.method == 'GET':
        auth_user, uat, urt = get_authenticated_user(request)
        posts = PostService.get_all_posts()
        context = {
            'title': 'Posts',
            'posts': posts,
            'auth_user_id': auth_user['id'],
        }
        response = render(request, 'posts_app/posts_show.html', context)
        if uat is not None:
            response = set_tokens(response, uat, urt)
        return response

    else:
        return JsonResponse({'error': f'{request.method} is unsupported '}, status=405)


def read_post(request, post_id):
    if request.method == 'GET':
        auth_user, uat, urt = get_authenticated_user(request)
        post = PostService.get_post(post_id)
        comments = CommentService.get_comments_by_post(post_id)
        comment_form = AddCommentForm()
        context = {
            'title': f'Post - {post_id}',
            'post': post,
            'comments': comments,
            'form': comment_form,
            'button_name': 'Create comment',
            'auth_user_id': auth_user['id'],
        }
        response = render(request, 'posts_app/post_detail.html', context)
        if uat is not None:
            response = set_tokens(response, uat, urt)
        return response

    else:
        return JsonResponse({'error': f'{request.method} is unsupported '}, status=405)


def create_post(request):
    if request.method == "GET":
        form = AddPostForm()

        context = {
            'title': 'Create post',
            'form': form,
            'button_name': 'Create post'
        }
        return render(request, 'posts_app/create_post.html', context)

    if request.method == 'POST':
        form = AddPostForm(request.POST, request.FILES)
        if form.is_valid():
            auth_user, uat, urt = get_authenticated_user(request)

            print(request.FILES)
            print(form.cleaned_data['image'])

            post = form.save(commit=False)
            post.author_id = auth_user['id']
            post.save()

            response = redirect('post_list')
            if uat is not None:
                response = set_tokens(response, uat, urt)

            produce_post_notification(auth_user['id'], post.id)
            return response

    else:
        return JsonResponse({'error': f'{request.method} is unsupported '}, status=405)


def update_post(request, post_id):
    post = PostService.get_post(post_id)
    if request.method == 'GET':
        form = AddPostForm(instance=post)
        context = {
            'title': 'Update post',
            'form': form,
            'post': post,
            'button_name': 'Update',
        }
        return render(request, 'posts_app/base_form.html', context)

    if request.method == 'POST':
        auth_user, uat, urt = get_authenticated_user(request)
        form = AddPostForm(request.POST, request.FILES, instance=post)

        if form.is_valid():
            post.title = form.cleaned_data['title']
            post.content = form.cleaned_data['content']
            post.published = form.cleaned_data['published']
            post.save()

            response = redirect('post_list')
            if uat is not None:
                response = set_tokens(response, uat, urt)
            return response

    else:
        return JsonResponse({'error': f'{request.method} is unsupported '}, status=405)


def delete_post(request, post_id):
    if request.method == 'DELETE':
        csrf_token = request.POST.get('csrfmiddlewaretoken')
        logger.debug(f'Body csrfmiddlewaretoken: {csrf_token}')

        x_csrf_token = request.headers.get('X-CSRFToken')
        logger.debug(f'Header X-CSRFToken: {x_csrf_token}')

        auth_user, uat, urt = get_authenticated_user(request)
        post = PostService.get_post(post_id)
        if post:
            post.delete()
            response = JsonResponse({'message': 'Post deleted successfully'}, status=204)
        else:
            response = JsonResponse({'error': 'Post not found'}, status=404)

        if uat is not None:
            response = set_tokens(response, uat, urt)
        return response

    # else:
    #     return JsonResponse({'error': f'{request.method} is unsupported '}, status=405)

    if request.method == 'POST':
        csrf_token = request.POST.get('csrfmiddlewaretoken')
        logger.debug(f'Body csrfmiddlewaretoken: {csrf_token}')

        x_csrf_token = request.headers.get('X-CSRFToken')
        logger.debug(f'Header X-CSRFToken: {x_csrf_token}')

        auth_user, uat, urt = get_authenticated_user(request)
        post = PostService.get_post(post_id)
        if post:
            post.delete()
            response = JsonResponse({'message': 'Post deleted successfully'}, status=204)
        else:
            response = JsonResponse({'error': 'Post not found'}, status=404)

        if uat is not None:
            response = set_tokens(response, uat, urt)
        return response

    else:
        return JsonResponse({'error': f'{request.method} is unsupported '}, status=405)


def find_posts_by_author(request):
    if request.method == 'GET':
        auth_user, uat, urt = get_authenticated_user(request)
        posts = PostService.get_posts_by_author(auth_user['id'])
        context = {
            'title': 'Posts found',
            'posts': posts,
            'auth_user_id': auth_user['id'],
        }
        response = render(request, 'posts_app/posts_show.html', context)
        if uat is not None:
            response = set_tokens(response, uat, urt)
        return response

    else:
        return JsonResponse({'error': f'{request.method} is unsupported '}, status=405)


def find_posts_by_date(request):
    if request.method == 'GET':
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        start_date_obj = dt.strptime(start_date, '%Y-%m-%d') if start_date else None
        end_date_obj = dt.strptime(end_date, '%Y-%m-%d') if end_date else None

        if start_date_obj:
            start_date_obj = timezone.make_aware(start_date_obj.replace(hour=0, minute=0, second=0))
        if end_date_obj:
            end_date_obj = timezone.make_aware(end_date_obj.replace(hour=23, minute=59, second=59))

        posts = PostService.get_posts_by_date(start_date_obj, end_date_obj)
        context = {
            'title': 'Posts found',
            'posts': posts
        }

        return render(request, 'posts/posts.html', context)

    else:
        return JsonResponse({'error': f'{request.method} is unsupported '}, status=405)


def read_comment(request, post_id, comment_id):
    if request.method == 'GET':
        auth_user, uat, urt = get_authenticated_user(request)
        comment, comments = CommentService.get_comment_detail(comment_id)
        form = AddCommentForm()
        context = {
            'title': f'Comment - {comment_id}',
            'comment': comment,
            'post_id': post_id,
            'form': form,
            'comments': comments,
            'auth_user_id': auth_user['id'],
        }
        response = render(request, 'posts_app/comment_detail.html', context)
        if uat is not None:
            response = set_tokens(response, uat, urt)
        return response

    else:
        return JsonResponse({'error': f'{request.method} is unsupported '}, status=405)


def create_comment(request, post_id):
    if request.method == 'GET':
        form = AddCommentForm()
        context = {
            'title': 'Create comment',
            'form': form,
            'post_id': post_id
        }
        return render(request, 'posts_app/create_comment_form.html', context)

    if request.method == 'POST':
        form = AddCommentForm(request.POST)

        auth_user, uat, urt = get_authenticated_user(request)

        parent_comment_id = request.POST.get('parent_comment_id')
        parent_comment = None

        if parent_comment_id:
            parent_comment = CommentService.get_comment(parent_comment_id)

        if form.is_valid():
            post = PostService.get_post(post_id)
            comment = form.save(commit=False)
            comment.author_id = auth_user['id']
            comment.post = post

            if parent_comment is not None:
                comment.parent = parent_comment

            comment.save()
            response = redirect('post_list')
            if uat is not None:
                response = set_tokens(response, uat, urt)
            return response

    else:
        return JsonResponse({'error': f'{request.method} is unsupported '}, status=405)


def update_comment(request, post_id, comment_id):
    comment = CommentService.get_comment(comment_id)
    if request.method == 'GET':
        form = AddCommentForm(instance=comment)
        context = {
            'title': 'Update comment',
            'form': form,
            'comment': comment,
            'post_id': post_id,
            'comment_id': comment_id,
        }
        return render(request, 'posts_app/update_comment_form.html', context)

    if request.method == 'POST':
        auth_user, uat, urt = get_authenticated_user(request)
        form = AddCommentForm(request.POST, instance=comment)

        if form.is_valid():
            comment.save()
            response = redirect('post_list')
            if uat is not None:
                response = set_tokens(response, uat, urt)
            return response

    else:
        return JsonResponse({'error': f'{request.method} is unsupported '}, status=405)


def delete_comment(request, post_id, comment_id):
    if request.method == 'DELETE':
        auth_user, uat, urt = get_authenticated_user(request)
        comment = CommentService.get_comment(comment_id)
        if comment:
            comment.delete()
            response = JsonResponse({'message': 'Post deleted successfully'}, status=204)
        else:
            response = JsonResponse({'error': 'Post not found'}, status=404)

        if uat is not None:
            response = set_tokens(response, uat, urt)
        return response

    else:
        return JsonResponse({'error': f'{request.method} is unsupported '}, status=405)


def add_post_like(request, post_id):
    if request.method == 'POST':
        auth_user, uat, urt = get_authenticated_user(request)
        PostLikeService.create_post_like(auth_user['id'], post_id)
        response = JsonResponse({'message': 'Like added successfully'})

        if uat is not None:
            response = set_tokens(response, uat, urt)
        return response

    else:
        return JsonResponse({'error': f'{request.method} is unsupported '}, status=405)


def delete_post_like(request, post_id):
    if request.method == 'DELETE':
        auth_user, uat, urt = get_authenticated_user(request)
        PostLikeService.delete_post_like(auth_user['id'], post_id)
        response = JsonResponse({'message': 'Like removed successfully'})

        if uat is not None:
            response = set_tokens(response, uat, urt)
        return response

    else:
        return JsonResponse({'error': f'{request.method} is unsupported '}, status=405)

