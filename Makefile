
.PHONY: build clean coverage format test

build:
	python setup.py bdist_wheel -d dist

clean:
	# run in interactive mode
	git clean -i

coverage:
    pytest --cov=geomagio --cov-report xml

format:
	black .

test:
	pytest
