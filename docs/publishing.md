# Local GitHub publication preparation

The working branch is `portfolio/readiness`. No commit, push, model upload,
training run or robot operation was performed during preparation.

The exact current publication set is [publish-manifest.txt](publish-manifest.txt).
It contains existing tracked files plus the new documentation and offline
checker. It excludes Git internals, ignored account/tool state, virtual
environments, dataset records, recordings, weights, logs and the local
NormaCore dependency checkout. No existing attribution or license was removed.

The original root README is preserved as `HACKATHON.md`. Its dates, targets,
installer and deployment commands are inherited draft context. The new README
explains available implementation, dependencies, configured training parameters
and the evidence missing for performance claims.

Documentation corrections include the Station trainer's six-dimensional limit,
the absence of a training `--motor-ids` option, the relative path to the exported
Parquet file, and the resume command matching the existing entrypoint. No
executable or packaging behavior was changed. Policy YAML changes are comments
labeling inherited result anecdotes as unverified.

Before publishing, maintainers still need to settle the project-wide license and
confirm how to credit individual work versus the inherited hackathon starter.
No project-wide license existed in the starting tracked tree. Upstream licenses
remain applicable to their components; see `THIRD_PARTY_NOTICES.md`.

The new ignore rules apply to future additions. They do not remove any secret
already present in Git history. The current-file credential pattern scan is
heuristic; the completed limited scan of reachable history is described in the verification record.
Do not publish raw Nebius logs/configuration without reviewing their contents.
