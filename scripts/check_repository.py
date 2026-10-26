#!/usr/bin/env python3
"""Read-only offline portfolio checks; never import or execute project entrypoints."""
from __future__ import annotations

import ast
import importlib.util
from pathlib import Path
import re
import subprocess
import sys
import tomllib
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]


def eligible_files() -> list[str]:
    result = subprocess.run(
        ['git', 'ls-files', '-c', '-o', '--exclude-standard', '-z'],
        cwd=ROOT, check=True, capture_output=True,
    )
    return sorted(set(name.decode() for name in result.stdout.split(b'\0') if name))


def main() -> int:
    files = eligible_files()
    errors = []
    counts = {'Python': 0, 'Bash': 0, 'TOML': 0, 'YAML': 0, 'Markdown links': 0}
    yaml_available = importlib.util.find_spec('yaml') is not None
    if yaml_available:
        import yaml
    # High-confidence patterns only. Findings report paths/line numbers, never values.
    secret_pattern = re.compile(
        r'\bhf_[A-Za-z0-9]{24,}\b|\b(?:AKIA|ASIA)[A-Z0-9]{16}\b|'
        r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|'
        r'\bgh[pousr]_[A-Za-z0-9]{30,}\b'
    )
    forbidden = {'.pt', '.pth', '.ckpt', '.safetensors', '.bin', '.parquet', '.mp4', '.zip'}
    for name in files:
        path = ROOT / name
        if not path.is_file():
            errors.append(f'{name}: missing or not a regular file')
            continue
        if path.stat().st_size > 5 * 1024 * 1024 or path.suffix in forbidden:
            errors.append(f'{name}: large/generated artifact in publication set')
        parts = path.relative_to(ROOT).parts
        if any(part in {'.aws', '.venv', 'venv', 'checkpoints', 'datasets', 'norma-core'}
               or part.startswith('.venv') for part in parts):
            errors.append(f'{name}: local/generated directory in publication set')
        if path.name in {'.env', 'station.env', 'elrobot.env'}:
            errors.append(f'{name}: local configuration in publication set')
        try:
            content = path.read_text()
        except UnicodeDecodeError:
            errors.append(f'{name}: unexpected binary file; inspect before publication')
            continue
        for line_number, line in enumerate(content.splitlines(), 1):
            if secret_pattern.search(line):
                errors.append(f'{name}:{line_number}: possible credential; inspect privately')
        try:
            if path.suffix == '.py':
                ast.parse(content, filename=name)
                counts['Python'] += 1
            elif path.suffix == '.sh':
                result = subprocess.run(['bash', '-n', str(path)], capture_output=True, text=True)
                if result.returncode:
                    errors.append(f'{name}: Bash syntax failed: {result.stderr.strip()}')
                counts['Bash'] += 1
            elif path.suffix == '.toml' or path.name == 'uv.lock':
                tomllib.loads(content)
                counts['TOML'] += 1
            elif path.suffix in {'.yaml', '.yml'} or path.name.endswith('.yaml.example'):
                if yaml_available:
                    yaml.safe_load(content)
                    counts['YAML'] += 1
            if path.suffix == '.md':
                for target in re.findall(r'\[[^\]]*\]\(([^\s)]+)(?:\s+[^)]*)?\)', content):
                    if target.startswith(('https:', 'http:', 'mailto:', '#')):
                        continue
                    target = unquote(target.split('#', 1)[0].strip('<>'))
                    if target and not (path.parent / target).exists():
                        errors.append(f'{name}: missing local link target {target}')
                    counts['Markdown links'] += 1
        except (SyntaxError, ValueError) as error:
            errors.append(f'{name}: parse failed: {error}')
        except Exception as error:
            errors.append(f'{name}: check failed: {type(error).__name__}: {error}')
    examples = ['.env.example', '.env-devlab.example', 'so101/station.env.example',
                'elrobot/elrobot.env.example', 'elrobot/station.yaml.example']
    for name in examples:
        if name not in files:
            errors.append(f'{name}: example missing from publication set')
    probes = ['.env', '.env.local', '.aws/credentials', '.venv-export/pyvenv.cfg',
              'so101/station.env', 'elrobot/elrobot.env', 'elrobot/norma-core/LICENSE',
              'data/sample.parquet', 'datasets/sample.json', 'checkpoints/model.safetensors',
              'nested/model.pt', 'nested/model.bin', 'nested/recording.mp4', 'wandb/run.json']
    for name in probes:
        result = subprocess.run(['git', 'check-ignore', '-q', '--', name], cwd=ROOT)
        if result.returncode != 0:
            errors.append(f'{name}: exclusion probe failed')
    print(f'Inspected {len(files)} publication files; counts: {counts}')
    print(f'Ignore probes: {len(probes)}; required templates: {len(examples)}')
    if not yaml_available:
        print('SKIP: YAML parsing (PyYAML unavailable)')
    for error in errors:
        print(f'FAIL: {error}')
    print('FAIL' if errors else 'PASS: offline repository checks')
    print('Credential pattern scan is heuristic; history and runtime compatibility require separate review.')
    return bool(errors)


if __name__ == '__main__':
    sys.exit(main())
