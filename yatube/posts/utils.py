from django.core.paginator import Paginator


def paginate_queryset(request, posts, count):
    paginator = Paginator(posts, count)
    page_number = request.GET.get('page')

    return paginator.get_page(page_number)
