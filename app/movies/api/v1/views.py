from django.contrib.postgres.aggregates import ArrayAgg
from django.db import models
from django.http import JsonResponse
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView
from movies.models import Filmwork, RoleType


class MoviesApiMixin:
    model = Filmwork
    http_method_names = ["get"]

    def get_queryset(self):
        return self.model.objects.values(
            "id",
            "title",
            "description",
            "creation_date",
            "rating",
            "type",
        ).annotate(
            genres=ArrayAgg("genres__name", distinct=True),
            actors=ArrayAgg(
                "persons__full_name",
                filter=models.Q(personfilmwork__role=RoleType.ACTOR),
                distinct=True,
            ),
            directors=ArrayAgg(
                "persons__full_name",
                filter=models.Q(personfilmwork__role=RoleType.DIRECTOR),
                distinct=True,
            ),
            writers=ArrayAgg(
                "persons__full_name",
                filter=models.Q(personfilmwork__role=RoleType.WRITER),
                distinct=True,
            ),
        )

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class MoviesListApi(MoviesApiMixin, BaseListView):
    paginate_by = 50

    def get_context_data(self, *, object_list=None, **kwargs):
        paginator, page, queryset, is_paginated = self.paginate_queryset(
            self.get_queryset(),
            self.paginate_by,
        )
        page_obj = paginator.page(page.number)
        next_page = page_obj.next_page_number() if page_obj.has_next() else None
        previous_page = (
            page_obj.previous_page_number() if page_obj.has_previous() else None
        )
        return {
            "count": paginator.count,
            "total_pages": paginator.num_pages,
            "next": next_page,
            "prev": previous_page,
            "results": list(queryset),
        }


class MovieDetailApi(MoviesApiMixin, BaseDetailView):
    pk_url_kwarg = "id"

    def get_context_data(self, **kwargs):
        if self.object:
            return self.object
        return JsonResponse(reason=404)
