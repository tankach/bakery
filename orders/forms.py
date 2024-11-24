from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.validators import RegexValidator
from .models import CustomUser
from django import forms

class CommentForm(forms.Form):
    name = forms.CharField(max_length=100)
    comment = forms.CharField(widget=forms.Textarea)

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, help_text="Введіть ваше ім'я.")
    last_name = forms.CharField(max_length=30, required=True, help_text="Введіть ваше прізвище.")
    phone_number = forms.CharField(
        max_length=15,
        required=True,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'Невірний формат номера телефону')],
        help_text='Введіть ваш номер телефону у форматі +380123456789.'
    )
    address = forms.CharField(max_length=255, required=True, help_text='Введіть вашу адресу проживання.')

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'phone_number', 'address', 'password1', 'password2')


class EditProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone_number = forms.CharField(max_length=15, required=True)
    address = forms.CharField(max_length=255, required=True)

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'phone_number', 'address']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone_number = self.cleaned_data['phone_number']
        user.address = self.cleaned_data['address']

        if commit:
            user.save()
        return user
