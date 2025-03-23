from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    객체의 소유자만 수정할 수 있도록 하는 권한
    """
    def has_object_permission(self, request, view, obj):
        # 읽기 권한은 모든 요청에 허용
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # 쓰기 권한은 객체의 소유자에게만 허용
        return obj.user == request.user or obj.creator == request.user 