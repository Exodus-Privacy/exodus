from rest_framework import permissions


class IsAuthenticatedOrOptions(permissions.IsAuthenticated):
    """
    Allow unauthenticated OPTIONS requests through.

    CORS preflight requests always omit credentials, so they must be
    answered without requiring authentication (see the Fetch spec).
    """

    def has_permission(self, request, view):
        if request.method == 'OPTIONS':
            return True
        return super().has_permission(request, view)


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        # if request.method in permissions.SAFE_METHODS:
        # return True

        # Write permissions are only allowed to the owner of the snippet.
        return obj.owner == request.user
