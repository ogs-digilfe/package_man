.PHONY: install inventory

CURRENT_DIR := $(shell pwd)
PACKAGE = apt


install:
	python3 $(CURRENT_DIR)/python_scripts/build_python_venv.py --package $(PACKAGE)

inventory:
	python3 $(CURRENT_DIR)/python_scripts/make_inventory.py
