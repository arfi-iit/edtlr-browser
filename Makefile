# Variables
VENV		= .venv
VENV_BIN	= $(VENV)/bin
VENV_PYTHON	= $(VENV_BIN)/python
VENV_PIP	= $(VENV_BIN)/pip

SRC_DIR		= src
APP_NAME	= browser
APP_DIR		= $(SRC_DIR)/$(APP_NAME)
APP_ROOT	= $(realpath $(SRC_DIR)/..)
LOG_DIR		= logs
PORT		= 8000
STATIC_ROOT	= static
STATIC_URL	= static

NUM_WORKERS	= 4
GUNICORN_PATH	= $(realpath ${VENV_BIN}/gunicorn)
PYTHON_PATH	= $(realpath ${SRC_DIR})

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
				psycopg2-binary \
				python-dotenv \
				gunicorn; \
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

# Make the .env file
dot-env-file: templates/.env.template
	cp templates/.env.template ${SRC_DIR}/.env;
	sed -i "s/__DEBUG__/${DEBUG}/g" ${SRC_DIR}/.env;
	sed -i "s/__SECRET_KEY__/${SECRET_KEY}/g" ${SRC_DIR}/.env;
	sed -i "s~__STATIC_ROOT__~$(STATIC_ROOT)~g" ${SRC_DIR}/.env;
	sed -i "s~__STATIC_URL__~$(STATIC_URL)~g" ${SRC_DIR}/.env;
	sed -i "s~__LOGIN_URL__~$(LOGIN_URL)~g" ${SRC_DIR}/.env;
	sed -i "s/__DATABASE_HOST__/${DATABASE_HOST}/g" ${SRC_DIR}/.env;
	sed -i "s/__DATABASE_NAME__/${DATABASE_NAME}/g" ${SRC_DIR}/.env;
	sed -i "s/__DATABASE_USER__/${DATABASE_USER}/g" ${SRC_DIR}/.env;
	sed -i "s/__DATABASE_PASSWORD__/${DATABASE_PASSWORD}/g" ${SRC_DIR}/.env;
	sed -i "s/__DATABASE_PORT__/${DATABASE_PORT}/g" ${SRC_DIR}/.env;

# Make the socket descriptor file
socket-descriptor: templates/edtlr-browser.socket.template
	rm -f templates/edtlr-browser.socket;
	cp templates/edtlr-browser.socket.template templates/edtlr-browser.socket;

# Make the Gunicorn configuration file
gunicorn-config: templates/gunicorn.conf.py.template
	rm -f templates/gunicorn.conf.py;
	cp templates/gunicorn.conf.py.template templates/gunicorn.conf.py;
	sed -i "s~__GUNICORN_PATH__~$(GUNICORN_PATH)~g" templates/gunicorn.conf.py;
	sed -i "s~__SRC_DIR_PATH__~$(PYTHON_PATH)~g" templates/gunicorn.conf.py;
	sed -i "s/__NUM_WORKERS__/$(NUM_WORKERS)/g" templates/gunicorn.conf.py;

# Make the service descriptor file
service-descriptor: templates/edtlr-browser.service.template
	rm -f templates/edtlr-browser.service;
	cp templates/edtlr-browser.service.template templates/edtlr-browser.service;
	sed -i "s~__GUNICORN_PATH__~$(GUNICORN_PATH)~g" templates/edtlr-browser.service;
	sed -i "s~__SRC_DIR_PATH__~$(PYTHON_PATH)~g" templates/edtlr-browser.service;
	sed -i "s/__USER__/$(USER)/g" templates/edtlr-browser.service;
	sed -i "s/__GROUP__/$(GROUP)/g" templates/edtlr-browser.service;

# Make the Nginx configuration file
nginx-config: templates/edtlr-browser.conf.template
	rm -f edtlr-browser.conf;
	cp templates/edtlr-browser.conf.template templates/edtlr-browser.conf;
	sed -i "s~__STATIC_URL__~$(STATIC_URL)~g" templates/edtlr-browser.conf;
	sed -i "s~__STATIC_ROOT__~$(realpath $(STATIC_ROOT))~g" templates/edtlr-browser.conf;

# Create or update the .po file containing the translation strings
messages: $(SRC_DIR)/manage.py
	if [ ! -d $(APP_DIR)/locale ]; then \
	    mkdir $(APP_DIR)/locale; \
	fi; \
	$(VENV_BIN)/django-admin makemessages --locale ro;

# Compile the translations
translations: $(APP_DIR)/locale/ro/LC_MESSAGES/django.po
	$(VENV_BIN)/django-admin compilemessages;

# Make migrations
migrations: $(SRC_DIR)/manage.py
	$(VENV_PYTHON) $(SRC_DIR)/manage.py makemigrations;

# Apply migrations
schema: $(SRC_DIR)/manage.py
	$(VENV_PYTHON) $(SRC_DIR)/manage.py migrate;

# Collect static files
static-files: $(SRC_DIR)/manage.py
	$(VENV_PYTHON) $(SRC_DIR)/manage.py collectstatic --no-input;

update: schema static-files translations
	$(VENV_PIP) install -r requirements.txt;
	mkdir -p $(LOG_DIR);
	sudo systemctl restart edtlr-annotator.service;
	sudo systemctl restart edtlr-annotator.socket;
	sudo systemctl restart nginx;
