PYLINT = flake8
PYLINTFLAGS = --ignore=E741,W503 --exclude=interactive.py,__main__.py
PYTHONFILES = $(shell find . -name "*.py")

lint: $(patsubst %.py,%.pylint,$(PYTHONFILES))

tests: pytests lint

pytests:
	nosetests --with-coverage --cover-package=APIServer.threads

%.pylint:
	$(PYLINT) $(PYLINTFLAGS) $*.py
