from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method !='POST':
            return True
        print('In permissions class and method is POST')
        # Write permissions are only allowed to the owner of the snippet.
        return request.user =='vesko'

class IsAuthenticatedOrPOSTmethod(permissions.BasePermission):
    """
    The request is authenticated as a user, or is a POST request.
    """

    def has_permission(self, request, view):
        # print('Hello from permissions method:%s'% (request.method))
        if (request.method == 'POST' or
            request.user and
            request.user.is_authenticated):
            return True
        return False