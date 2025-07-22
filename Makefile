# Variables
VENV		= .venv
VENV_BIN	= $(VENV)/bin
VENV_PYTHON	= $(VENV_BIN)/python
VENV_PIP	= $(VENV_BIN)/pip

SRC_DIR		= src
APP_NAME	= browser
APP_DIR		= $(SRC_DIR)/$(APP_NAME)

PORT		= 8000

# Recipes
clean:
	rm -rf "$(VENV)";

# Create the virtual environment for running the app
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

# Create the virtual environment for development
dev-venv: venv
	if [ -f requirements-dev.txt ]; then \
		$(VENV_PIP) install -r requirements-dev.txt; \
	else \
		$(VENV_PIP) install python-lsp-server[all] \
				yapf \
				cmake-language-server \
				autotools-language-server; \
		$(VENV_PIP) freeze -r requirements.txt | sed '1,/^## The following/d' > requirements-dev.txt; \
	fi; \

# Create the Django application
app: dev-venv
	if [ ! -d $(SRC_DIR) ]; then \
	    $(VENV_BIN)/django-admin startproject config; \
	    mv config $(SRC_DIR); \
	fi; \
	if [ ! -d $(APP_DIR) ]; then \
	    cd $(SRC_DIR); \
	    ../$(VENV_PYTHON) manage.py startapp $(APP_NAME); \
	fi;

# Run the development server
start: $(SRC_DIR)/manage.py
	$(VENV_PYTHON) $(SRC_DIR)/manage.py runserver 0.0.0.0:$(PORT);
