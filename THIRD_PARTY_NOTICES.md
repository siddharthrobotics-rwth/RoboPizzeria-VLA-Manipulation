# Attribution and licensing

This repository retains the Robotics Pizza Hackathon starter material and its
Git history. The original overview is preserved in [HACKATHON.md](HACKATHON.md).
Portfolio preparation adds review fixes, offline checks and evidence boundaries;
it does not establish authorship of the upstream robotics or policy stacks.

- **LeRobot / Hugging Face**: SO-101 control, dataset APIs, ACT and SmolVLA
  integration. Dependency pinned to 0.6.1 in `so101/pyproject.toml` and `uv.lock`.
  Upstream: https://github.com/huggingface/lerobot (Apache-2.0).
- **NormaCore**: Station, generated client bindings, remote teleoperation and
  `smolvla_py`. Installer targets `v0.1.0-beta.10` from
  https://github.com/norma-core/norma-core. The local upstream checkout has an
  MIT root license (Copyright 2026 NormaCore) and a separate Apache-2.0 license
  at `software/ai/smolvla_py/LICENSE.md`. Preserve component-specific licenses
  when redistributing. The upstream checkout is ignored and is not vendored here.
- **SmolVLA base checkpoint**: `lerobot/smolvla_base` on Hugging Face; model weights
  and their applicable model-card terms are separate from this repository.
- The Station converter retains its reference to the LeRobot v0.3.3 dataset
  implementation. Other existing source notices and documentation links remain.

No repository-wide LICENSE was present in the starting tracked tree. No new
license or copyright ownership is asserted here. The maintainers must choose
and authorize a license for their own contributions before representing this
repository as licensed open source. Dependency licenses do not license this
repository as a whole. Dataset usage and redistribution rights also require
separate verification; recordings and weights are excluded.
