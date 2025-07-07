# imxTools
A variety of tools for working with IMX.


## Development Setup

⚠️ We highly recommend using [uv](https://github.com/astral-sh/uv) to manage packages and Python versions — it’s ⚡fast and easy 🦾! 

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
  uv pip install --editable . --group dev --group gui
```

### Manage dependencies

```bash
uv add <pkg>               # Add to main group
uv add --dev <pkg>         # Add to dev group
uv remove <pkg>            # Remove a package
uv update <pkg>            # Upgrade a package
uv sync                    # Sync venv with pyproject.toml
```
💡 **Tip:** Always commit `pyproject.toml` and `uv.lock` before `uv sync`!

📚 See the [uv docs](https://docs.astral.sh/uv/) for full details.  

---

### 🧮 Version Bumping
**We use bump-my-version for manging the versions** 

```shell
  bump-my-version show-bump
```

the pick the version to bump

🧭 Typical flow:

dev* → alpha* → rc* → patch/minor/major → next dev*


#### **TODO implement github actions**
see docs https://github.com/callowayproject/bump-my-version


## 🪵 Error Monitoring with Sentry
This project includes optional integration with [Sentry.io](https://sentry.io/) for error tracking and diagnostics.

--- 

## 📄 License

[MIT License](LICENSE.md)
