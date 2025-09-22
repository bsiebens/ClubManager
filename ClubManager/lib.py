from django.http import HttpRequest, HttpResponseRedirect
from django.template.response import TemplateResponse as BaseTemplateResponse
from django.urls import reverse


def is_alpine(request: HttpRequest) -> bool:
    return "X-Alpine-Request" in request.headers


class AlpineTemplateResponse(BaseTemplateResponse):
    def get_ajax_template(self, request: HttpRequest, template: str) -> str:
        if is_alpine(request):
            # Use the target ID from the request as the partial name.
            # This allows one view to serve multiple, distinct partials.
            # We fall back to "alpine" as a sensible default.
            partial = request.headers.get("X-Alpine-Target", "alpine")
            return f"{template}#{partial}"

        return template

    def __init__(self, request: HttpRequest, template: str, *args, **kwargs):
        template_name = self.get_ajax_template(request, template)
        super().__init__(request, template_name, *args, **kwargs)


def do_redirect(request: HttpRequest, pattern_name: str | None = None, *args, **kwargs) -> HttpResponseRedirect:
    url = reverse(pattern_name, args=args, kwargs=kwargs)

    return HttpResponseRedirect(url)
