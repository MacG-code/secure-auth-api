from rest_framework.permissions import BasePermission

# Solo para admin
# "has_permission" valida acceso general
class IsAdminUserRole(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


# Para admin o e mismo usuario
# "has_object_permission" valida sobre un objeto en especifico
class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.user.role == 'admin' or obj.id == request.user.id
        )