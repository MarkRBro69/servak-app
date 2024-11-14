from django import forms

from posts_app.models import *


class AddPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'published', 'image']


class AddCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
