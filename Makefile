.PHONY: setup test render

# Clone-and-go: zero third-party dependencies (pure Python 3 stdlib), so "setup"
# is just proving the repo works — runs the test suite and regenerates the
# results tables from the committed scored.json files. No install step exists.
setup: test render
	@echo "Probity is ready. See results/RESULTS.md or run 'make test' / 'make render' again anytime."

test:
	python3 -m unittest discover -s tests -v

render:
	python3 results/render.py
