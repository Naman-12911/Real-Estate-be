from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
import math
class CommonPagination(PageNumberPagination):
    page_size = 50  # Set the number of items per page
    page_size_query_param = 'page_size'
    max_page_size = 1000  # Set the maximum page size to prevent abuse


    def get_paginated_response(self, data):
        total_count = self.page.paginator.count
        page_size = self.get_page_size(self.request)
        total_pages = math.ceil(total_count / page_size)
        
        return Response({
            
            'count': total_count,
            'total_pages': total_pages,
            'results': data
        })
