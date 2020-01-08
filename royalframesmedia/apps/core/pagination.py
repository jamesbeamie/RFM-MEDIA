from rest_framework.pagination import PageNumberPagination


class PaginateContent(PageNumberPagination):
    """
        Custom pagination class
    """
    page_size = 150
    page_size_query_param = 'page_size'
