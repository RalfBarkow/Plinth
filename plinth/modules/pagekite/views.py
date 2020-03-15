# SPDX-License-Identifier: AGPL-3.0-or-later

from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import ugettext as _
from django.views.generic import View
from django.views.generic.edit import FormView

from plinth.modules import pagekite

from . import utils
from .forms import (AddCustomServiceForm, ConfigurationForm,
                    DeleteCustomServiceForm)


class ContextMixin(object):
    """Mixin to add 'subsubmenu' and 'title' to the context.

    Also adds the requirement of all necessary packages to be installed
    """
    def get_context_data(self, **kwargs):
        """Use self.title and the module-level subsubmenu"""
        context = super(ContextMixin, self).get_context_data(**kwargs)
        context['app_info'] = pagekite.app.info
        context['title'] = pagekite.app.info.name
        context['is_enabled'] = pagekite.app.is_enabled()
        return context

    def dispatch(self, *args, **kwargs):
        return super(ContextMixin, self).dispatch(*args, **kwargs)


class DeleteServiceView(ContextMixin, View):
    def post(self, request):
        form = DeleteCustomServiceForm(request.POST)
        if form.is_valid():
            form.delete(request)
        return HttpResponseRedirect(reverse('pagekite:index'))


class AddCustomServiceView(FormView):
    """View to add a new custom PageKite service."""
    form_class = AddCustomServiceForm
    template_name = 'pagekite_custom_services.html'
    success_url = reverse_lazy('pagekite:index')

    def get_context_data(self, *args, **kwargs):
        """Return additional context for rendering the template."""
        context = super().get_context_data(*args, **kwargs)
        context['title'] = _('Add custom PageKite service')
        return context

    def form_valid(self, form):
        """Add a custom service."""
        form.save(self.request)
        return super().form_valid(form)


class ConfigurationView(ContextMixin, FormView):
    template_name = 'pagekite_configure.html'
    form_class = ConfigurationForm
    prefix = 'pagekite'
    success_url = reverse_lazy('pagekite:index')

    def get_context_data(self, *args, **kwargs):
        context = super(ConfigurationView,
                        self).get_context_data(*args, **kwargs)
        unused, custom_services = utils.get_pagekite_services()
        for service in custom_services:
            service['form'] = AddCustomServiceForm(initial=service)
        context['custom_services'] = [
            utils.prepare_service_for_display(service)
            for service in custom_services
        ]
        context.update(utils.get_kite_details())
        return context

    def get_initial(self):
        return utils.get_pagekite_config()

    def form_valid(self, form):
        form.save(self.request)
        return super(ConfigurationView, self).form_valid(form)
