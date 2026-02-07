import collections
import datetime

class Session:
    """A Requests session."""
    def __init__(self):
        self.headers = collections.OrderedDict()
        self.cookies = {}
        self.auth = None

    def get(self, url, **kwargs):
        """Sends a GET request."""
        return self.request('GET', url, **kwargs)

    def post(self, url, data=None, json=None, **kwargs):
        """Sends a POST request."""
        return self.request('POST', url, data=data, json=json, **kwargs)

    def request(self, method, url, **kwargs):
        # Implementation details omitted for brevity
        print(f"Requesting {method} {url}")
        return "Response Object"

def get(url, params=None, **kwargs):
    """Sends a GET request.
    
    :param url: URL for the new :class:`Request` object.
    :param params: (optional) Dictionary, list of tuples or bytes to send
        in the query string for the :class:`Request`.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
    """
    with Session() as session:
        return session.get(url, params=params, **kwargs)
