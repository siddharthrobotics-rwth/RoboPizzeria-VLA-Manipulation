# Verification and review boundaries

Portfolio preparation started on a clean `main` working tree at commit
`78139ef` and uses local branch `portfolio/readiness`. The ignored
`elrobot/norma-core/` checkout was present and remains untouched.

The final preparation changes documentation, attribution notes and ignore rules,
and adds a read-only repository checker. Training, dataset processing, Station
installation and robot-control behavior remain unchanged. Earlier behavioral
edits and their temporary regression tests were removed at the user's request.

## Checks

Run `python3 scripts/check_repository.py` from the repository root. It parses
Python without importing it, runs `bash -n`, parses TOML and (when PyYAML is
installed) YAML, checks relative Markdown file targets, inspects the publication
set for generated artifacts and likely credential patterns, and verifies ignore
rules against representative local filenames. It does not validate Markdown
anchors or external URLs. The secret scan uses a small set of recognizable
credential formats and cannot prove the absence of secrets.

On 2026-10-26, the final offline checker passed over **67 publication files**:
8 Python sources, 24 shell scripts, 2 TOML files (including `uv.lock`), 6 YAML
files and 110 relative Markdown links. All 14 ignore probes passed and all 5
configuration templates remained publishable. PyYAML was available; no YAML
check was skipped. `git diff --check` also passed.

A byte comparison against the starting commit confirmed that all **33 existing
Python, shell and packaging/lock files** remain unchanged. Policy YAML changes
are comments only. `HACKATHON.md` is an exact copy of the original root README.

A separate read-only scan of **219 unique reachable Git blobs** across all local
refs found no matches for the selected Hugging Face, AWS, GitHub, private-key or
long literal W&B/AWS-secret assignment patterns. No reachable historical blob
exceeded 5 MiB. This is a limited pattern scan, not a guarantee that history
contains no sensitive information. No history was rewritten.

## Source review findings retained without behavior changes

| Area | Existing behavior or limitation |
| --- | --- |
| ACT / SmolVLA | YAML profiles exist and reference a Hub dataset/base model; no local run artifacts verify their training results. Camera mapping, preprocessing and installed LeRobot API compatibility require runtime confirmation. |
| Packaging | `so101/pyproject.toml` uses `backend-backend` rather than the standard `build-backend`. TOML parsing does not test package installation. |
| Private helper | `training/run.py` is marked private/legacy, uses a different SmolVLA recipe, and resolves `.env` under `so101/` while public docs use the repository root. |
| Dataset conversion | Supports v2.0/v2.1 with timestamp resampling and provenance; the SO-101 stack expects v3. Source column types and same-row action semantics need dataset-level confirmation. One input file and an episode's JPEGs can occupy substantial memory. |
| Station | Installer may replace its source checkout while preserving selected runtime files. It was inspected but not executed. Upstream trainer dimensions are six; the target ElRobot has eight servos. |
| Inference | SO-101 rollout automatically renames SmolVLA cameras only when the policy path contains `smolvla`; other checkpoint names require explicit `RENAME_MAP`. The monitor prints live bus/motor counts, not policy-quality metrics. |
| Resume | Entry point resumes only when the saved `train_config.json` exists; an explicit resume request does not independently enforce its presence. No resume workflow was run. |
| Checkpoint inspection | `training/eval.py` checks file existence and parses JSON. It does not load weights, validate tensors/processors or evaluate a policy. |

These findings are documentation of the supplied code, not newly implemented
features or claims of observed robot behavior.

## Not verified

No dependency installation, Docker build, full converter run, video encoding,
dataset download, CUDA availability, training, checkpoint loading, robot
connection, torque/motor command, cloud request or upload was attempted. The
system Python has NumPy, Pillow and PyYAML, but lacks PyArrow, Hugging Face
`datasets` and PyAV; the converter cannot run in that environment as supplied.
`ruff` and `shellcheck` are unavailable; syntax checks are not substitutes for
those linters. No model or dataset artifacts are committed.
