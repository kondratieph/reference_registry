from rest_framework import serializers

from reference_registry.models import ReferenceBook, ReferenceBookItem


class ReferenceBookSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)

    class Meta:
        model = ReferenceBook
        fields = ('id', 'code', 'name',)


class ReferenceBookItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferenceBookItem
        fields = ('code', 'value',)
