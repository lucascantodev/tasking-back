from django.urls import include, path
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from app import views

router = routers.DefaultRouter()
router.register(r"users", views.UserViewSet)
router.register(r"groups", views.GroupViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path("", include(router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Lists endpoints
    path("lists/", views.ListCreateListView.as_view(), name="list_create_list"),
    path(
        "lists/<int:pk>/",
        views.ListFindUpdateDeleteView.as_view(),
        name="list_find_update_delete",
    ),
    # Tasks endpoints
    path(
        "lists/<int:list_pk>/tasks/",
        views.TaskCreateListView.as_view(),
        name="task_list_create",
    ),
    path(
        "lists/<int:list_pk>/tasks/<int:pk>/",
        views.TaskFindUpdateDeleteView.as_view(),
        name="task_find_update_delete",
    ),
]
