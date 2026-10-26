# Robotics Pizza Hackathon 2026

**Teach a Robot to Make Pizza in 48 Hours**

October 30 – November 1, 2026 · [Venue / City] · 8–12 teams · 2–4 participants per team

Each team has two kits: a LeRobot SO-101 pair and an ElRobot pair. Pick the arm directory for the stack you are on. They do not share a Python environment.

| Arm | Directory | Stack |
| --- | --- | --- |
| LeRobot SO-101 | [so101](so101/README.md) | `uv` + LeRobot 0.6.1 |
| ElRobot | [elrobot](elrobot/README.md) | NormaCore Station binary |

**SO-101 train → deploy:** [DevLab](so101/docs/devlab.md) · [Train and deploy](so101/docs/train-and-deploy.md) · **ElRobot train → deploy:** [Train and deploy](elrobot/docs/train-and-deploy.md)

Status: **Draft v0.1**.

---

## SO-101 (LeRobot)

From `so101`. Full steps: [so101/README.md](so101/README.md).

**1. Install `uv` once** if `uv` is not a command (DevLabs Jupyter, a fresh machine). The installer writes `~/.local/bin/uv` and updates the shell profile. The terminal you installed in still needs `source`.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source "$HOME/.local/bin/env"
```

**2. Create the environment.** DevLabs’ `(base)` Python is `/usr/bin/python3.12` and has no `Python.h`. On Linux, LeRobot pulls `pynput`, which pulls `evdev`, and that package compiles from source. `uv sync` has to use uv’s own CPython 3.13 (`so101/.python-version`). `hf` is installed inside the venv.

```bash
cd so101
unset UV_PYTHON
rm -rf .venv
uv python install 3.13
uv sync --managed-python --python 3.13
uv run hf auth login
cp station.env.example station.env
cp ../.env.example ../.env
```

The sync log must name an interpreter under `~/.local/share/uv/python`. A line that says `/usr/bin/python3.12` means this environment will fail the same way again.

That install includes LeRobot **0.6.1** with robot CLIs (`core_scripts` + `feetech`) and policy extras **ACT** (core), **SmolVLA**, **Diffusion**, **π0 / π0.5**, and **GR00T N1.7**.

| Step | Command (from `so101`) |
| --- | --- |
| Find USB ports | `bash scripts/list_ports.sh` |
| Calibrate | `bash scripts/calibrate.sh follower` then `leader` |
| Teleop | `bash scripts/teleoperate.sh` |
| Record 50 demos | `bash scripts/record.sh` |
| Preview in Rerun | `bash scripts/viz_dataset.sh` |
| CPU ACT smoke (20 steps) | `bash training/scripts/train_local.sh act lerobot/pusht 20` |
| DevLab fine-tune (recommended) | [DevLab guide](so101/docs/devlab.md) |
| Job canary (500 steps) | `bash training/scripts/run_serverless.sh --debug act` |
| Job ACT | `bash training/scripts/run_serverless.sh act` |
| Copy checkpoint from FS mount | `bash training/scripts/download_checkpoint.sh <job-name>` |
| Run policy | `bash scripts/rollout.sh <checkpoint>` |

Robot work uses the `uv` venv in `so101`. `train_local.sh` is a CPU smoke. GPU fine-tune is a [DevLab](so101/docs/devlab.md) (recommended, RTX PRO 6000 by default) or a [Job](so101/docs/train-and-deploy.md#cloud-training). L40S and H100 are the other platforms.

Upstream: [LeRobot install](https://huggingface.co/docs/lerobot/installation) · [SO-101](https://huggingface.co/docs/lerobot/so101) · [real-robot IL](https://huggingface.co/docs/lerobot/il_robots)

## ElRobot (NormaCore Station)

From `elrobot`. Full steps: [elrobot/README.md](elrobot/README.md).

```bash
cd elrobot
bash scripts/install.sh
bash scripts/run.sh
```

`install.sh` downloads Station **v0.1.0-beta.10** and shallow-clones that tag into `norma-core/`. Serials and the task sentence live in `elrobot.env`. The SmolVLA trainer in the tag is 6-DoF and needs CUDA; ElRobot has 8 servos.

| Step | Command (from `elrobot`) |
| --- | --- |
| Install | `bash scripts/install.sh` |
| Config | `cp elrobot.env.example elrobot.env` |
| Start Station | `bash scripts/run.sh` |
| Calibrate follower | `bash scripts/calibrate.sh` |
| Teleop | `bash scripts/teleop.sh` |
| Export parquet | `bash scripts/export_dataset.sh <START> <END>` |
| Convert to LeRobot v2.1 | [data collection](elrobot/docs/data-collection.md#convert-to-lerobot) (`scripts/export_to_lerobot.py`) |

Upstream: [norma-core](https://github.com/norma-core/norma-core/tree/v0.1.0-beta.10)

---

## Document map

| Document | Covers |
| --- | --- |
| [SO-101 setup](so101/README.md) | Install, calibrate, collect, train, deploy |
| [ElRobot setup](elrobot/README.md) | Install, calibrate, collect, train, deploy |
| [SO-101 data collection](so101/docs/data-collection.md) | `lerobot-record`, H.264, LeRobot v3 |
| [ElRobot data collection](elrobot/docs/data-collection.md) | Station tags, parquet export, LeRobot v2.1 conversion |
| [SO-101 DevLab](so101/docs/devlab.md) | Recommended GPU workspace: data, fine-tune, policy server |
| [SO-101 train and deploy](so101/docs/train-and-deploy.md) | CPU smoke, DevLab, Jobs, rollout |
| [ElRobot train and deploy](elrobot/docs/train-and-deploy.md) | SmolVLA fine-tune, deploy, evaluation |

The two datasets are separate. Norma's SmolVLA trainer reads Station parquet. `elrobot/scripts/export_to_lerobot.py` writes a LeRobot **v2.1** folder from those parquets. SO-101 training reads LeRobot **v3**.

## Local data

Nothing under `data/` is committed.

| Stack | Where recordings land |
| --- | --- |
| ElRobot export | `data/elrobot-pizza.parquet` and `data/elrobot-pizza.mp4` (prefix `../data/elrobot-pizza` in `elrobot.env`) |
| SO-101 | `~/.cache/huggingface/lerobot/${HF_USER}/${DATASET_NAME}_<timestamp>/` |

---

## Quick facts

- **Format:** Teleoperate → Collect Data → Fine-Tune → Deploy → Compete
- **Three challenges:** Precision Topping (30 pts) · Recipe Assembly (40 pts) · Mystery Pizza (30 pts) — 100 pts total
- **Primary KPI:** ≥70% of participating teams successfully deploy one autonomous learned policy to a real robot
- **Platforms:** each team uses both the SO-101 kit (LeRobot) and the ElRobot kit (NormaCore Station)
