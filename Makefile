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
				psycopg2-binary \
				python-dotenv; \
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
	sed -i "s/__STATIC_ROOT__/${STATIC_ROOT}/g" ${SRC_DIR}/.env;
	sed -i "s/__DATABASE_HOST__/${DATABASE_HOST}/g" ${SRC_DIR}/.env;
	sed -i "s/__DATABASE_NAME__/${DATABASE_NAME}/g" ${SRC_DIR}/.env;
	sed -i "s/__DATABASE_USER__/${DATABASE_USER}/g" ${SRC_DIR}/.env;
	sed -i "s/__DATABASE_PASSWORD__/${DATABASE_PASSWORD}/g" ${SRC_DIR}/.env;
	sed -i "s/__DATABASE_PORT__/${DATABASE_PORT}/g" ${SRC_DIR}/.env;

# Make the socket descriptor
socket-descriptor: templates/edtlr-browser.socket.template
	rm -f templates/edtlr-browser.socket;
	cp templates/edtlr-browser.socket.template templates/edtlr-browser.socket;

