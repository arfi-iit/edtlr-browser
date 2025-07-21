VENV           = .venv
VENV_BIN       = $(VENV)/bin
VENV_PYTHON    = $(VENV_BIN)/python
VENV_PIP       = $(VENV_BIN)/pip

clean:
	rm -rf "$(VENV)";

venv: clean
	python3.11 -m venv $(VENV);
	$(VENV_PIP) install -U pip;
	if [ -f requirements.txt ]; then \
		$(VENV_PIP) install -r requirements.txt; \
	else \
		$(VENV_PIP) install django \
				psycopg2-binary; \
		$(VENV_PIP) freeze > requirements.txt; \
	fi; \

dev-venv: venv
	if [ -f requirements-dev.txt ]; then \
		$(VENV_PIP) install -r requirements-dev.txt; \
	else \
		$(VENV_PIP) install python-lsp-server[all] \
				yapf \
				cmake-language-server \
				autotools-language-server; \
		$(VENV_PIP) freeze > requirements-dev.txt; \
		sed -i '/^## The following/,+1d' requirements-dev.txt; \
	fi; \
