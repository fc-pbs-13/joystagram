from rest_framework import pagination


class IDPagination(pagination.CursorPagination):
    ordering = '-id'
