.PHONY: install inventory

CURRENT_DIR := $(shell pwd)
PYTHON_INTERPRETOR := $(shell pwd)/../../venv_package_man/bin/python
AIRFLOW_HOME_DIR := $(shell cd $(shell pwd)/../airflow && pwd)
PACKAGE := apt


install:
	python3 $(CURRENT_DIR)/python_scripts/build.py --package $(PACKAGE)
	
	@echo "start initializing Airflow db ..."
	@export AIRFLOW_HOME=$(AIRFLOW_HOME_DIR) && $(PYTHON_INTERPRETOR) -m airflow db migrate
	@echo "Airflow db initialize done!"

inventory:
	python3 $(CURRENT_DIR)/python_scripts/make_inventory.py
