"""The index view."""
from django.http import QueryDict
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View


class IndexView(View):
    """Implements the index view."""

    template_name = "index.html"
    index_page = "browser:index"

    def get(self, request):
        """Handle the GET request.

        Parameters
        ----------
        request: HttpRequest, required
            The request object.
        """
        search_term = request.GET.get('t', '')
        return render(request,
                      self.template_name,
                      context={'search_term': search_term})

    def post(self, request):
        """Handle the POST request.

        Parameters
        ----------
        request: HttpRequest, required
            The request object.
        """
        term = request.POST.get('term')
        if not term:
            return redirect(self.index_page)
        params = QueryDict.fromkeys(['t'], value=term)
        base_url = reverse(self.index_page)
        return redirect(f'{base_url}?{params.urlencode()}')
