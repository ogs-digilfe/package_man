.PHONY: install inventory

CURRENT_DIR := $(shell pwd)
PYTHON_INTERPRETOR := $(shell pwd)/../../venv_package_man/bin/python
PACKAGE = apt


install:
	python3 $(CURRENT_DIR)/python_scripts/build_python_venv.py --package $(PACKAGE)

	@echo "$(PYTHON_INTERPRETOR) -m airflow db migrate"
	cd ../airflow && $(PYTHON_INTERPRETOR) -m airflow db migrate

inventory:
	python3 $(CURRENT_DIR)/python_scripts/make_inventory.py
