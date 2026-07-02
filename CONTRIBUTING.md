# Contributing to Probity

Thanks for taking the time to contribute! 🎉

## Quick start for contributors

```bash
git clone https://github.com/eikiyo/probity.git
cd probity
cp .env.example .env      # add your own keys
# no install step -- pure Python 3 stdlib, zero third-party dependencies
python3 -m unittest discover -s tests -v   # make sure tests pass before you change anything
```

## How to contribute

1. **Open an issue first** for anything non-trivial — describe the problem before the fix.
2. **Fork & branch**: `git checkout -b feat/short-description` (or `fix/...`, `docs/...`).
3. **Make focused commits** — one logical change per commit. Follow [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`).
4. **Add/adjust tests** for any behavior change.
5. **Run the full check** before pushing: `python3 -m unittest discover -s tests`.
6. **Open a PR** against `main`, fill in the template, link the issue.

## What makes a PR easy to merge

- It does one thing.
- Tests pass and coverage doesn't drop.
- The description explains *why*, not just *what*.
- No secrets, no unrelated formatting churn.

## Reporting bugs / requesting features

Use the issue templates. For security issues, **do not** open a public issue — see [SECURITY.md](SECURITY.md).

## Code of Conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md). By participating you agree to uphold it.
