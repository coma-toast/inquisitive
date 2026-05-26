.PHONY: help init sync-skill evals

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

init: ## Create .inquisitive/ dirs and user/org dirs in ~/.inquisitive/
	@mkdir -p .inquisitive/entries .inquisitive/summaries
	@mkdir -p ~/.inquisitive/user/entries ~/.inquisitive/user/summaries
	@mkdir -p ~/.inquisitive/orgs
	@if [ ! -f .inquisitive/config.json ]; then \
		echo '{"backend":"json-md","personality":"inquisitive","frequency":"major","org_slug":null}' > .inquisitive/config.json; \
		echo "Created .inquisitive/config.json (defaults)"; \
	fi
	@if [ ! -f .inquisitive/.gitignore ]; then \
		printf '# Private — not committed\nentries/\n*.db\nerrors.log\n\n# Summaries ARE committed (enables team sharing)\n# To stop sharing, uncomment:\n# summaries/\n' > .inquisitive/.gitignore; \
		echo "Created .inquisitive/.gitignore"; \
	fi
	@echo "OK init"

init-sqlite: ## Initialize SQLite backend in .inquisitive/ (run after init if using sqlite)
	@python3 scripts/inquisitive-sqlite.py init

sync-skill: ## Sync root SKILL.md → skills/inquisitive/SKILL.md (preserves YAML frontmatter)
	@python3 scripts/sync-skill.py

evals: ## Run automated eval tests
	@python3 scripts/run-evals.py
