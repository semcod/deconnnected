# Changelog

## [Unreleased]

## [0.6.2] - 2026-07-12

### Docs
- Update CHANGELOG.md
- Update README.md
- Update docs/ARCHITECTURE.md
- Update docs/ARTIFACTS.md
- Update docs/CLI.md
- Update docs/LLM_PROVIDERS.md
- Update docs/REFACTORING_WORKFLOW.md
- Update docs/TROUBLESHOOTING.md

### Test
- Update tests/__pycache__/test_agent_models.cpython-313-pytest-9.1.1.pyc
- Update tests/__pycache__/test_budget.cpython-313-pytest-9.1.1.pyc
- Update tests/__pycache__/test_classification.cpython-313-pytest-9.1.1.pyc
- Update tests/__pycache__/test_config_scanner.cpython-313-pytest-9.1.1.pyc
- Update tests/__pycache__/test_correlation.cpython-313-pytest-9.1.1.pyc
- Update tests/__pycache__/test_extraction.cpython-313-pytest-9.1.1.pyc
- Update tests/__pycache__/test_frontend_tests.cpython-313-pytest-9.1.1.pyc
- Update tests/__pycache__/test_integrations.cpython-313-pytest-9.1.1.pyc
- Update tests/__pycache__/test_patch_policy.cpython-313-pytest-9.1.1.pyc
- Update tests/__pycache__/test_python_analysis.cpython-313-pytest-9.1.1.pyc
- ... and 26 more files

### Other
- Update .env.example
- Update .gitignore
- Update .idea/.gitignore
- Update .idea/deconnected.iml
- Update .idea/inspectionProfiles/Project_Default.xml
- Update .idea/inspectionProfiles/profiles_settings.xml
- Update .idea/modules.xml
- Update .idea/vcs.xml
- Update Makefile
- Update examples/config/deconnected.example.yaml
- ... and 29 more files


## 0.6.1

Documentation release.

- rewrote README around the actual 0.6 CLI and safety behavior;
- added architecture, CLI, provider, workflow, artifact and troubleshooting guides;
- added example OpenRouter and project configuration files;
- clarified current limitations and acceptance rules;
- documented that table classifications are evidence, not automatic deletion decisions.

## 0.6.0

- added patch-scope validation;
- added forbidden-operation detection;
- added before/after repository snapshots;
- added policy and snapshot artifacts;
- added agent budget policy;
- expanded tests to 24 cases.

## 0.5.0

- added structured refactoring plans;
- added LiteLLM/OpenRouter and Claude Code providers;
- added isolated Git worktree execution;
- added validation and patch artifacts.

## 0.4.0

- added sqlglot SQL analysis;
- added LibCST Python analysis;
- added table classification and extraction planning.
