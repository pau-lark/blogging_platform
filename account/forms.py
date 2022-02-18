from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    """Переопределение admin-формы создания пользователя"""
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('birth_date', 'photo')


class CustomUserChangeForm(UserChangeForm):
    """Переопределение admin-формы изменения пользователя"""
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'photo']


class RegisterForm(forms.ModelForm):
    """Форма регистрации пользователя"""
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


class ProfileEditForm(forms.ModelForm):
    birth_date = forms.DateField(widget=forms.TextInput(
        attrs={'type': 'date'}
    ))

    class Meta:
        model = CustomUser
        fields = ('username',
                  'first_name',
                  'last_name',
                  'email',
                  'birth_date',
                  'photo',
                  'about')
