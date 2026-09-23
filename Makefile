PYTHON ?= python3

.PHONY: check refs refs-status octemu-prepare gearmulator-prepare audit-md

check:
	$(PYTHON) scripts/references.py validate
	$(PYTHON) -m compileall -q scripts
	$(PYTHON) -m unittest discover -s tests -p 'test_*.py'

refs:
	$(PYTHON) scripts/references.py fetch

refs-status:
	$(PYTHON) scripts/references.py status

octemu-prepare:
	$(PYTHON) scripts/prepare_octemu.py

gearmulator-prepare:
	$(PYTHON) scripts/prepare_gearmulator.py

audit-md:
	@test -n "$(IMAGE)" || (echo "usage: make audit-md IMAGE=/path/to/your-flash.bin" >&2; exit 2)
	$(PYTHON) scripts/audit_md_image.py "$(IMAGE)"
