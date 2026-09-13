build:
	git describe --tags --abbrev=0 | tail -n 1 | xargs -I % uv version %
	rm -rf dist/
	rm -rf build/
	sphinx-build -vvv --write-all --fresh-env src build

create-dev:
	pre-commit install
	pre-commit autoupdate
	uv sync
	uv build

serve:
	.venv/bin/sphinx-autobuild -b dirhtml src build

clean:
	rm -rf build/

.PHONY: build-site check-site
build-site:
	.venv/bin/sphinx-build -b dirhtml --write-all src build

check-site:
	.venv/bin/sphinx-build -b dirhtml -W --keep-going --write-all src build
	.venv/bin/python scripts/check-site.py
