"""The index view."""
from browser.models.entry import Entry
from django.db.models import Q
from django.http import QueryDict
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View
import unicodedata


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
        search_term = request.GET.get('t', None)
        if search_term is None:
            return render(request, self.template_name)
        else:
            search_results = self.__search(search_term)
            return render(request,
                          self.template_name,
                          context={
                              'search_term': search_term,
                              'search_results': search_results
                          })

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
        params = QueryDict(mutable=True)
        params['t'] = term
        base_url = reverse(self.index_page)
        return redirect(f'{base_url}?{params.urlencode()}')

    def __search(self, term: str) -> list[Entry]:
        """Search entries matching the specified term.

        Parameters
        ----------
        term: str, required
            The search term.

        Returns
        -------
        results: list of Entry
            The entries matching the search term.
        """
        normalized_term = self.__to_normalized_form(term)
        query = Q(title_word_normalized__icontains=normalized_term)
        query.add(Q(title_word__icontains=term), Q.OR)
        results = Entry.objects.filter(query).order_by('title_word')
        return list(results)

    def __to_normalized_form(self, term: str) -> str:
        """Convert the provided term to normalized form.

        Parameters
        ----------
        term: str, required
            The term to convert.

        Returns
        -------
        normalized_term: str
            The term in its canonical form.
        """
        nfkd_form = unicodedata.normalize('NFKD', term)
        return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])
