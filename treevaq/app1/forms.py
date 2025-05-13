from django import forms
from .models import CommunityPost, Comment, Review, Question, Answer

# Import Product directly if it's in this app, or reference it if it's in another app
try:
    from .models import Product
except ImportError:
    # If Product is in another app, you might need to import it differently
    # For example:
    # from products_app.models import Product
    pass

class CommunityPostForm(forms.ModelForm):
    class Meta:
        model = CommunityPost
        fields = ['title', 'content', 'category']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Add a comment...'}),
        }
        labels = {
            'content': '',
        }

# Only define this if Product exists in your project
try:
    class ProductPostForm(forms.ModelForm):
        class Meta:
            model = Product
            # Adjust these fields based on your actual Product model structure
            fields = ['name', 'description', 'price', 'image'] 
            widgets = {
                'description': forms.Textarea(attrs={'rows': 5}),
            }
except NameError:
    # If Product isn't imported, create a placeholder
    class ProductPostForm(forms.Form):
        # Define basic fields that match your actual Product model
        name = forms.CharField(max_length=200)
        description = forms.CharField(widget=forms.Textarea(attrs={'rows': 5}))
        price = forms.DecimalField(max_digits=10, decimal_places=2)
        image = forms.ImageField(required=False)

class SellerApplicationForm(forms.Form):
    name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    business_name = forms.CharField(max_length=200, required=True)
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 5}), required=True)

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write your review...'}),
        }

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['title', 'content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe your question...'}),
        }

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Your answer...'}),
        }
        labels = {
            'content': '',
        }