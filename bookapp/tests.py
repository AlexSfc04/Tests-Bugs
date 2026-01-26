from django.test import TestCase, Client
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from datetime import date, timedelta
from django.core.exceptions import ValidationError

from bookapp.models import Book, Author
from bookapp.forms import BookForm


class BookModelTests(TestCase):
    """Tests for Book model"""
    
    def setUp(self):
        """Set up test data"""
        self.author = Author.objects.create(name='John', last_name='Doe')
        self.published_date = date(2020, 1, 1)
        self.read_date = date(2021, 1, 1)
    
    def test_book_creation_basic(self):
        """Test correct creation of Book without authors and cover"""
        book = Book.objects.create(
            title='Test Book',
            pages=200,
            status='FI',
            published_date=self.published_date
        )
        self.assertEqual(book.title, 'Test Book')
        self.assertEqual(book.pages, 200)
        self.assertEqual(book.status, 'FI')
        self.assertIsNone(book.rating)
        self.assertIsNone(book.read_date)
    
    def test_book_invalid_pages_zero(self):
        """Test that pages must be at least 1"""
        book = Book(
            title='Test Book',
            pages=0,
            status='PE',
            published_date=self.published_date
        )
        with self.assertRaises(ValidationError):
            book.full_clean()
    
    def test_book_invalid_pages_negative(self):
        """Test that pages cannot be negative"""
        book = Book(
            title='Test Book',
            pages=-5,
            status='PE',
            published_date=self.published_date
        )
        with self.assertRaises(ValidationError):
            book.full_clean()
    
    def test_book_invalid_rating_below_min(self):
        """Test that rating must be at least 1"""
        book = Book(
            title='Test Book',
            pages=100,
            rating=0,
            status='FI',
            published_date=self.published_date
        )
        with self.assertRaises(ValidationError):
            book.full_clean()
    
    def test_book_invalid_rating_above_max(self):
        """Test that rating cannot exceed 5"""
        book = Book(
            title='Test Book',
            pages=100,
            rating=6,
            status='FI',
            published_date=self.published_date
        )
        with self.assertRaises(ValidationError):
            book.full_clean()
    
    def test_book_read_date_before_published_date(self):
        """Test that read_date must be after published_date"""
        book = Book(
            title='Test Book',
            pages=100,
            status='FI',
            published_date=self.published_date,
            read_date=date(2019, 1, 1)  # Before published_date
        )
        with self.assertRaises(ValidationError) as context:
            book.full_clean()
        self.assertIn('read_date', context.exception.error_dict)
        self.assertIn('The read date must be after the published date', 
                    str(context.exception.error_dict['read_date']))
    
    def test_book_read_date_same_as_published_date(self):
        """Test that read_date can be same as published_date"""
        book = Book.objects.create(
            title='Test Book',
            pages=100,
            status='FI',
            published_date=self.published_date,
            read_date=self.published_date
        )
        book.full_clean()  # Should not raise
        self.assertEqual(book.read_date, self.published_date)
    
    def test_book_with_author(self):
        """Test Book with one author"""
        book = Book.objects.create(
            title='Test Book',
            pages=200,
            status='FI',
            published_date=self.published_date
        )
        book.authors.add(self.author)
        self.assertEqual(book.authors.count(), 1)
        self.assertEqual(book.authors.first().name, 'John')
    
    def test_book_with_multiple_authors(self):
        """Test Book with multiple authors"""
        author2 = Author.objects.create(name='Jane', last_name='Smith')
        book = Book.objects.create(
            title='Test Book',
            pages=200,
            status='FI',
            published_date=self.published_date
        )
        book.authors.add(self.author, author2)
        self.assertEqual(book.authors.count(), 2)
    
    def test_book_with_cover_image(self):
        """Test Book with cover image"""
        image = SimpleUploadedFile(
            name='test_cover.jpg',
            content=b'fake image content',
            content_type='image/jpeg'
        )
        book = Book.objects.create(
            title='Test Book',
            pages=200,
            status='FI',
            published_date=self.published_date,
            cover_image=image
        )
        self.assertTrue(book.cover_image)
        self.assertIn('covers/', book.cover_image.name)
    
    def test_book_str_method(self):
        """Test Book __str__ method"""
        book = Book.objects.create(
            title='My Favorite Book',
            pages=300,
            status='FI',
            published_date=self.published_date
        )
        self.assertEqual(str(book), 'My Favorite Book')


# ========== FORM TESTS ==========
class BookFormTests(TestCase):
    """Tests for BookForm"""
    
    def setUp(self):
        """Set up test data"""
        self.author = Author.objects.create(name='John', last_name='Doe')
        self.published_date = date(2020, 1, 1)
        self.valid_data = {
            'title': 'Valid Book',
            'pages': 200,
            'status': 'FI',
            'published_date': self.published_date,
        }
    
    def test_form_valid_basic(self):
        """Test form creation with valid data"""
        form = BookForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
    
    def test_form_invalid_title_too_long(self):
        """Test form with title exceeding 50 characters"""
        data = self.valid_data.copy()
        data['title'] = 'A' * 51
        form = BookForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
    
    def test_form_title_too_long_error_message(self):
        """Test error message for title too long"""
        data = self.valid_data.copy()
        data['title'] = 'B' * 51
        form = BookForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('The title must be less than 50 characters long', 
                    str(form.errors['title']))
    
    def test_form_invalid_title_empty(self):
        """Test form with empty title"""
        data = self.valid_data.copy()
        data['title'] = ''
        form = BookForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
    
    def test_form_title_empty_error_message(self):
        """Test error message for empty title"""
        data = self.valid_data.copy()
        data['title'] = ''
        form = BookForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('The title is mandatory', str(form.errors['title']))
    
    def test_form_invalid_pages_zero(self):
        """Test form with pages = 0"""
        data = self.valid_data.copy()
        data['pages'] = 0
        form = BookForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('pages', form.errors)
    
    def test_form_invalid_pages_negative(self):
        """Test form with negative pages"""
        data = self.valid_data.copy()
        data['pages'] = -10
        form = BookForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('pages', form.errors)
    
    def test_form_invalid_rating_below_min(self):
        """Test form with rating < 1"""
        data = self.valid_data.copy()
        data['rating'] = 0
        form = BookForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('rating', form.errors)
    
    def test_form_invalid_rating_above_max(self):
        """Test form with rating > 5"""
        data = self.valid_data.copy()
        data['rating'] = 6
        form = BookForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('rating', form.errors)
    
    def test_form_rating_optional(self):
        """Test that rating is optional"""
        form = BookForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
    
    def test_form_invalid_read_date_before_published_date(self):
        """Test form with read_date before published_date"""
        data = self.valid_data.copy()
        data['read_date'] = date(2019, 1, 1)
        form = BookForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('read_date', form.errors)
    
    def test_form_read_date_before_published_date_error_message(self):
        """Test error message for read_date before published_date"""
        data = self.valid_data.copy()
        data['read_date'] = date(2019, 12, 31)
        form = BookForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('The read date must be after the published date', 
                     str(form.errors))
    
    def test_form_read_date_optional(self):
        """Test that read_date is optional"""
        form = BookForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
    
    def test_form_with_author(self):
        """Test form with author"""
        data = self.valid_data.copy()
        data['authors'] = [self.author.id]
        form = BookForm(data=data)
        self.assertTrue(form.is_valid())
    
    def test_form_with_cover_image(self):
        """Test form with cover image"""
        image = SimpleUploadedFile(
            name='test_cover.jpg',
            content=b'fake image content',
            content_type='image/jpeg'
        )
        data = self.valid_data.copy()
        form = BookForm(data=data, files={'cover_image': image})
        self.assertTrue(form.is_valid())
    
    def test_form_cover_image_optional(self):
        """Test that cover_image is optional"""
        form = BookForm(data=self.valid_data)
        self.assertTrue(form.is_valid())


# ========== VIEW TESTS ==========
class BookViewsTests(TestCase):
    """Tests for Book views"""
    
    def setUp(self):
        """Set up test users and data"""
        self.client = Client()
        
        # Create admin user with permissions
        self.admin_user = User.objects.create_user(
            username='admin',
            password='adminpass123'
        )
        # Add permissions
        content_type = ContentType.objects.get_for_model(Book)
        add_perm = Permission.objects.get(codename='add_book')
        change_perm = Permission.objects.get(codename='change_book')
        delete_perm = Permission.objects.get(codename='delete_book')
        self.admin_user.user_permissions.add(add_perm, change_perm, delete_perm)
        
        # Create regular authenticated user without permissions
        self.regular_user = User.objects.create_user(
            username='user',
            password='userpass123'
        )
        
        # Create test book
        self.published_date = date(2020, 1, 1)
        self.book = Book.objects.create(
            title='Test Book',
            pages=200,
            status='FI',
            published_date=self.published_date
        )
    
    # LIST VIEW TESTS
    def test_list_view_accessible_anonymous(self):
        """Test that list view is accessible to anonymous users"""
        response = self.client.get(reverse('book_list'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('books', response.context)
    
    def test_list_view_accessible_authenticated(self):
        """Test that list view is accessible to authenticated users"""
        self.client.login(username='user', password='userpass123')
        response = self.client.get(reverse('book_list'))
        self.assertEqual(response.status_code, 200)
    
    # FORM (CREATE) VIEW TESTS
    def test_form_view_redirects_anonymous(self):
        """Test that form view redirects anonymous users"""
        response = self.client.get(reverse('form'), follow=False)
        self.assertEqual(response.status_code, 302)
    
    def test_form_view_forbidden_regular_user(self):
        """Test that form view forbids regular authenticated users (no permission)"""
        self.client.login(username='user', password='userpass123')
        response = self.client.get(reverse('form'), follow=False)
        self.assertEqual(response.status_code, 403)
    
    def test_form_view_accessible_admin_user(self):
        """Test that form view is accessible to admin users"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('form'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
    
    # DETAIL VIEW TESTS
    def test_detail_view_redirects_anonymous(self):
        """Test that detail view redirects anonymous users"""
        response = self.client.get(
            reverse('book_detail', args=[self.book.id]), 
            follow=False
        )
        self.assertEqual(response.status_code, 302)
    
    def test_detail_view_accessible_authenticated_user(self):
        """Test that detail view is accessible to authenticated users"""
        self.client.login(username='user', password='userpass123')
        response = self.client.get(reverse('book_detail', args=[self.book.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['book'].id, self.book.id)
    
    def test_detail_view_accessible_admin_user(self):
        """Test that detail view is accessible to admin users"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('book_detail', args=[self.book.id]))
        self.assertEqual(response.status_code, 200)
    
    # EDIT VIEW TESTS
    def test_edit_view_redirects_anonymous(self):
        """Test that edit view redirects anonymous users"""
        response = self.client.get(
            reverse('book_edit', args=[self.book.id]), 
            follow=False
        )
        self.assertEqual(response.status_code, 302)
    
    def test_edit_view_forbidden_regular_user(self):
        """Test that edit view forbids regular users (no permission)"""
        self.client.login(username='user', password='userpass123')
        response = self.client.get(
            reverse('book_edit', args=[self.book.id]), 
            follow=False
        )
        self.assertEqual(response.status_code, 403)
    
    def test_edit_view_accessible_admin_user(self):
        """Test that edit view is accessible to admin users"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('book_edit', args=[self.book.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['book'].id, self.book.id)
    
    # DELETE VIEW TESTS
    def test_delete_view_redirects_anonymous(self):
        """Test that delete view redirects anonymous users"""
        response = self.client.get(
            reverse('book_delete', args=[self.book.id]), 
            follow=False
        )
        self.assertEqual(response.status_code, 302)
    
    def test_delete_view_forbidden_regular_user(self):
        """Test that delete view forbids regular users (no permission)"""
        self.client.login(username='user', password='userpass123')
        response = self.client.get(
            reverse('book_delete', args=[self.book.id]), 
            follow=False
        )
        self.assertEqual(response.status_code, 403)
    
    def test_delete_view_accessible_admin_user(self):
        """Test that delete view is accessible to admin users"""
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('book_delete', args=[self.book.id]))
        self.assertEqual(response.status_code, 200)