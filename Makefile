PYTHON = uv run python3
UV = uv

all: install run

install:
	@echo "executing (fly-in)"
	$(UV) sync

run:
	@echo 'start fly simulation'
	$(PYTHON) main.py

clean:
	@echo 'remove all artifacts'
	rm -rf __pycache__ .venv .uv

debug:
	$(PYTHON) -m pdb main.py

lint:
	@echo "check code quality (--strict - mode)"
	flake8 . --exclude .venv
	mypy . --strict --warn-return-any \
	--warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs \
	--check-untyped-defs
