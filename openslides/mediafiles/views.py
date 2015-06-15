from django.http import HttpResponse

from openslides.config.api import config
from openslides.projector.api import get_active_slide
from openslides.utils.rest_api import ModelViewSet
from openslides.utils.views import (AjaxView, RedirectView)

from .models import Mediafile
from .serializers import MediafileSerializer


class PdfNavBaseView(AjaxView):
    """
    BaseView for the Pdf Ajax Navigation.
    """

    def get_ajax_context(self, *args, **kwargs):
        return {'current_page': self.active_slide['page_num']}

    def load_other_page(self, active_slide):
        """
        Tell connected clients to load an other pdf page.
        """
        config['projector_active_slide'] = active_slide


class PdfNextView(PdfNavBaseView):
    """
    Activate the next Page of a pdf and return the number of the current page.
    """

    def get(self, request, *args, **kwargs):
        """
        Increment the page number by 1.

        If the page number is set in the active slide, we are the value is
        incremented by 1. Otherwise, it is the first page and it is set to 2.
        """
        self.active_slide = get_active_slide()
        if self.active_slide['callback'] == 'mediafile':
            if 'page_num' not in self.active_slide:
                self.active_slide['page_num'] = 2
            else:
                self.active_slide['page_num'] += 1
            self.load_other_page(self.active_slide)
            response = super(PdfNextView, self).get(self, request, *args, **kwargs)
        else:
            # no Mediafile is active and the JavaScript should not do anything.
            response = HttpResponse()
        return response


class PdfPreviousView(PdfNavBaseView):
    """
    Activate the previous Page of a pdf and return the number of the current page.
    """

    def get(self, request, *args, **kwargs):
        """
        Decrement the page number by 1.

        If the page number is set and it is greater than 1, it is decremented
        by 1. Otherwise, it is the first page and nothing happens.
        """
        self.active_slide = get_active_slide()
        response = None
        if self.active_slide['callback'] == 'mediafile':
            if 'page_num' in self.active_slide and self.active_slide['page_num'] > 1:
                self.active_slide['page_num'] -= 1
                self.load_other_page(self.active_slide)
                response = super(PdfPreviousView, self).get(self, request, *args, **kwargs)
        if not response:
            response = HttpResponse()
        return response


class PdfGoToPageView(PdfNavBaseView):
    """
    Activate the page set in the textfield.
    """

    def get(self, request, *args, **kwargs):
        target_page = int(request.GET.get('page_num'))
        self.active_slide = get_active_slide()
        if target_page:
            self.active_slide['page_num'] = target_page
            self.load_other_page(self.active_slide)
            response = super(PdfGoToPageView, self).get(self, request, *args, **kwargs)
        else:
            response = HttpResponse()
        return response


class PdfToggleFullscreenView(RedirectView):
    """
    Toggle fullscreen mode for pdf presentations.
    """
    allow_ajax = True
    url_name = 'core_dashboard'

    def get_ajax_context(self, *args, **kwargs):
        config['pdf_fullscreen'] = not config['pdf_fullscreen']
        return {'fullscreen': config['pdf_fullscreen']}


class MediafileViewSet(ModelViewSet):
    """
    API endpoint to list, retrieve, create, update and destroy mediafile
    objects.
    """
    queryset = Mediafile.objects.all()
    serializer_class = MediafileSerializer

    def check_permissions(self, request):
        """
        Calls self.permission_denied() if the requesting user has not the
        permission to see mediafile objects and in case of create, update or
        destroy requests the permission to manage mediafile objects.
        """
        # TODO: Use mediafiles.can_upload permission to create and update some
        #       objects but restricted concerning the uploader.
        if (not request.user.has_perm('mediafiles.can_see') or
                (self.action in ('create', 'update', 'destroy') and not
                 request.user.has_perm('mediafiles.can_manage'))):
            self.permission_denied(request)