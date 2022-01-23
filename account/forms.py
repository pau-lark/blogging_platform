from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser


# Переопределение форм создания и изменения юзера
class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('birth_date', 'photo')


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = UserChangeForm.Meta.fields


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')
    password2 = forms.CharField(widget=forms.PasswordInput, label='Повторите пароль')

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'birth_date')

    def clean_password2(self):
        password, password2 = self.cleaned_data['password'], self.cleaned_data['password2']
        if password != password2:
            raise forms.ValidationError('Пароли не совпадают')
        return password2
