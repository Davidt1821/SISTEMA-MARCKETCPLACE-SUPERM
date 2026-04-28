import re

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from .models import CustomerProfile


class CustomerRegistrationForm(forms.Form):
    name = forms.CharField(label='Nome', max_length=150)
    phone = forms.CharField(label='Telefone', max_length=30)
    email = forms.EmailField(label='Email')
    password1 = forms.CharField(label='Senha', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmacao de senha', widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists() or User.objects.filter(username__iexact=email).exists():
            raise forms.ValidationError('Este email ja esta cadastrado.')
        return email

    def clean_phone(self):
        phone = self.cleaned_data['phone'].strip()
        digits = re.sub(r'\D', '', phone)
        if len(digits) < 10:
            raise forms.ValidationError('Informe um telefone valido com DDD.')
        return phone

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('password1') != cleaned_data.get('password2'):
            self.add_error('password2', 'As senhas nao conferem.')
        return cleaned_data

    def save(self):
        email = self.cleaned_data['email']
        name_parts = self.cleaned_data['name'].strip().split(' ', 1)
        user = User.objects.create_user(
            username=email,
            email=email,
            password=self.cleaned_data['password1'],
            first_name=name_parts[0],
            last_name=name_parts[1] if len(name_parts) > 1 else '',
        )
        CustomerProfile.objects.create(user=user, phone=self.cleaned_data['phone'])
        return user


class CustomerLoginForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(label='Senha', widget=forms.PasswordInput)

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.user = None

    def clean(self):
        cleaned_data = super().clean()
        email = (cleaned_data.get('email') or '').strip().lower()
        password = cleaned_data.get('password')
        if email and password:
            self.user = authenticate(self.request, username=email, password=password)
            if self.user is None:
                raise forms.ValidationError('Email ou senha invalidos.')
        return cleaned_data

    def get_user(self):
        return self.user


class CustomerProfileForm(forms.ModelForm):
    name = forms.CharField(label='Nome', max_length=150)
    email = forms.EmailField(label='Email', disabled=True)

    class Meta:
        model = CustomerProfile
        fields = [
            'name',
            'email',
            'phone',
            'default_street',
            'default_number',
            'default_district',
            'default_city',
            'default_complement',
            'default_reference',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = self.instance.user
        self.fields['name'].initial = user.get_full_name() or user.username
        self.fields['email'].initial = user.email

    def clean_phone(self):
        phone = self.cleaned_data['phone'].strip()
        digits = re.sub(r'\D', '', phone)
        if len(digits) < 10:
            raise forms.ValidationError('Informe um telefone valido com DDD.')
        return phone

    def save(self, commit=True):
        profile = super().save(commit=False)
        name_parts = self.cleaned_data['name'].strip().split(' ', 1)
        profile.user.first_name = name_parts[0]
        profile.user.last_name = name_parts[1] if len(name_parts) > 1 else ''
        if commit:
            profile.user.save(update_fields=['first_name', 'last_name'])
            profile.save()
        return profile
