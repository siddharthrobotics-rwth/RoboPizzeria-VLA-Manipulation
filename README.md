# RobotPizzaCup

Imitation learning workflows for pizza topping tasks using two robot stacks:
**SO-101 with LeRobot** and **ElRobot with NormaCore Station**. The repository
contains data collection wrappers, a Station-to-LeRobot dataset converter,
ACT and SmolVLA training configurations, Nebius launch scripts and inference
instructions.

This is a portfolio presentation of an existing Robotics Pizza Hackathon starter
project. It demonstrates the code and integration workflow available here.
**No successful autonomous robot manipulation or measured success rate is
verified by the files in this checkout.** Existing run anecdotes are identified
below, separately from reproducible evidence.

## What is implemented

| Area | Files | Role |
| --- | --- | --- |
| SO-101 collection | [`so101/scripts/`](so101/scripts/) | Calibration, teleoperation, recording, replay and camera configuration wrappers |
| SO-101 training | [`so101/training/`](so101/training/README.md) | ACT, SmolVLA and optional policy profiles; local, Docker and Nebius job workflows |
| Station integration | [`elrobot/scripts/`](elrobot/scripts/) | Install pinned Station release, configure clients, export history to Parquet |
| Dataset processing | [`export_to_lerobot.py`](elrobot/scripts/export_to_lerobot.py) | Convert synchronized Station telemetry and JPEGs to LeRobot v2.0/v2.1 |
| Inference | [`rollout.sh`](so101/scripts/rollout.sh), [`ElRobot guide`](elrobot/docs/train-and-deploy.md) | SO-101 rollout wrapper and upstream Station deployment instructions |
| Inspection | [`training/eval.py`](so101/training/eval.py) | Check required checkpoint filenames and read policy metadata; no performance evaluation |

## Architecture

```text
SO-101 leader/follower + front/top cameras
  -> LeRobot recording (v3 dataset)
  -> lerobot-train: ACT / SmolVLA (local, Docker, or Nebius CUDA)
  -> checkpoints -> SO-101 rollout wrapper

ElRobot leader/follower + cameras
  -> NormaCore Station history -> dataset-generator -> Station Parquet
     -> upstream smolvla_py trainer -> upstream live Station inference
     -> export_to_lerobot.py -> LeRobot v2.0/v2.1 dataset (separate export path)
```

These are separate environments and data formats. A Station v2.1 export is not
presented as a directly compatible SO-101 v3 training dataset. The converter
keeps all source joints, while the bundled Station SmolVLA trainer hardcodes
six state and action values; ElRobot has eight servos. Full eight-servo learned
control is not established by this repository.

## Setup and dependencies

Run commands from the indicated directory. Installation requires network access;
the offline review reported here did not install or execute the robotics stacks.

**SO-101:** [`so101/pyproject.toml`](so101/pyproject.toml) declares Python >=3.12;
[`.python-version`](so101/.python-version) selects managed Python 3.13 for the
local workflow. [`uv.lock`](so101/uv.lock) records dependencies, including
LeRobot **0.6.1**, PyTorch and policy extras. Linux source dependencies may need
compiler tools and Python development headers; the managed interpreter avoids
the documented DevLab system-Python header issue. The CUDA Docker dependency
image uses managed Python 3.12 and has separate OS dependencies.

```bash
cd so101
uv python install 3.13
uv sync --frozen --managed-python --python 3.13
cp station.env.example station.env
cp ../.env.example ../.env
```

Fill the local templates for your hardware, dataset and optional cloud accounts.
`HF_TOKEN` is for private/gated Hub access; W&B credentials enable logging;
Nebius jobs need your project, subnet and shared filesystem configuration.
Examples contain inherited organizer defaults; confirm your own values before
using cloud workflows. Credentials do not belong in Git.

The existing `pyproject.toml` spells the build backend key `backend-backend`
instead of `build-backend`. This packaging issue is recorded, and a fresh
installation has not been verified. Executable and packaging behavior was left
unchanged during portfolio preparation.

**ElRobot:** the installer targets NormaCore Station **v0.1.0-beta.10**, with a
release binary and a separate source checkout under ignored `elrobot/norma-core/`.
Supported installer targets are Linux amd64/arm64 and macOS Apple Silicon. Station
client imports need `station_py`, generated protobuf stubs and the upstream
Gremlin runtime, exposed by `scripts/python_env.sh`. The upstream `smolvla_py`
project has its own environment: Python >=3.10, PyTorch, torchvision,
`transformers==5.3.0`, safetensors, Hugging Face Hub, Pillow, num2words and PyArrow
(as declared in the local upstream checkout). Training requires CUDA. Do not
reuse the SO-101 environment for this trainer.

**Standalone converter:** create a separate environment for NumPy, PyArrow,
PyAV (`av`), Pillow and Hugging Face `datasets`. No converter lockfile is provided.
The script encodes H.264 through PyAV/libx264; codec availability must be checked
in the target environment. Detailed commands and semantics are in the
[collection guide](elrobot/docs/data-collection.md#convert-to-lerobot).

## Dataset processing

The converter recursively discovers Parquet files, separates episodes by source
file and episode identifier, sorts timestamps and samples a regular FPS grid.
It selects the nearest complete source row, choosing the earlier row on ties.
State, action, task and images stay aligned; rows can repeat or be skipped.

`observation.state` uses `joints[].position_norm`; `action` uses same-row
`joints[].goal_norm`. No action shift or joint-unit conversion is applied.
Joint/camera ordering comes from the source. The converter validates dimensions,
computes episode statistics, writes provenance and retains native image sizes.
MP4 output is lossy H.264; embedded-image mode retains source JPEG bytes.
It processes one source file in memory at a time. Actual dataset conversion and
reader interoperability were not exercised in this review.

## Training profiles

Values below are read from the committed YAML files, not reports of completed
runs. Both SO-101 profiles reference `robotpizzacup/robot-pizza-cup-1`, seed 1000,
eight workers, checkpoint interval 10,000 and logging interval 50. Environment
evaluation is disabled; YAML enables W&B, while launch wrappers may override it.
Hub model upload defaults to false.

| Parameter | ACT | SmolVLA |
| --- | --- | --- |
| Configuration | [`act/config.yaml`](so101/training/policy/act/config.yaml) | [`smolvla/config.yaml`](so101/training/policy/smolvla/config.yaml) |
| Initialization | ACT with ImageNet ResNet-18 vision backbone | `lerobot/smolvla_base` |
| Steps / batch size | 30,000 / 16 | 60,000 / 16 |
| Chunk / executed action steps | 100 / 50 | 50 / 50 |
| Learning rate | 1e-5, backbone 1e-5 | 1e-4 |
| Weight decay | 1e-4 | Policy default; not specified in YAML |
| Schedule | ACT preset | Warmup 1,000; decay 60,000; floor 2.5e-6 |
| Other | VAE enabled, KL weight 10, dropout 0.1, AMP enabled | Expert-only, frozen vision encoder, state projection trainable, AMP disabled |
| Camera handling | `front`, `top` | Rename to `camera1`, `camera2`; one empty camera |

Both profiles apply up to two color transforms per sample. The inherited dataset
description says **397 episodes, 176,039 frames, 30 FPS, two 640×480 cameras and
six joints**. The actual metadata and dataset revision are absent here, so these
counts remain unverified. Approximate training passes based on those reported
counts are 2.7 for ACT and 5.5 for SmolVLA; these are configuration arithmetic,
not measured performance.

The [training guide](so101/training/README.md) documents local smokes and Nebius
jobs. [`DevLab guide`](so101/docs/devlab.md) covers interactive CUDA training.
Optional Diffusion, GR00T and π0.5 profiles are included but not validated here.
`training/run.py` is an inherited private organizer helper, not the public path.
Training and deployment commands in the linked guides execute workloads or
hardware operations; none were run during this preparation.

## Verified results and limitations

The available evidence establishes source code, configuration and documentation
only. This review checks Python and shell syntax, TOML/YAML parsing, documentation
links, artifact exclusions and likely credential patterns without importing robot
code. Exact check outcomes and limits are in [verification](docs/verification.md).

ACT comments mention historical L1 losses around 0.25 at 15k and 0.20 at 30k,
and roughly 21 steps/s for a batch-eight run. SmolVLA comments mention a 10k
probe at about 0.15 seconds/update. These are inherited anecdotes: raw logs,
resolved configurations, run identities and checkpoints are missing. They are
**not verified results**, and training loss alone cannot establish robot success.

Additional code-review limits are recorded in [verification](docs/verification.md),
including filename-based rollout camera mapping and the limited checkpoint
inspector. There is no automated manipulation benchmark, held-out evaluation
report or documented physical success rate in these files.

## Offline review

From the repository root, with Python 3.11+ (for `tomllib`) and Bash:

```bash
python3 scripts/check_repository.py
```

PyYAML enables the optional YAML parse check. The checker reports skips explicitly.
It reads Git-eligible files and runs `bash -n`; it does not import project modules,
connect to Station, run robot commands, launch training or call cloud services.

## Publishing and provenance

Use [the publication manifest](docs/publish-manifest.txt) for the exact file list
and [publishing notes](docs/publishing.md) for exclusions and known gaps. Dataset
files, recordings, model weights, virtual environments, local configuration and
the downloaded NormaCore checkout are excluded. Nothing has been pushed.

[The Nebius handoff](docs/nebius-handoff.md) lists the exact external evidence
needed to support future training claims. A project-wide license and an accurate
statement of individual contributions still require the maintainers' input;
this review does not assign ownership or invent a license.

Original hackathon material is preserved in [HACKATHON.md](HACKATHON.md), including
its draft event details and aspirational targets. Those targets are not project
results. Existing upstream attribution is retained; see
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for provenance and license notes.
