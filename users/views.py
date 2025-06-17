"""Представления для работы с пользователями: регистрация, аутентификация, профиль."""

from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import UserRegisterForm, UserLoginForm, UserProfileUpdateForm
from django.shortcuts import redirect, render, get_object_or_404
from .models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from .forms import UserPasswordChangeForm


class UserRegisterView(CreateView):
    """Представление для регистрации новых пользователей."""

    form_class = UserRegisterForm
    template_name = "users/register.html"
    success_url = reverse_lazy("landing")

    def dispatch(self, request, *args, **kwargs):
        """Перенаправляет аутентифицированных пользователей на главную страницу."""
        if request.user.is_authenticated:
            return redirect("landing")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """Обрабатывает валидную форму: сохраняет пользователя и выполняет автоматический вход."""
        response = super().form_valid(form)
        user = form.save()  # Получаем сохраненного пользователя из формы
        login(self.request, user)
        messages.success(
            self.request,
            f"Добро пожаловать, {user.username}! Регистрация прошла успешно.",
        )
        return response

    def form_invalid(self, form):
        """Обрабатывает невалидную форму: выводит сообщение об ошибке."""
        messages.error(
            self.request, "Пожалуйста, исправьте ошибки в форме регистрации."
        )
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        """Добавляет заголовок страницы в контекст."""
        context = super().get_context_data(**kwargs)
        context["title"] = "Регистрация"
        return context


class UserLoginView(LoginView):
    """Представление для аутентификации пользователей."""

    template_name = "users/login.html"
    form_class = UserLoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        """Определяет URL для перенаправления после успешного входа."""
        messages.success(self.request, f"С возвращением, {self.request.user.username}!")
        next_url = self.request.GET.get("next")
        return next_url or reverse_lazy("landing")

    def form_invalid(self, form):
        """Обрабатывает невалидную форму: выводит сообщение об ошибке."""
        messages.error(
            self.request, "Неверное имя пользователя или пароль. Попробуйте снова."
        )
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        """Добавляет заголовок страницы в контекст."""
        context = super().get_context_data(**kwargs)
        context["title"] = "Вход"
        return context


class UserLogoutView(LogoutView):
    """Представление для выхода пользователей из системы."""

    next_page = reverse_lazy("landing")

    def dispatch(self, request, *args, **kwargs):
        """Добавляет сообщение об успешном выходе для аутентифицированных пользователей."""
        if request.user.is_authenticated:
            messages.info(request, "Вы успешно вышли из системы.")
        return super().dispatch(request, *args, **kwargs)


class UserProfileDetailView(LoginRequiredMixin, DetailView):
    """Представление для просмотра профиля пользователя."""

    model = User
    template_name = "users/profile_detail.html"
    context_object_name = "profile_user"

    def get_context_data(self, **kwargs):
        """Добавляет заголовок и флаг принадлежности профиля в контекст."""
        context = super().get_context_data(**kwargs)
        # self.object содержит объект профиля (экземпляр User)
        context["title"] = f"Профиль: {self.object.username}"
        context["is_own_profile"] = self.request.user == self.object
        return context


class UserPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    """Представление для смены пароля пользователя."""

    template_name = "users/password_change_form.html"
    form_class = UserPasswordChangeForm

    def get_success_url(self):
        """Определяет URL для перенаправления после успешной смены пароля."""
        messages.success(self.request, "Ваш пароль был успешно изменен.")
        return reverse_lazy("users:profile_detail", kwargs={"pk": self.request.user.pk})

    def form_invalid(self, form):
        """Обрабатывает невалидную форму: выводит сообщение об ошибке."""
        messages.error(self.request, "Пожалуйста, исправьте ошибки при смене пароля.")
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        """Добавляет заголовок страницы в контекст."""
        context = super().get_context_data(**kwargs)
        context["title"] = "Смена пароля"
        return context


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Представление для обновления профиля пользователя."""

    model = User
    form_class = UserProfileUpdateForm
    template_name = "users/profile_update_form.html"

    def get_object(self, queryset=None):
        """Возвращает текущего аутентифицированного пользователя для редактирования."""
        return self.request.user

    def get_success_url(self):
        """Определяет URL для перенаправления после успешного обновления профиля."""
        messages.success(self.request, "Ваш профиль успешно обновлен.")
        return reverse_lazy("users:profile_detail", kwargs={"pk": self.request.user.pk})

    def form_invalid(self, form):
        """Обрабатывает невалидную форму: выводит сообщение об ошибке."""
        messages.error(self.request, "Пожалуйста, исправьте ошибки в форме.")
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        """Добавляет заголовок страницы в контекст."""
        context = super().get_context_data(**kwargs)
        context["title"] = "Редактирование профиля"
        return context
