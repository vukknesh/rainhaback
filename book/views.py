from django.db.models import Q
from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from datetime import datetime, timezone
from django.db.models import Avg, Count, Min, Sum
from rest_framework.filters import (
    SearchFilter,
    OrderingFilter,
)
from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    ListAPIView,
    UpdateAPIView,
    RetrieveAPIView,
    RetrieveUpdateAPIView
)
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.serializers import ValidationError

from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAdminUser,
    IsAuthenticatedOrReadOnly,
)
from django_filters import rest_framework as filters
from book.models import Book, Type, Category, ResumoMensal

from .serializers import (
    BookCreateUpdateSerializer,
    BookDetailSerializer,
    BookListSerializer,
    ResumoSerializer
)


import django_filters
from django.db.models import Q


def infinite_filter(request):
    limit = request.GET.get('limit')
    offset = request.GET.get('offset')
    return Book.objects.all()[int(offset): int(offset) + int(limit)]


def is_there_more_data(request):
    offset = request.GET.get('offset')
    if int(offset) > Book.objects.all().count():
        return False
    return True


class BookFilter(filters.FilterSet):
    multi_name_fields = django_filters.CharFilter(
        method='filter_by_all_name_fields')

    class Meta:
        model = Book
        fields = []

    def filter_by_all_name_fields(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) | Q(description__icontains=value) | Q(
                authors__icontains=value)
        )


class BookCreateAPIView(CreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookCreateUpdateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BookDetailAPIView(RetrieveAPIView):
    queryset = Book.objects.all()
    serializer_class = BookDetailSerializer
    permission_classes = [AllowAny]
    #lookup_url_kwarg = "abc"
    lookup_field = 'id'


class BookUpdateAPIView(RetrieveUpdateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookCreateUpdateSerializer
    # permission_classes = [IsOwnerOrReadOnly]

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)
        # email send_email


class BookDeleteAPIView(DestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookDetailSerializer
    lookup_field = 'id'
    # permission_classes = [IsOwnerOrReadOnly]


class BookListAPIView(ListAPIView):
    pagination_class = LimitOffsetPagination
    serializer_class = BookListSerializer
    # filter_backends = [SearchFilter, OrderingFilter]
    filterset_class = BookFilter
    permission_classes = [AllowAny]
    # search_fields = ['title', 'content', 'user__first_name']

    def get_queryset(self, *args, **kwargs):

        queryset_list = Book.objects.all()  # filter(user=self.request.user)
        query = self.request.GET.get("q")
        if query:
            queryset_list = queryset_list.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(authors__icontains=query)
            ).distinct()
        return queryset_list


# resumo

@api_view(['GET'])
def get_resumo_mes(request):
    now = datetime.now(timezone.utc)
    year = now.year
    month = now.month
    list = []

    for cat in Category.objects.all():

        total_compra = Book.objects.filter(
            category__title=cat.title, type__title="Saida/Compra").filter(data__year__gte=year,
                                                                          data__month__gte=month,
                                                                          data__year__lte=year,
                                                                          data__month__lte=month).aggregate(soma=Sum('price'))
        total_venda = Book.objects.filter(
            category__title=cat.title, type__title="Entrada/Venda").filter(data__year__gte=year,
                                                                           data__month__gte=month,
                                                                           data__year__lte=year,
                                                                           data__month__lte=month).aggregate(soma=Sum('price'))
        total_compra_quantidade = Book.objects.filter(
            category__title=cat.title, type__title="Saida/Compra").filter(data__year__gte=year,
                                                                          data__month__gte=month,
                                                                          data__year__lte=year,
                                                                          data__month__lte=month).aggregate(quant=Sum('quantidade'))
        total_venda_quantidade = Book.objects.filter(
            category__title=cat.title, type__title="Entrada/Venda").filter(data__year__gte=year,
                                                                           data__month__gte=month,
                                                                           data__year__lte=year,
                                                                           data__month__lte=month).aggregate(quant=Sum('quantidade'))

        dict = {}

        if total_compra['soma'] is None:
            total_compra['soma'] = 0
        if total_compra_quantidade['quant'] is None:
            total_compra_quantidade['quant'] = 0
        if total_venda_quantidade['quant'] is None:
            total_venda_quantidade['quant'] = 0
        if total_venda['soma'] is None:
            total_venda['soma'] = 0
        saldo = total_venda['soma'] - total_compra['soma']
        dict['nome'] = cat.title
        dict['saldo'] = saldo
        dict['quantidade_venda'] = total_venda_quantidade['quant']
        dict['quantidade_compra'] = total_compra_quantidade['quant']
        list.append(dict)
        print(f'list = {list}')

    total = sum(item['saldo'] for item in list)

    return Response({
        "resumo": list,
        "saldo_mes": total
    })


def task_resumo_mensal():

    now = datetime.now(timezone.utc)
    year = now.year
    month = now.month

    for cat in Category.objects.all():

        total_compra = Book.objects.filter(
            category__title=cat.title, type__title="Saida/Compra").filter(data__year__gte=year,
                                                                          data__month__gte=month,
                                                                          data__year__lte=year,
                                                                          data__month__lte=month).aggregate(soma=Sum('price'))
        total_venda = Book.objects.filter(
            category__title=cat.title, type__title="Entrada/Venda").filter(data__year__gte=year,
                                                                           data__month__gte=month,
                                                                           data__year__lte=year,
                                                                           data__month__lte=month).aggregate(soma=Sum('price'))

        if total_compra['soma'] is None:
            total_compra['soma'] = 0.0

        if total_venda['soma'] is None:
            total_venda['soma'] = 0.0
        saldo = total_venda['soma'] - total_compra['soma']

        ResumoMensal.objects.create(nome=cat.title, saldo=saldo)


@api_view(['GET'])
def get_all_resumo(request):

    group_by_value = {}
    value_list = ResumoMensal.objects.values_list(
        'data', flat=True
    ).distinct()
    group_by_value = {}

    for value in value_list:

        v_date = str(value.month)+"/"+str(value.year)

        group_by_value[v_date] = ResumoSerializer(
            ResumoMensal.objects.filter(data=value), many=True).data

    return Response({"resumo": group_by_value})


@api_view(['GET'])
def teste_resumo_mensal(request):
    print('hello')
    now = datetime.now(timezone.utc)
    year = now.year
    month = now.month
    print('dentro')

    for cat in Category.objects.all():
        print(f'categoria = {cat.title}')
        total_compra = Book.objects.filter(
            category__title=cat.title, type__title="Saida/Compra").filter(data__year__gte=year,
                                                                          data__month__gte=month,
                                                                          data__year__lte=year,
                                                                          data__month__lte=month).aggregate(soma=Sum('price'))
        total_venda = Book.objects.filter(
            category__title=cat.title, type__title="Entrada/Venda").filter(data__year__gte=year,
                                                                           data__month__gte=month,
                                                                           data__year__lte=year,
                                                                           data__month__lte=month).aggregate(soma=Sum('price'))

        if total_compra['soma'] is None:
            total_compra['soma'] = 0.0

        if total_venda['soma'] is None:
            total_venda['soma'] = 0.0
        saldo = total_venda['soma'] - total_compra['soma']
        print(f'saldo = {saldo}')

        ResumoMensal.objects.create(nome=cat.title, saldo=saldo, data=now)
