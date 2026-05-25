.PHONY: help init sync-skill evals

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

init: ## Create data directories and init SQLite
	@mkdir -p data/memory/entries data/summaries
	@python3 scripts/inquisitive-sqlite.py init && echo "OK" || echo "FAIL"

sync-skill: ## Sync root SKILL.md → skills/inquisitive/SKILL.md (preserves YAML frontmatter)
	@python3 scripts/sync-skill.py

evals: ## Run automated eval tests
	@python3 scripts/run-evals.py
