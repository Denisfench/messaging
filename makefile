# A template makefile that works for static websites.
# Need to export as ENV var
export TEMPLATE_DIR = templates
PTML_DIR = html_src
UTILS_DIR = utils
REPO = socnet
DOCKER_DIR = docker
REQ_DIR = requirements
API_DIR = APIServer
WEB_DIR = frontend
WEB_PUBLIC = $(WEB_DIR)/public
WEB_SRC = $(WEB_DIR)/src
WEBFILES = $(shell ls $(WEB_SRC)/*.js)
WEBFILES += $(shell ls $(WEB_SRC)/components/*.js)
WEBFILES += $(shell ls $(WEB_SRC)/*.css)
API_SERVER_PORT = 5000

INCS = $(TEMPLATE_DIR)/head.txt $(TEMPLATE_DIR)/logo.txt $(TEMPLATE_DIR)/menu.txt

HTMLFILES = $(shell ls $(PTML_DIR)/*.ptml | sed s/.ptml/.html/ | sed 's/html_src\///')

FORCE:

%.html: $(PTML_DIR)/%.ptml $(INCS)
	python3 $(UTILS_DIR)/html_checker.py $< 
	$(UTILS_DIR)/html_include.awk <$< >$@
	git add $@

local: $(HTMLFILES)

prod: $(INCS) $(HTMLFILES) tests
	make webapp
	-git commit -a 
	git push origin master

tests: FORCE
	cd APIServer; make tests

api_server: FORCE
	cd APIServer; make api_server

#dev_env will install all necessary libraries to run locally
dev_env: FORCE
	pip3 install -r requirements-dev.txt

# get new code for each submodule:
submods:
	git submodule foreach 'git pull origin master'

# dev container has dev tools
dev_container: $(DOCKER_DIR)/Dockerfile # $(REQ_DIR)/requirements.txt $(REQ_DIR)/requirements-dev.txt
	make rm_dev_container
	docker build -t gcallah/$(REPO)-dev -f $(DOCKER_DIR)/Dockerfile . # build image
	docker run -d -p $(API_SERVER_PORT):8000 --name $(REPO)-dev gcallah/socnet-dev # run container at localhost:$(API_SERVER_PORT)

# clean up the dev container
rm_dev_container:
	docker stop $(REPO)-dev 2> /dev/null || true # stop the previous running containers
	docker rm $(REPO)-dev 2> /dev/null || true # remove the previous containers

nocrud:
	rm *~
	rm .*swp
	rm $(PTML_DIR)/*~
	rm $(PTML_DIR)/.*swp

clean:
	touch $(PTML_DIR)/*.ptml; make local

webapp: $(WEB_PUBLIC)/index.html

$(WEB_PUBLIC)/index.html: $(WEBFILES)
	- rm -r static || true
	- rm webapp.html || true
	- cd $(WEB_DIR) && \
	npm run build && \
	mv build/index.html build/webapp.html && \
	cp -r build/* .. && \
	cd ..
	@echo "Adding the webapp changes to the stage index"
	git add .
