PYTHON ?= python3

.PHONY: check refs refs-status octemu-prepare

check:
	$(PYTHON) scripts/references.py validate
	$(PYTHON) -m compileall -q scripts

refs:
	$(PYTHON) scripts/references.py fetch

refs-status:
	$(PYTHON) scripts/references.py status

octemu-prepare:
	$(PYTHON) scripts/prepare_octemu.py
