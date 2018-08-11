from rest_framework import serializers


class SqlSerializer(serializers.Serializer):
    query = serializers.CharField()
    params = serializers.CharField(required=False)
