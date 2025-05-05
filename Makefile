.PHONY: test
test:
	pytest -v

.PHONY: test-cov
test-cov:
	pytest -v --cov
