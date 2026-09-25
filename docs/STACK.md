# ttfa stack

Reviewed **2026-09-25** against the latest stable official docs. This page is the pin for the Python package in this repository: the interpreter floor, the `pyproject.toml` build, the unittest suite, and the optional Mojo twin named in the README.

[DESIGN.md](../DESIGN.md) describes a later serving path (Qwen3-TTS, vLLM-Omni, NVIDIA). Those tools are not declared here and are not pinned on this page.

## Pins

| Component | Role here | Declared in the repo | Latest stable on 2026-09-25 | Official docs |
| --- | --- | --- | --- | --- |
| Python | Runtime for `src/ttfa/ref.py` and `tests/` | `requires-python = ">=3.10"` | **3.14.7** (5 Aug 2026), bugfix branch through 2030-10 | [Python 3.14.7 documentation](https://docs.python.org/3.14/) |
| setuptools | PEP 517 build backend | `setuptools>=61` | **84.0.0** (8 Aug 2026) | [setuptools 84.0.0 documentation](https://setuptools.pypa.io/en/stable/) |
| unittest | Test runner | stdlib, no extra dependency | ships with the interpreter pin | [unittest](https://docs.python.org/3.14/library/unittest.html) |
| typing | Reference signatures | stdlib | ships with the interpreter pin | [typing](https://docs.python.org/3.14/library/typing.html) |
| uv | Optional installer for Mojo | README command, no version | **0.12.19** (25 Sep 2026) | [uv documentation](https://docs.astral.sh/uv/) and [release 0.12.19](https://github.com/astral-sh/uv/releases/tag/0.12.19) |
| Mojo | Optional CPU twin of the cut | README command, no version; source comment names 1.0 | **1.1.0** (17 Sep 2026) | [Mojo 1.1.0 docs](https://mojolang.org/docs/) and [v1.1.0 notes](https://mojolang.org/releases/v1.1.0/) |

Python 3.15 is still a prerelease (first release planned 2026-10-01, [PEP 790](https://peps.python.org/pep-0790/), [status table](https://devguide.python.org/versions/)). It is not a pin. The Mojo nightly `1.2.0.dev2026092205` (22 Sep 2026) is not a pin.

## What the tree actually runs

`pyproject.toml` is a [PEP 621](https://peps.python.org/pep-0621/) project table plus a [PEP 517](https://peps.python.org/pep-0517/) / [PEP 518](https://peps.python.org/pep-0518/) build system. There is no `[project.dependencies]` table, no optional-dependencies, no console script, and no lockfile. Runtime imports in `src/ttfa` are the standard library only.

```toml
[project]
name = "ttfa"
version = "0.1.0"
description = "Time-to-first-audio: silence / chunk-boundary kernel"
readme = "README.md"
requires-python = ">=3.10"
authors = [{ name = "lyffseba" }]

[build-system]
requires = ["setuptools>=61"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-data]
ttfa = ["*.mojo"]
```

| Key | Spec | What it does in this repo |
| --- | --- | --- |
| `[project]` | [Declaring project metadata](https://packaging.python.org/en/latest/specifications/pyproject-toml/) and the [writing guide](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/) | Static version `0.1.0`. Readme is `README.md`. Authors is a single name. |
| `requires-python` | same | Accepts 3.10 and every newer feature release. The floor's own docs are the [3.10 documentation](https://docs.python.org/3.10/). Schedule: [PEP 619](https://peps.python.org/pep-0619/). |
| `[build-system]` | [pyproject.toml build-system](https://packaging.python.org/en/latest/specifications/pyproject-toml/) and [setuptools `build_meta`](https://setuptools.pypa.io/en/stable/build_meta.html) | Isolated builds install setuptools, then call `setuptools.build_meta`. |
| `packages.find` `where = ["src"]` | [Package discovery](https://setuptools.pypa.io/en/stable/userguide/package_discovery.html) | src layout. The import package is `ttfa` from `src/ttfa`. |
| `package-data` `ttfa = ["*.mojo"]` | [Data files](https://setuptools.pypa.io/en/stable/userguide/datafiles.html) | Ships `silence.mojo` inside the wheel. setuptools does not compile it. |
| tool config in `pyproject.toml` | [Configuring setuptools using pyproject.toml](https://setuptools.pypa.io/en/stable/userguide/pyproject_config.html) | Discovery and package data live in `[tool.setuptools]`, not `setup.cfg`. |

The README runs tests without installing the wheel:

```bash
PYTHONPATH=src python -m unittest tests.test_silence -v
```

`tests/test_silence.py` subclasses `unittest.TestCase` and calls `unittest.main()`. Assertions in use are `assertEqual`, `assertLess`, `assertGreaterEqual`, and `assertTrue`. `.pytest_cache/` is gitignored; pytest is not a dependency.

`src/ttfa/ref.py` uses `from __future__ import annotations` ([future statements](https://docs.python.org/3.14/reference/simple_stmts.html#future-statements)) and `typing.Sequence`. Those forms are valid on the 3.10 floor and on 3.14.7. Language changes since the floor are summarized in [What's new in Python 3.14](https://docs.python.org/3.14/whatsnew/3.14.html).

`LICENSE` is the Apache License 2.0 text. The `[project]` table does not yet set a [PEP 639](https://peps.python.org/pep-0639/) `license` expression. The packaging guide's license section is [Writing your pyproject.toml](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/).

## Optional Mojo twin

The README installs and runs the twin only when a `mojo` binary is wanted:

```bash
uv pip install mojo
mojo src/ttfa/silence.mojo
```

`uv pip install` is documented at [uv pip packages](https://docs.astral.sh/uv/pip/packages/). With no version specifier, that command resolves the newest stable `mojo` release on PyPI, which on this review date is `mojo==1.1.0`. The `mojo` command itself is [mojo run](https://mojolang.org/docs/cli/run/) when given a file. Stability of the language versus the standard library is [Mojo stability guarantees](https://mojolang.org/docs/api-docs/stability/).

`src/ttfa/silence.mojo` is a SIMD scan for the same cut as the Python reference. The names it uses, and the 1.1.0 pages for them:

| In `silence.mojo` | 1.1.0 reference |
| --- | --- |
| `from std.sys import simd_width_of` | [`simd_width_of`](https://mojolang.org/docs/std/sys/info/simd_width_of/) |
| `DType.float32` | [`DType`](https://mojolang.org/docs/std/builtin/dtype/DType/) |
| `SIMD[DType.float32, WIDTH]` | [`SIMD`](https://mojolang.org/docs/std/simd/SIMD/) and [numeric types](https://mojolang.org/docs/reference/numeric-types/) |
| `Array[Float32, 32]` | [`Array`](https://mojolang.org/docs/std/collections/array/Array/) |
| `Span[Float32, _]` | [`Span`](https://mojolang.org/docs/std/collections/span/Span/) |
| `Pointer[mut=False, Float32, _]` plus `unsafe_offset` / `unsafe_load` | [`Pointer`](https://mojolang.org/docs/std/memory/pointer/Pointer/) and [pointers](https://mojolang.org/docs/manual/pointers/) |

The file header still says "Mojo 1.0". The 1.1.0 notes removed the legacy `fn` / `alias` keywords and the pre-`unsafe_` pointer spellings. This twin already uses `def`, `comptime`, and the `unsafe_*` pointer operations. This page records that match; it does not claim the file was executed on 1.1.0.

## Drift

Checked 2026-09-25 by reading the version tables and the docs titles, then confirming package versions from the PyPI JSON API (`https://pypi.org/pypi/setuptools/json`, and the same path for `uv` and `mojo`).

| Item | Where it stands |
| --- | --- |
| Python floor vs latest stable | The repo allows `>=3.10`. Latest stable is 3.14.7. 3.10 is the security branch ([status](https://devguide.python.org/versions/)); its end-of-life column is `2026-10`. Newest 3.10 patch is 3.10.21 (12 Aug 2026). The reference uses no syntax that 3.10 lacks. |
| Python docs alias | [docs.python.org/3.14/](https://docs.python.org/3.14/) is titled "3.14.7 Documentation", matching the latest 3.14 release. [docs.python.org/3/](https://docs.python.org/3/) shows that same title today. The series URL is the pin because `/3/` moves when a new feature release becomes stable. |
| setuptools floor vs latest stable | `setuptools>=61` bottoms at v61.0.0 (24 Mar 2022). Latest is 84.0.0. There is no upper bound and no lockfile, so an isolated build takes the current release. setuptools 84.0.0 requires `Python >=3.10`, the same floor as this project. |
| setuptools docs slug | [setuptools.pypa.io/en/stable/](https://setuptools.pypa.io/en/stable/) and `/en/latest/` are both titled "setuptools 84.0.0 documentation". `https://setuptools.pypa.io/en/v84.0.0/` returns 404. The stable URL plus the title is the pin. |
| uv | The README does not pin a version. Latest stable is 0.12.19, published 2026-09-25T00:33:02Z. [docs.astral.sh/uv](https://docs.astral.sh/uv/) has no version path; the GitHub release is the version pin. uv 0.12.19 requires Python `>=3.8`, which covers this floor. |
| Mojo package vs docs vs comment | PyPI `mojo` 1.1.0 (uploaded 2026-09-17) matches docs HTML `docs-version-1.1.0` and [the 1.1.0 notes](https://mojolang.org/releases/v1.1.0/). The source comment still says "Mojo 1.0". The install line is unpinned, so the next stable release replaces 1.1.0 without a repo change. |
| Test and cache cruft | Tests are unittest. `.pytest_cache/` and `.pixi/` are gitignored. Neither pytest nor Pixi is declared. |
| License metadata | `LICENSE` is Apache-2.0. `[project]` has no `license` field. |
| Lockfile | No `uv.lock`, `pylock`, or requirements file. Floors float upward to whatever is current on PyPI. |

## Keeping the pins current

Update this page when any pinned project publishes a new stable release, and again at the start of October 2026 when the 3.10 end-of-life month and the planned 3.15 release land. Replace a pin only after the new release is marked stable on the publisher's version table. Leave prereleases and nightlies in the drift section until that happens.

Recheck, from a shell:

```bash
python - << 'PY'
import json, urllib.request
def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "ttfa-stack-docs"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())
for name in ("setuptools", "uv", "mojo"):
    info = get(f"https://pypi.org/pypi/{name}/json")["info"]
    print(f"{name} {info['version']} requires_python={info.get('requires_python')}")
PY
```

Then open these pages and record the version in the title or the release table before editing the pins:

- [Status of Python versions](https://devguide.python.org/versions/) and [python.org/downloads](https://www.python.org/downloads/)
- [Python 3.14 documentation](https://docs.python.org/3.14/) (move the series number when a newer release is stable)
- [setuptools history](https://setuptools.pypa.io/en/stable/history.html)
- [uv releases](https://github.com/astral-sh/uv/releases)
- [Mojo releases](https://mojolang.org/releases/)

After a Mojo bump, re-read the new release notes against `unsafe_*`, `Array`, `Span`, `SIMD`, and `simd_width_of` before treating the twin as still described by the table above.
