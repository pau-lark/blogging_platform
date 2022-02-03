from .models import Post
from django import forms
from django.utils.safestring import mark_safe
from PIL import Image


class SearchForm(forms.Form):
    search = forms.CharField(max_length=50, label='')


IMAGE_RESOLUTION = {
    'min': (400, 300),
    'max': (4000, 3000)
}


class PostCreationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['preview_image'].help_text = mark_safe(
            '<div class="text-muted">'
            'Минимальное разрешение: {}x{},<br> '
            'Максимальное разрешение: {}x{}</div>'.format(*IMAGE_RESOLUTION['min'],
                                                          *IMAGE_RESOLUTION['max'])
            )

    class Meta:
        model = Post
        fields = ('category', 'title', 'preview_image')
        widgets = {
            'preview_image': forms.FileInput(attrs={'onchange': 'loadImage(event)'})
        }

    def clean_image(self):
        preview_image = self.cleaned_data['preview_image']
        with Image.open(preview_image) as pil_image:
            min_height, min_width = IMAGE_RESOLUTION['min']
            max_height, max_width = IMAGE_RESOLUTION['max']
            if pil_image.height < min_height or pil_image.width < min_width:
                raise forms.ValidationError('Изображение меньше чем надо')
            if pil_image.height > max_height or pil_image.width > max_width:
                raise forms.ValidationError('Изображение больше чем надо')
        return preview_image
