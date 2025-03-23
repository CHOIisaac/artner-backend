class DetailedSerializerMixin:
    """상세 조회 시 다른 시리얼라이저를 사용하기 위한 믹스인"""
    detailed_serializer_class = None
    
    def get_serializer_class(self):
        if self.action == 'retrieve' and self.detailed_serializer_class:
            return self.detailed_serializer_class
        return super().get_serializer_class() 