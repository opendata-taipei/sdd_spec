.PHONY: validate enterprise evals agent-evals portability drift new-change

validate:
	python scripts/validate_sdd.py
	python scripts/validate_enterprise.py
	python -m unittest discover -s tests -v
	python scripts/run_evals.py
	python scripts/run_agent_evals.py
	python scripts/validate_runtime_audit.py

enterprise:
	python scripts/validate_enterprise.py

evals:
	python scripts/run_evals.py

agent-evals:
	python scripts/run_agent_evals.py

portability:
	python scripts/portability_check.py

# 使用：make new-change ID=CHG-2026-001 SLUG=add-feature AUTHOR=github-login
new-change:
	python scripts/bootstrap_change.py $(ID) $(SLUG) $(AUTHOR)

# 使用：make drift ID=CHG-2026-001
drift:
	python scripts/drift_check.py --change $(ID)
