
ACTIVATE_LINUX:=. venvdiffgram/bin/activate
PYTHONEXEC:=python3
PIPEXEC:=pip3
ifeq ($(OS),Windows_NT)
	export PYTHONPATH := $(shell echo %cd%)
else
	export PYTHONPATH := $(shell pwd)
endif
clean:
	rm -rf venvdiffgram
	docker compose down
setup-env-backend:
	@echo "Creating virtual environment..."
	$(PYTHONEXEC) -m venv venvdiffgram
	@echo "Activating virtual environment..."
	@echo "Installing dependencies..."
	@$(ACTIVATE_LINUX);$(PIPEXEC) install -r default/requirements.txt;$(PIPEXEC) install -r walrus/requirements.txt;$(PIPEXEC) install -r eventhandlers/requirements.txt
	@echo "Done."
run-bg-services:
	@echo "Running background services..."
	docker compose up -d db rabbitmq minio
run-default:
	@echo "Running default..."
	@$(ACTIVATE_LINUX); cd default; $(PYTHONEXEC) main.py


run-walrus:
	@echo "Running walrus..."
	@$(ACTIVATE_LINUX); cd walrus; $(PYTHONEXEC) main.py


run-eventhandlers:
	@echo "Running eventhandlers..."
	@$(ACTIVATE_LINUX); cd eventhandlers; $(PYTHONEXEC) main.py

run-dispatcher:
	@echo "Running dispatcher..."
	@$(ACTIVATE_LINUX); cd local_dispatcher; $(PYTHONEXEC) local_dispatch.py


frontend-deps:
	@echo "Installing frontend dependencies..."
	@cd frontend; yarn install

frontend-run:
	@echo "Running frontend..."
	@cd frontend; yarn start

e2e-tests:
	@echo "Running e2e tests..."
	@cd frontend; yarn run cypress open