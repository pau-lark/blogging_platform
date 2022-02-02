from .models import Post
from django import forms


class SearchForm(forms.Form):
    search = forms.CharField(max_length=50, label='')


class PostCreationForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('category', 'title', 'poster')
        widgets = {
            'poster': forms.FileInput(attrs={'onchange': 'loadImage(event)'})
        }
