# imxTools
A variety of tools for working with IMX.


## 🧪 Development Setup

We highly recommend using [uv](https://github.com/astral-sh/uv) to manage packages and Python versions — it’s ⚡fast and easy 🦾! 

We use the following tools:


- 🧪 `pytest` — Unit Testing
```bash
  uv run pytest
```

- 🧹 `ruff` — Linter & Formatter
```bash
  uv run ruff format   # 🧽 Format code
  uv run ruff check    # 🔎 Lint code
```

- ⚡ `ty` — Fast type checking
```bash
  uv run ty check      # 🧠 Type check
```

- 🌈 `zizmor` — GitHub workflow checking
```bash
  uv run zizmor . 
```


---

## 📦 Managing Dependencies with `uv`

### Setup

Create virtual environment
```bash
  uv venv
```

Activate Windows
```bash
  .venv\Scripts\activate
```

Activate Unix/Mac
```bash
  source .venv/bin/activate  
```

### Install project dependencies

```bash
  uv pip install --editable .
  uv pip install --group dev
  uv pip install --group gui
```

Or all at once:

```bash
  uv pip install --editable . --group dev
```

### Manage Dependencies

```bash
  uv add <pkg>               # Add to main group
  uv add --dev <pkg>         # Add to dev group
  uv sync                    # Sync venv with pyproject.toml
```

📚 See the [uv docs](https://docs.astral.sh/uv/) for full details.

---

## 🧮 Version Bumping



## todo: implement bump-my-version

1. first run
`uv run bump-my-version sample-config --no-prompt --destination .bumpversion.toml`

2. config so we have dev rc final 

3. show bump
`uv run  bump-my-version show-bump`


##### first
check out all docs 
implement flow manually (see docs https://github.com/callowayproject/bump-my-version)
implement flow github actions (see docs https://github.com/callowayproject/bump-my-version)





## TODO: Remove below!!!!

### 🧾 Version Format

Versions follow the pattern:

- 🧪 **Development versions (dev)**: Incremental dev builds  
- 🧬 **Alpha versions (alpha)**: Early pre-release builds for testing  
- 🧯 **Release candidates (rc)**: Final pre-production testing  
- 🐞 **Patch versions (patch)**: Bug fixes  
- ✨ **Minor versions (minor)**: Backward-compatible features  
- 💥 **Major versions (major)**: Breaking changes  

🧭 Typical flow:

dev* → alpha* → rc* → patch/minor/major → next dev*

Use the included CLI tool to bump the package version in `src/rifmp/__init__.py`.



########################################################











## 🪵 Error Monitoring with Sentry

This project includes optional integration with [Sentry.io](https://sentry.io/) for error tracking and diagnostics.

--- 

## 📄 License

[MIT License](LICENSE.md)
