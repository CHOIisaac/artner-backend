from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    객체의 소유자만 쓰기 권한을 가지도록 하는 권한 클래스
    """
    
    def has_object_permission(self, request, view, obj):
        # 읽기 권한은 모든 요청에 허용
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # 쓰기 권한은 객체의 소유자에게만 허용
        # obj.user, obj.author 등 다양한 필드명 처리
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'author'):
            return obj.author == request.user
        elif hasattr(obj, 'collection'):
            return obj.collection.user == request.user
        
        # 기본적으로는 권한 거부
        return False 