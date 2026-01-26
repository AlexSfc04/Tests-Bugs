from django import forms
from .models import Book

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = '__all__'
        widgets = {
            "published_date": forms.DateInput(attrs={"type": "date"}),
            "read_date": forms.DateInput(attrs={"type": "date"}),
            "authors": forms.CheckboxSelectMultiple()
        }
        error_messages = {
            "title": {
                "max_length": "The title must be less than 50 characters long",
                "required": "The title is mandatory"
            }
        }
    
    # BUG FIX: Added clean() method - the form was missing validation for read_date vs published_date
    # Without this, the validation only happens at model level after save, not during form validation
    def clean(self):
        super().clean()
        read_date = self.cleaned_data.get('read_date')
        published_date = self.cleaned_data.get('published_date')
        
        if read_date and published_date and read_date < published_date:
            self.add_error('read_date', 'The read date must be after the published date')