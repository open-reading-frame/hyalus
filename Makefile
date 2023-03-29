# Makefile framework
SHELL=/bin/zsh
.SHELLFLAGS=-o nonomatch -c

# Sphinx vars
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
SOURCEDIR     = docs
BUILDDIR      = _build

CODEDIRS = src/hyalus tests
EXCLUDES = tests/*/data/*.py tests/run/*_dir*/*/*.py


# Make commands
HELP_TEXT  = "\nHyalus\n******\n\nTargets\n=======\n\n"
HELP_TEXT += $(__TARGET_HELP)

CWD := ${CURDIR}

.PHONY: help clean api-docs html confluence test mypy pylint black

# Put it first so that "make" without argument is like "make help".
__TARGET_HELP += "  * help - display this help message\n"
help:
	@echo $(HELP_TEXT) $(VAR_TEXT)

__TARGET_HELP += "  * clean - remove doc build, pytest, coverage, etc. artifacts\n"
clean:
	$(SHELL) $(.SHELLFLAGS) 'rm -rf build **/*.egg-info _builder confluence docs/_* **/__pycache__ pytest-*-report.xml .coverage*'

__TARGET_HELP += "  * api-docs - Generates the rst documentation for all code in the \`$(CODEDIRS)\` directory(ies)\n"
api-docs:
# 	docker pull ghcr.io/genapsysinc/docbuilder:latest
	docker run -v `pwd`:/repo/ ghcr.io/genapsysinc/docbuilder:latest -d $(CODEDIRS) -e $(EXCLUDES)

__TARGET_HELP += "  * html - Build the html documentation locally - The \`index.html\` is in the \`$(BUILDDIR)/html/\` directory\n"
html:
# 	docker pull ghcr.io/genapsysinc/docbuilder:latest
	docker run -v `pwd`:/repo/ ghcr.io/genapsysinc/docbuilder:latest -m -d $(CODEDIRS) -e $(EXCLUDES)

__TARGET_HELP += "  * confluence - Build the confluence documentation\n"
confluence:
# 	docker pull ghcr.io/genapsysinc/docbuilder:latest
	docker run -v `pwd`:/repo/ ghcr.io/genapsysinc/docbuilder:latest -c -d $(CODEDIRS) -e $(EXCLUDES)

__TARGET_HELP += "  * test - Run pytest and produce term-missing coverage report\n"
test:
	coverage run -m pytest || rm -f .coverage*
	coverage combine -q
	coverage report -m

__TARGET_HELP += "  * mypy - Run mypy, ignoring docs and confluence dirs\n"
mypy:
	mypy .

__TARGET_HELP += "  * pylint - Run pylint, ignoring docs and confluence dirs\n"
pylint:
	pylint --recursive=true .

__TARGET_HELP += "  * black - Run black, line length set to 120 and skipping string normalization\n"
black:
	black src src/hyalus/bin/hyalus tests
