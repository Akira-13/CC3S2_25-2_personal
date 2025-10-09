
VENV=.venv
PY=$(VENV)/bin/python
PIP=$(VENV)/bin/pip
PYTEST=$(VENV)/bin/pytest

.PHONY: venv deps test_all test_unit cov clean

venv:
	python -m venv $(VENV)

deps: venv
	$(PIP) install -r requirements.txt

# Ejecuta pytest en cada sub-actividad
test_all: deps
	$(PYTEST) -q soluciones/aserciones_pruebas|| exit 1
	$(PYTEST) -q soluciones/pruebas_pytest|| exit 1
	$(PYTEST) -q soluciones/pruebas_fixtures|| exit 1
	$(PYTEST) --cov=models --cov-report term-missing -q soluciones/coverage_pruebas|| exit 1
	$(PYTEST) -q soluciones/factories_fakes|| exit 1
	$(PYTEST) -q soluciones/mocking_objetos|| exit 1
	$(PYTEST) -q soluciones/practica_tdd|| exit 1

# Atajo para correr sólo unidad si decides marcar tests con -m "unit"
test_unit:
	cd soluciones && $(PYTEST) -m "unit" -q

# Cobertura sólo para coverage_pruebas (puedes extender a otras)
cov:
	$(PYTEST) --cov=models --cov-report term-missing -q soluciones/coverage_pruebas

clean:
	rm -rf .pytest_cache **/__pycache__ htmlcov .coverage
