PYTHON = uv run python3
UV = uv
DEFAULT_MAP = main.py maps/challenger/01_the_impossible_dream.txt

all: install run

install:
	@echo "executing (fly-in)"
	$(UV) sync

run:
	@echo 'start fly simulation'
	$(PYTHON) $(DEFAULT_MAP)

clean:
	@echo 'remove all artifacts'
	rm -rf __pycache__ .venv .uv

lint:
	@echo "check code quality (--strict - mode)"
	flake8 . --exclude .venv
	mypy . --strict --warn-return-any \
	--warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs \
	--check-untyped-defs
