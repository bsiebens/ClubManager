from django.http import HttpRequest
from django.template.response import TemplateResponse as BaseTemplateResponse

class HTMXTemplateResponse(BaseTemplateResponse):
    """Can return an optional small HTML fragment instead of a full HTML page depending on the request headers."""
    
    def get_partial_template(self, request: HttpRequest, template: str, partial_template: str | None = None) -> str:
        if request.htmx:
            if partial_template is None:
                return request.htmx.target
            
            return f"{template}#{partial_template}"
        return template
    
    def __init__(self, request: HttpRequest, template: str, context: dict, partial_template: str | None = None, *args, **kwargs):
        template_name = self.get_partial_template(request, template, partial_template)
        
        super().__init__(request, template_name, context, *args, **kwargs)