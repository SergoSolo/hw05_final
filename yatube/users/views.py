from django.urls import reverse_lazy
from django.views.generic.edit import CreateView

from .forms import CreationForm


class SignUp(CreateView):
    form_class = CreationForm
    template_name = 'users/signup.html'
    success_url = reverse_lazy('posts:index')
