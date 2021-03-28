from django.urls import path

from rest_framework.authtoken import views as authtoken_views
from uni_db.views_meta import UniDB

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="EQAR Contact DB",
        default_version='v3',
        description="EQAR internal database",
        terms_of_service="https://www.eqar.eu/",
        contact=openapi.Contact(email="admin@eqar.eu"),
        license=openapi.License(name="GPL"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path(r'login/', authtoken_views.obtain_auth_token),
    path(r'system/tables/', UniDB.TableList.as_view()),
    path(r'system/queries/', UniDB.QueryList.as_view()),
    UniDB.table_path(),
    path(r'swagger<format>', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path(r'swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path(r'redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

