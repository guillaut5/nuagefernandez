from rest_framework.pagination import PageNumberPagination


class FifteenPerPagePagination(PageNumberPagination):
    page_size = 15
