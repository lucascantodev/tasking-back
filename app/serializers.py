from django.contrib.auth.models import Group, User
from rest_framework import serializers
from app.models import List, Task


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "email", "date_joined"]


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "email", "password", "date_joined"]
        extra_kwargs = {
            "id": {"read_only": True},
            "password": {"write_only": True},
            "date_joined": {"read_only": True},
        }

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data["password"])
        user.username = user.email
        user.save()
        return user


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ["url", "name"]


class ListSerializer(serializers.ModelSerializer):
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    updatedAt = serializers.DateTimeField(source="updated_at", read_only=True)
    
    class Meta:
        model = List
        fields = [
            "id",
            "name",
            "description",
            "priority",
            "status",
            "createdAt",
            "updatedAt",
        ]


class TaskSerializer(serializers.ModelSerializer):
    listId = serializers.IntegerField(source="list.id", read_only=True)
    isComplete = serializers.BooleanField(source="is_complete", required=False)
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    updatedAt = serializers.DateTimeField(source="updated_at", read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "listId",
            "name",
            "description",
            "priority",
            "status",
            "isComplete",
            "createdAt",
            "updatedAt",
        ]
