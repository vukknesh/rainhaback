from django.conf.urls import url
from django.contrib import admin

from .views import (
    BookCreateAPIView,
    BookDeleteAPIView,
    BookDetailAPIView,
    BookListAPIView,
    BookUpdateAPIView,
    get_resumo_mes,
    get_all_resumo,
    teste_resumo_mensal
)

urlpatterns = [
    url(r'^$', BookListAPIView.as_view(), name='list'),
    url(r'^create/$', BookCreateAPIView.as_view(), name='create'),
    url(r'^resumo-mes/$', get_resumo_mes, name='resumo'),
    url(r'^teste/$', teste_resumo_mensal, name='teste'),
    url(r'^resumo-all/$', get_all_resumo, name='res-all'),
    url(r'^(?P<id>[\w-]+)/$', BookDetailAPIView.as_view(), name='detail'),
    url(r'^(?P<id>[\w-]+)/edit/$',
        BookUpdateAPIView.as_view(), name='update'),
    url(r'^(?P<id>[\w-]+)/delete/$',
        BookDeleteAPIView.as_view(), name='delete'),


]
