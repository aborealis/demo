"""Database table structure for articles and authors"""
from django.db import models
from my_profile.models import Entity


class Author(models.Model):
    """Blog authors table"""
    entity = models.ForeignKey(Entity, on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=100)
    description = models.TextField(  # Under the article
        max_length=250, blank=True
    )
    image = models.ImageField(upload_to="static/img/profile/", blank=False)
    url = models.CharField(max_length=200)  # Link to author's page

    def __str__(self) -> str:
        return f'{self.name}'


class Post(models.Model):
    """Blog article"""
    entity = models.ForeignKey(Entity, on_delete=models.DO_NOTHING)
    title = models.CharField(max_length=100)
    seo_title = models.CharField(max_length=100)
    seo_description = models.CharField(max_length=200)
    image = models.ImageField(upload_to="static/img/post/", blank=False)
    image_alt = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    abstract = models.TextField(max_length=150)
    author = models.ForeignKey(Author, on_delete=models.PROTECT, blank=False)
    date_published = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    include_astrofont = models.BooleanField(default=False)
    include_math = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f'{self.title}'

    def get_absolute_url(self):
        """Returns the absolute path to the page"""
        return f"/blog/{self.slug}/"
