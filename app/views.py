from app.models import List, Task
from django.contrib.auth.models import Group, User
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions, viewsets
from rest_framework import status
from app.serializers import (
    GroupSerializer,
    ListSerializer,
    UserSerializer,
    TaskSerializer,
)
from rest_framework.pagination import PageNumberPagination


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """

    queryset = Group.objects.all().order_by("name")
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


class ListCreateListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ListSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    def get(self, request):
        paginator = PageNumberPagination()
        paginator.page_size = request.query_params.get("limit", 10)
        lists = List.objects.filter(user=request.user)
        result_page = paginator.paginate_queryset(lists, request)
        serializer = ListSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class ListFindUpdateDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            list_item = List.objects.get(pk=pk)
            if list_item.user != request.user:
                return Response(status=status.HTTP_403_FORBIDDEN)
            serializer = ListSerializer(list_item)
            return Response(serializer.data)
        except List.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            list_item = List.objects.get(pk=pk)
            if list_item.user != request.user:
                return Response(status=status.HTTP_403_FORBIDDEN)
            serializer = ListSerializer(list_item, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(
                serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        except List.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            list_item = List.objects.get(pk=pk)
            if list_item.user != request.user:
                return Response(status=status.HTTP_403_FORBIDDEN)
            list_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except List.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class TaskCreateListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, list_pk):
        try:
            list_item = List.objects.get(pk=list_pk, user=request.user)
            serializer = TaskSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(list=list_item)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(
                serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        except List.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def get(self, request, list_pk):
        try:
            list_item = List.objects.get(pk=list_pk)
            if list_item.user != request.user:
                return Response(status=status.HTTP_403_FORBIDDEN)
            tasks = Task.objects.filter(list=list_item)
            serializer = TaskSerializer(tasks, many=True)
            return Response(serializer.data)
        except List.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class TaskFindUpdateDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, list_pk, pk):
        try:
            list_item = List.objects.get(pk=list_pk)
            if list_item.user != request.user:
                return Response(status=status.HTTP_403_FORBIDDEN)
            task = Task.objects.get(pk=pk, list=list_item)
            serializer = TaskSerializer(task)
            return Response(serializer.data)
        except (List.DoesNotExist, Task.DoesNotExist):
            return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, list_pk, pk):
        try:
            list_item = List.objects.get(pk=list_pk)
            if list_item.user != request.user:
                return Response(status=status.HTTP_403_FORBIDDEN)
            task = Task.objects.get(pk=pk, list=list_item)
            serializer = TaskSerializer(task, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(
                serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        except (List.DoesNotExist, Task.DoesNotExist):
            return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, list_pk, pk):
        try:
            list_item = List.objects.get(pk=list_pk)
            if list_item.user != request.user:
                return Response(status=status.HTTP_403_FORBIDDEN)
            task = Task.objects.get(pk=pk, list=list_item)
            task.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except (List.DoesNotExist, Task.DoesNotExist):
            return Response(status=status.HTTP_404_NOT_FOUND)
