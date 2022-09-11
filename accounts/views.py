from django.urls import reverse_lazy
from django.views import generic
from core.forms import MyUserCreationForm


class SignUpView(generic.CreateView):
    form_class = MyUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"
