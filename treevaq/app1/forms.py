from django import forms
from .models import CommunityPost, Product

class ProductPostForm(forms.ModelForm):
    class Meta:
        model = CommunityPost
        fields = ['product', 'content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Share your thoughts about this product...'}),
        }

    def save(self, user, commit=True):
        instance = super().save(commit=False)
        instance.user = user
        instance.post_type = 'PRODUCT_POST'
        if commit:
            instance.save()
        return instance

class ReviewForm(forms.ModelForm):
    rating = forms.IntegerField(min_value=1, max_value=5, widget=forms.NumberInput(attrs={'min': 1, 'max': 5}))

    class Meta:
        model = CommunityPost
        fields = ['product', 'content', 'rating']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Write your review...'}),
        }

    def save(self, user, commit=True):
        instance = super().save(commit=False)
        instance.user = user
        instance.post_type = 'REVIEW'
        if commit:
            instance.save()
        return instance

class QuestionForm(forms.ModelForm):
    class Meta:
        model = CommunityPost
        fields = ['product', 'content']
        widgets = {
            'product': forms.Select(attrs={'class': 'optional'}),
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Ask a question...'}),
        }

    def save(self, user, commit=True):
        instance = super().save(commit=False)
        instance.user = user
        instance.post_type = 'QUESTION'
        if commit:
            instance.save()
        return instance

class AnswerForm(forms.ModelForm):
    class Meta:
        model = CommunityPost
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Provide an answer...'}),
        }

    def save(self, user, parent, commit=True):
        instance = super().save(commit=False)
        instance.user = user
        instance.post_type = 'ANSWER'
        instance.parent = parent
        if commit:
            instance.save()
        return instance