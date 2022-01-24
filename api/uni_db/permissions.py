from rest_framework import permissions

class IsSuperUser(permissions.BasePermission):
    """
    Allows access only to super users
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)

class AllowReadOnly(permissions.BasePermission):
    """
    Allows read-only access
    """
    def has_permission(self, request, view):
        return bool(request.method in permissions.SAFE_METHODS)

class ObjectOwnerOrReadOnly(permissions.BasePermission):
    """
    Allows full access to object owner (requires owner field in model), r/o otherwise

    NB: Do not OR this class with classes that have no object-level permissions,
        because that will result in True always.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        # otherwise, only object owner
        return bool(obj.owner == request.user)

