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
    RegisterSerializer,
    TaskSerializer,
)
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer


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

# Simple wrapper around the TokenObtainPairView that should behave same as the wrapped view but 
# setting refreshToken in cookies and return user data along with 
class TokenObtainPairViewWrapper(APIView):
    def post(self, request):
        serializer = TokenObtainPairSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.get(email=request.data.get("username")) # username doesn't exist on this request
            user_data = UserSerializer(user, context={"request": request}).data
            user_data.pop("password", None)  # removes the field if present
            data = {
                "user": user_data,
                "access": serializer.validated_data["access"],
                "refresh": serializer.validated_data["refresh"]
            }
            response = Response(data, status=status.HTTP_200_OK)
            response.set_cookie(
                key="refreshToken",
                value=serializer.validated_data["refresh"],
                httponly=True,
                secure=True,
                samesite="None",  # required if frontend and backend are on different domains
                max_age=60 * 60 * 24 * 7  # example: 7 days
            )
            return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Simple wrapper around the TokenRefreshView that should behave same as the wrapped view but 
# setting refreshToken in cookies
class TokenRefreshViewWrapper(APIView):
    def post(self, request):
        serializer = TokenRefreshSerializer(data={"refresh": request.COOKIES["refreshToken"]})
        if serializer.is_valid():
            response = Response(serializer.validated_data, status=status.HTTP_200_OK)

            if ("refresh" in serializer.validated_data):
                response.set_cookie(
                    key="refreshToken",
                    value=serializer.validated_data["refresh"],
                    httponly=True,
                    secure=True,
                    samesite="None",  # required if frontend and backend are on different domains
                    max_age=60 * 60 * 24 * 7  # example: 7 days
                )

            return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserMeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(serializer.data)


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user_data = UserSerializer(user, context={"request": request}).data
            token_serializer = TokenObtainPairSerializer(
                data={"username": user.username, "password": request.data.get("password")}
            )
            if token_serializer.is_valid():
                data = {
                    "user": user_data,
                    "access": token_serializer.validated_data["access"],
                    "refresh": token_serializer.validated_data["refresh"]
                }
                response = Response(data, status=status.HTTP_201_CREATED)
                response.set_cookie(
                    key="refreshToken",
                    value=token_serializer.validated_data["refresh"],
                    httponly=True,
                    secure=True,
                    samesite="None",  # required if frontend and backend are on different domains
                    max_age=60 * 60 * 24 * 7  # example: 7 days
                )
                return response
            return Response(token_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class ListCreateListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ListSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    def get(self, request):
        lists = List.objects.filter(user=request.user).order_by("-created_at")
        serializer = ListSerializer(lists, many=True)
        return Response(serializer.data)


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

    def patch(self, request, pk):
        try:
            list_item = List.objects.get(pk=pk)
            if list_item.user != request.user:
                return Response(status=status.HTTP_403_FORBIDDEN)
            serializer = ListSerializer(list_item, data=request.data, partial=True)
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

    def patch(self, request, list_pk, pk):
        try:
            list_item = List.objects.get(pk=list_pk)
            if list_item.user != request.user:
                return Response(status=status.HTTP_403_FORBIDDEN)
            task = Task.objects.get(pk=pk, list=list_item)
            print("Request Data: ", request.data)
            serializer = TaskSerializer(task, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                print("Serializer Data: ", serializer.data)
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

class LogoutView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie("refreshToken")
        return response
