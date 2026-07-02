.PHONY: setup test render package-data package

# Clone-and-go: zero third-party dependencies (pure Python 3 stdlib), so "setup"
# is just proving the repo works — runs the test suite and regenerates the
# results tables from the committed scored.json files. No install step exists.
setup: test render
	@echo "Probity is ready. See results/RESULTS.md or run 'make test' / 'make render' again anytime."

test:
	python3 -m unittest discover -s tests -v

render:
	python3 results/render.py

# GENERATES probity_cli/data/ (gitignored) by mirroring engine/, leaves/*, results/, demo/ into
# the package so `pip install probity-bench` ships the full pipeline minus corpus/ (raw SEC
# documents) and _archive_* (stale pre-fix runs). Run this before `python3 -m build`.
package-data:
	rm -rf probity_cli/data
	mkdir -p probity_cli/data
	for d in engine leaves results demo; do \
		if [ -d "$$d" ]; then \
			rsync -a --exclude='corpus' --exclude='_archive_*' --exclude='__pycache__' --exclude='*.pyc' "$$d" probity_cli/data/; \
		fi; \
	done
	@echo "probity_cli/data/ regenerated."

package: package-data
	python3 -m pip install --quiet --upgrade build
	python3 -m build
