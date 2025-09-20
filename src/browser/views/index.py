"""The index view."""
from django.views import View
from django.shortcuts import render


class IndexView(View):
    """Implements the index view."""

    def get(self, request):
        """Handle the GET request.

        Parameters
        ----------
        request: HttpRequest, required
            The request object.
        """
        return render(request, "index.html")
