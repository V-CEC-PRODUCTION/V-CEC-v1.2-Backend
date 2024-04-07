from rest_framework.permissions import IsAuthenticated, AllowAny


class CustomPermissionMixin:
    def get_permissions(self):
        if hasattr(self, 'require_authentication') and self.require_authentication:
            return [IsAuthenticated()]
        return [AllowAny()]
