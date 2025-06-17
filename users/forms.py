# users/forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model # Рекомендуется для работы с моделью пользователя

User = get_user_model() # Получаем активную модель пользователя

class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control mb-2', # Добавляем отступ снизу для лучшего вида
            'placeholder': 'Имя пользователя или email'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Пароль'
        })

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Email'}),
        required=True, # Делаем email обязательным
        help_text="Обязательное поле."
    )

    class Meta: # Убрали наследование от UserCreationForm.Meta
        model = User # Указываем модель пользователя
        fields = ('username', 'email') # Включаем username и email в форму

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # for field_name in ('username', 'password1', 'password2'):
        #     if self.fields.get(field_name): # Проверяем, существует ли поле
        #         self.fields[field_name].help_text = ''
        
        self.fields['username'].widget.attrs.update({
            'class': 'form-control mb-2',
            'placeholder': 'Имя пользователя',
   
        })
        # Для полей пароля UserCreationForm уже добавляет placeholder'ы, но мы можем переопределить классы
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control mb-2',
            'placeholder': 'Придумайте пароль',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Повторите пароль',
        })

    # Расширяем логику валидации поля email
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует.")
        return email
    