from django.views.generic import ListView, DetailView, UpdateView, CreateView
import django_tables2 as tables
from django.db.models.fields import BigAutoField, UUIDField, DateTimeField
from django.db.models.fields.related import ForeignKey, ManyToManyField
from django.db.models.fields.json import JSONField
from django.db.models.fields.files import FileField
from django.urls import reverse
from django.conf import settings

INELIGIBLE_FIELDS = [BigAutoField, UUIDField, ManyToManyField, JSONField, DateTimeField, FileField]

class EasyMixin:
    CRUD_OPERATIONS = ['list', 'detail', 'create', 'update']

    def is_using_default_template(self):
        return self.template_name in ['easy/list.html', 'easy/detail.html', 'easy/create.html', 'easy/update.html']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.is_using_default_template():
            context = self.add_easy_context(context)
        return context
    
    def add_easy_context(self, context):
        if not hasattr(self, 'easy_object_name'):
            context['easy_object_name'] = self.model._meta.model_name.title()
        else:
            context['easy_object_name'] = self.easy_object_name

        if hasattr(self, 'easy_url_prefix'):
            urls = {}
            for operation in self.CRUD_OPERATIONS:
                try:
                    if operation in ['detail', 'update'] and hasattr(self, 'easy_url_field'):
                        urls[operation] = reverse(f'{self.easy_url_prefix}_{operation}', args=[getattr(self.object, self.easy_url_field)])
                    else:
                        urls[operation] = reverse(f'{self.easy_url_prefix}_{operation}')
                except:
                    pass
            context['urls'] = urls

        context['base_template'] = settings.get('EASY_VIEWS_BASE_TEMPLATE', 'base.html')
        context['content_block'] = settings.get('EASY_VIEWS_TEMPLATE_CONTENT_NAME', 'content')
        return context
    
    def get_queryset(self):
        qs = super().get_queryset()
        sort = self.request.GET.get('sort', None)
        if sort:
            return qs.order_by(sort)
        return qs


class EasyFormHelper:

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self, 'formset_class'):
            if self.request.method == 'POST':
                context['formset'] = self.formset_class(self.request.POST, instance=self.object)
            else:
                context['formset'] = self.formset_class(instance=self.object)

        return context
    
    def form_valid(self):
        if hasattr(self, 'formset'):
            self.formset.save()
        return super().form_valid()


class EasyListView(EasyMixin, ListView):
    """
    Will render a list of objects in a table.
    """
    template_name = 'easy/list.html'

    def add_easy_context(self, context):
        context = super().add_easy_context(context)
        class EasyTable(tables.Table):
            class Meta:
                model = self.model
                template_name = 'django_tables2/bootstrap4.html'
                fields = [x.name for x in self.model._meta.fields if x.__class__ not in INELIGIBLE_FIELDS]

        table = EasyTable(self.get_queryset())
        context['table']  = table
        return context
    

class EasyCreateView(EasyMixin, CreateView):
    template_name = 'easy/create.html'

    def add_easy_context(self, context):
        # Placeholder
        return super().add_easy_context(context)


class EasyUpdateView(EasyMixin, UpdateView):

    def add_easy_context(self, context):
        # Placeholder
        return super().add_easy_context(context)


class EasyDetailView(EasyMixin, DetailView):
    template_name = 'easy/detail.html'

    def add_easy_context(self, context):
        context = super().add_easy_context(context)
        context['object_fields'] = {x.name: getattr(self.object, x.name) for x in self.model._meta.fields if x.__class__ not in INELIGIBLE_FIELDS}
        return context