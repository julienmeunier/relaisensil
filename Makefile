.PHONY: venv virtualenv dependencies clean_virtualenv

DEPLOY_DIR := $(CURDIR)/python

virtualenv: venv
	ENV=./.venv/bin/activate $(SHELL) -li;
venv:
	test -d .venv || virtualenv2 .venv || virtualenv .venv;
dependencies:
	.venv/bin/pip install -Ur requirements.txt;
clean_virtualenv:
	rm -rf .venv;
deploy: 
	mkdir python -p
	pip install --no-use-wheel --target=$(DEPLOY_DIR) --build=$(DEPLOY_DIR)/tmp --ignore-installed -Ur requirements.txt
	./deploy.py -s production
