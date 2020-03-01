from __future__ import unicode_literals

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.db.models import Avg
from markdown_deux import markdown

from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys


class ResumoMensal(models.Model):
    data = models.DateTimeField()
    nome = models.CharField(max_length=255, default="", null=True, blank=True)
    saldo = models.FloatField()

    def __str__(self):
        return f'{self.data.month}/{self.data.year} - R$  {self.saldo} '


class Buyer(models.Model):
    name = models.CharField(max_length=255, default='')
    email = models.CharField(max_length=100, default='', null=True, blank=True)
    tel = models.CharField(max_length=50, default='', null=True, blank=True)
    address = models.CharField(
        max_length=255, default='', null=True, blank=True)

    def __str__(self):
        return str(self.name)


class Seller(models.Model):
    name = models.CharField(max_length=255, default='')
    email = models.CharField(max_length=100, default='', null=True, blank=True)
    tel = models.CharField(max_length=50, default='', null=True, blank=True)
    address = models.CharField(
        max_length=255, default='', null=True, blank=True)

    def __str__(self):
        return str(self.name)


class Category(models.Model):
    title = models.CharField(max_length=255, default='')

    def __str__(self):
        return str(self.title)


class Type(models.Model):
    title = models.CharField(max_length=255, default='')

    def __str__(self):
        return str(self.title)


class Book(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)

    type = models.ForeignKey(Type, on_delete=models.CASCADE)
    data = models.DateField(auto_now=False, auto_now_add=False)
    price = models.FloatField(null=True, blank=True)

    image = models.ImageField(
        upload_to='books_pics')

    quantidade = models.FloatField(null=True, blank=True)

    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    buyer = models.ForeignKey(
        Buyer, null=True, blank=True, on_delete=models.CASCADE)
    seller = models.ForeignKey(
        Seller, null=True, blank=True, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self):
        # Opening the uploaded image
        im = Image.open(self.image)

        output = BytesIO()

        # Resize/modify the image
        im = im.resize((200, 200))

        # after modifications, save it to the output
        im.save(output, format='JPEG', quality=91)
        output.seek(0)

        # change the imagefield value to be the newley modifed image value
        self.image = InMemoryUploadedFile(output, 'ImageField', "%s.jpg" % self.image.name.split(
            '.')[0], 'image/jpeg', sys.getsizeof(output), None)

        super(Book, self).save()

    def __unicode__(self):
        return str(self.data)

    def __str__(self):
        return str(f'{self.data} - {self.category.title} - {self.price}')

    def get_absolute_url(self):
        return reverse("books:thread", kwargs={"slug": self.slug})

    def get_delete_url(self):
        return reverse("books:delete", kwargs={"id": self.id})
