# Missing Nebius evidence

No Nebius API, training job, upload, cloud filesystem mount or remote inference
service was contacted during this preparation. The local tree contains no
Nebius job export, training log, checkpoint or resolved run configuration.
The ignored NormaCore source checkout is available for source inspection, but
it is not evidence of a completed training run.

To substantiate the inherited ACT/SmolVLA run anecdotes, retrieve the following
from the DevLab workspace or shared filesystem, without adding raw data or
weights to Git:

| Required item | Exact content needed | Expected source |
| --- | --- | --- |
| Run identity | ACT and SmolVLA job/run IDs, timestamps, status, command and source Git commit | Nebius job metadata, saved shell command or DevLab run record |
| Resolved configuration | `train_config.json`, policy `config.json`, CLI overrides, seed, camera rename map, optimizer and scheduler settings | Run output; often `checkpoints/last/pretrained_model/` |
| Training trace | Step-indexed loss, learning rate, throughput, batch size, final completed step and any failures | Console logs, local log files or an exported W&B scalar history |
| Dataset identity | Immutable Hub commit/revision, `meta/info.json`, feature shapes, episode/frame counts and any episode selection or split | Cached dataset metadata / run configuration |
| Checkpoint inventory | Relative file list, file sizes and SHA-256 checksums; corresponding policy type and training step | Run checkpoints on the workspace disk or shared filesystem |
| Preprocessing | Normalization statistics and saved policy pre/postprocessor configuration/state, where emitted by that LeRobot version | Checkpoint export alongside weights |
| Environment | Python, LeRobot, torch, CUDA/driver versions, GPU model, image digest or dependency lock | DevLab environment / job spec |
| Evaluation evidence, if it exists | Evaluation protocol, held-out episode IDs, per-trial outcomes, resets and model identity; media with permission to publish | Separately recorded evaluation artifacts |

The job scripts expect a run directory such as
`/mnt/checkpoints/<HF_USER>/<job-name>/checkpoints/last/pretrained_model/`.
Interactive DevLab runs may instead be under `so101/outputs/train/` on the
workspace/container disk. These are script conventions, not observed locations
of existing runs. Exact run names and whether artifacts survived are unknown.

The existing `training/eval.py` checks filenames and reads JSON only. Its
"Checkpoint OK" output does not establish valid weights, processor
compatibility, inference quality or manipulation success.

Export a small, sanitized metrics table and configuration summary into a future
results document. Keep credentials, account-specific secrets, dataset records,
weights and unreviewed logs outside Git. Do not infer success from decreasing
training loss. If evaluation records do not exist, report that explicitly.

Separate from Nebius, the repository still needs maintainer-confirmed individual
contribution credit and a license decision. Real-world performance evidence
would need an actual recorded evaluation; fetching training artifacts alone
cannot supply it.
