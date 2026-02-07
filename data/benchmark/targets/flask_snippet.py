class Flask:
    """The flask object implements a WSGI application."""
    def __init__(self, import_name):
        self.import_name = import_name
        self.routes = {}

    def route(self, rule, **options):
        """A decorator that is used to register a view function for a
        given URL rule.
        """
        def decorator(f):
            self.routes[rule] = f
            return f
        return decorator

    def run(self, host=None, port=None, debug=None, **options):
        """Runs the application on a local development server."""
        print(f"Running on http://{host or '127.0.0.1'}:{port or 5000}/")

def render_template(template_name_or_list, **context):
    """Renders a template from the template folder with the given
    context.
    """
    return f"Rendered {template_name_or_list}"
