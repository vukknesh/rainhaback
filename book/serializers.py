from rest_framework.serializers import (
    HyperlinkedIdentityField,
    ModelSerializer,
    SerializerMethodField,
    CharField,
    ImageField,
    SlugField
)

from accounts.serializers import UserSerializer

from book.models import Book, ResumoMensal


class BookCreateUpdateSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Book
        fields = [
            'id',
            'image',
            'price',
            'quantidade',
            'data',
            'user',

        ]


class BookDetailSerializer(ModelSerializer):

    user = UserSerializer(read_only=True)
    image = SerializerMethodField()

    class Meta:
        model = Book
        fields = [
            'id',
            'image',
            'quantidade',
            'data',
            'category',
            'type',
            'price',
            'user',
            'buyer',
            'seller',
        ]

    def get_image(self, obj):
        try:
            image = obj.image.url
        except:
            image = None
        return image


class BookListSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Book
        fields = [
            'id',
            'image',
            'quantidade',
            'data',
            'category',
            'type',
            'price',
            'user',
            'buyer',
            'seller',
        ]


class ResumoSerializer(ModelSerializer):

    class Meta:
        model = ResumoMensal
        fields = "__all__"
