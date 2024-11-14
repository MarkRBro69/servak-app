from django.db import models


class BaseContent(models.Model):
    author_id = models.IntegerField()
    content = models.TextField()
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    like_count = models.PositiveIntegerField(default=0)

    objects = models.Manager()

    class Meta:
        abstract = True


class Post(BaseContent):
    title = models.CharField(max_length=255)
    published = models.BooleanField(default=False)

    def get_image_upload_path(self, filename):
        return f'posts/{self.author_id}/{self.title}/{filename}'

    image = models.ImageField(
        upload_to=get_image_upload_path,
        blank=True,
        height_field=None,
        width_field=None,
        max_length=None,
    )


class Comment(BaseContent):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )


class BaseLike(models.Model):
    author_id = models.IntegerField()

    objects = models.Manager()

    class Meta:
        abstract = True


class PostLike(BaseLike):
    content = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_likes')


class CommentLike(BaseLike):
    content = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='comment_likes')
