from django.urls import include, path
from rest_framework import routers

from app import views

router = routers.DefaultRouter()
router.register(r"users", views.UserViewSet)
router.register(r"groups", views.GroupViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    # Additional users endpoints
    path("users/me/", views.UserMeView.as_view(), name="user_me"),
    path("", include(router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    # Login View with token
    path("api/token/", views.TokenObtainPairViewWrapper.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", views.TokenRefreshViewWrapper.as_view(), name="token_refresh"),
    path("api/token/logout/", views.LogoutView.as_view(), name="token_logout"),
    # Additional auth endpoints
    path("api/register/", views.RegisterView.as_view(), name="register"),
    # Lists endpoints
    path("api/lists/", views.ListCreateListView.as_view(), name="list_create_list"),
    path(
        "api/lists/<int:pk>/",
        views.ListFindUpdateDeleteView.as_view(),
        name="list_find_update_delete",
    ),
    # Tasks endpoints
    path(
        "api/lists/<int:list_pk>/tasks/",
        views.TaskCreateListView.as_view(),
        name="task_list_create",
    ),
    path(
        "api/lists/<int:list_pk>/tasks/<int:pk>/",
        views.TaskFindUpdateDeleteView.as_view(),
        name="task_find_update_delete",
    ),
]
