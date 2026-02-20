from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Avg, Max, Min, Count
import json

from bookapp.forms import BookForm
from bookapp.models import Book


class BookCreate(LoginRequiredMixin, CreateView):
    model = Book
    form_class = BookForm
    template_name = 'bookapp/form.html'
    success_url = reverse_lazy('book_list')


class BookUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'bookapp.change_book'
    model = Book
    form_class = BookForm
    template_name = 'bookapp/form.html'
    success_url = reverse_lazy('book_list')


class BookDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'bookapp.delete_book'
    model = Book
    template_name = 'bookapp/confirm_delete.html'
    success_url = reverse_lazy('book_list')


class BookDetail(LoginRequiredMixin, DetailView):
    model = Book
    template_name = 'bookapp/detail.html'
    context_object_name = 'book'


def book_list(request):
    VALID_ORDER_FIELDS = ['title', 'pages', 'rating', 'status', 'published_date',
                          '-title', '-pages', '-rating', '-status', '-published_date']

    title_filter = request.GET.get('title', '')
    order_by = request.GET.get('order_by', 'title')

    if order_by not in VALID_ORDER_FIELDS:
        order_by = 'title'

    books = Book.objects.all()

    if title_filter:
        books = books.filter(title__icontains=title_filter)

    books = books.order_by(order_by)

    paginator = Paginator(books, 5)  # 5 libros por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'bookapp/list.html', {
        'page_obj': page_obj,
        'title_filter': title_filter,
        'order_by': order_by,
    })


def stats(request):
    max_pages = Book.objects.order_by('-pages').first()
    min_pages = Book.objects.order_by('pages').first()
    avg_pages = Book.objects.aggregate(avg=Avg('pages'))['avg'] or 0
    avg_rating = Book.objects.aggregate(avg=Avg('rating'))['avg'] or 0

    # Datos para gráfico de tarta (status)
    status_data = Book.objects.values('status').annotate(count=Count('id'))
    status_labels = [d['status'] for d in status_data]
    status_counts = [d['count'] for d in status_data]

    # Datos para gráfico de barras (rating)
    rating_data = Book.objects.filter(rating__isnull=False).values('rating').annotate(count=Count('id')).order_by('rating')
    rating_labels = [str(d['rating']) for d in rating_data]
    rating_counts = [d['count'] for d in rating_data]

    return render(request, 'bookapp/stats.html', {
        'max_pages': max_pages,
        'min_pages': min_pages,
        'avg_pages': round(avg_pages, 2),
        'avg_rating': round(avg_rating, 2),
        'status_labels': json.dumps(status_labels),
        'status_counts': json.dumps(status_counts),
        'rating_labels': json.dumps(rating_labels),
        'rating_counts': json.dumps(rating_counts),
    })


def register(request):
    form = UserCreationForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('book_list')
    return render(request, 'bookapp/form.html', {'form': form})
