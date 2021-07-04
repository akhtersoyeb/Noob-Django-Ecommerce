from django.views.generic import TemplateView
from products.models import Category

class HomePageView(TemplateView):
    template_name = 'pages/home.html'

    def get_context_data(self, *args, **kwargs):
        context = super(HomePageView, self).get_context_data(*args, **kwargs)
        categories = Category.objects.all() 
        context['categories'] = categories
        return context 