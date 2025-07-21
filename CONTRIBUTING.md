# Development

This document describes the process for running this application on your local computer.

## Development Setup

- ⚠️ We highly recommend using [uv](https://github.com/astral-sh/uv) to manage packages and Python versions — it’s ⚡fast and easy 🦾!
- 📚 See the [uv docs](https://docs.astral.sh/uv/) for how to install and full details about using uv. See below for a quick reference guide. 

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

### 🪝 Pre-commit Hooks

We use the above commands in a pre-commit hook to catch issues before commits are made. 
**Typing is NOT enforced**, but should be on some point.

✅ Pre-commit checks are enforced in CI — always run them locally to avoid CI failures. 
Checks will be forced on commit but can be run manual whit:

```bash
  pre-commit run --all-files
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
  uv sync
  uv pip install --editable .
  uv pip install --group dev
  uv pip install --group gui
```

Or all at once:

```bash
  uv pip install --group dev --group gui .
```
ℹ️ the flag ``--editable`` tells pip (or in this case uv pip) to install the current project in place.
Any changes you make to the code are immediately reflected without needing to reinstall the package.
This is commonly used for local development and

### Manage dependencies

```bash
uv add <pkg>               # Add to main group
uv add --dev <pkg>         # Add to dev group
uv remove <pkg>            # Remove a package
uv update <pkg>            # Upgrade a package
uv sync                    # Sync venv with pyproject.toml
```

💡 **Tip:** Always commit `pyproject.toml` and `uv.lock` before `uv sync`!

---


## 🚀 Development Workflow

This project uses clear conventions to keep our history clean and our releases smooth.

✅ **Follow these rules to ensure your work passes CI and shows up correctly in the changelog.**

✅ **Ideally a branch should contain a implementation of one feature or fix.**

---- 
### 🔀 **Branching Model — Git Flow**

**Main branches**  
- `main` — Production-ready, stable code only.  
- `dev` — Ongoing development and new features.  


**Supporting branches**  
- `feature/<name>` — For new features; branch off `dev` and merge back into `dev`.  
- `rc/<name>` — Release candidates; branch off `dev` and merge into `main`.  
- `fix/<name>` — Hotfixes or urgent patches; branch off `main` and merge back into `main` (and optionally `dev` to keep it up to date).  


---

### ✅ Commit Message Rules

- We use automatic release notes so every commit to dev should follow the commit msg rules.

**All commits on `dev` *****must***** follow these prefixes:**

| Prefix      | Purpose                              |
| ----------- | ------------------------------------ |
| `feat:`     | New features                         |
| `fix:`      | Bug fixes                            |
| `perf:`     | Performance improvements             |
| `chore:`    | Maintenance tasks (deps, etc)        |
| `docs:`     | Documentation updates                |
| `refactor:` | Code refactoring (no feature change) |
| `test:`     | Adding or updating tests             |
| `ci:`       | CI/CD configuration changes          |
| `style:`    | Code style (formatting, lint)        |
| `build:`    | Build system changes                 |


✔️ **Example:**

```bash
  git commit -m "feat: add user login endpoint"
  git commit -m "chore: update pre-commit hooks"
  git commit -m "refactor: simplify validation logic"
```

If needed we can use prefix(additional info) to make things explict.

```bash
  git commit -m "fix(auth): handle expired tokens correctly"
  git commit -m "docs(readme): add branching model section"
  git commit -m "ci(github): add deployment workflow"
```

❌ **Don’t do this:**

```bash
git commit -m "added login feature"
```

💡 Commits **not** matching these prefixes **will be excluded from the changelog!**

#### ✅ Squash Commits for a Clean and clear History.  
Groups related changes together under a single commit with a clear message.
This keeps main and dev clean and easy to read and makes the changelog and version bumps accurate.

---

### ✅ **Typical Workflow**

#### 1️⃣ Create a new feature
- Branch off from `dev` using `feature/<name>`.
- Implement the feature in clear, atomic commits.
- Regularly pull `dev` to stay up to date and resolve conflicts early.
- Before opening a PR, ensure your branch **bumps the version** (every PR must bump `dev`!).
- Open a PR targeting `dev`, following commit message rules.
- Address any review comments.
- A maintainer will squash and merge your PR into `dev`.

---

#### 2️⃣ Prepare a release candidate
- A maintainer creates an `rc/<name>` branch from `dev`.
- The RC signals a **feature freeze** — only bug fixes are allowed.
- The RC is used for acceptance testing and pre-release builds.
- Any fixes must be submitted as PRs targeting the RC.
- All fixes merged into the RC must also be merged back into `dev`.
- Each fix must bump the RC version; each RC build generates a new pre-release tag.
- Once acceptance testing passes, the maintainer:
  - Merges the RC branch into `main` for the final release.
  - Tags `main` with the final `vX.Y.Z` version (without `-rc`).
  - Deletes the RC branch after merge.
- After merging to `main`, merge `main` back into `dev` to ensure `dev` stays ahead.

---

#### 3️⃣ Apply a hotfix or patch
- Hotfixes are only for urgent production issues.
- Create a `fix/<name>` branch from `main`.
- Implement the fix and open a PR targeting `main`.
- The fix must also be merged back into `dev` (and into any active RC).
- The fix must **bump the patch version** in all relevant branches.
- The maintainer merges the PR after review.

---

- ✅ **Every PR to `dev` must bump the version — no exceptions!**
- ✅ **Keep `main` stable and production-ready at all times.**
- ✅ **Keep `dev` always ahead of `main`.**

---


## 🔖 Version Bumping
We manage versions with **bump-my-version**. 

When a new version will be merged in to main or dev, a (pre-)release will be triggered automatically.

1️⃣ Check the next bump:

```bash
bump-my-version show-bump
```

Example output 
```
0.0.1.dev6 ── bump ─┬─ major ─ 1.0.0.dev0
                    ├─ minor ─ 0.1.0.dev0
                    ├─ patch ─ 0.0.2.dev0
                    ├─ pre_l ─ 0.0.1.rc0
                    ╰─ pre_n ─ 0.0.1.dev7
```

2️⃣ Bump the version:

Choose the type of bump you want:
```bash
bump-my-version bump pre_n
```

⚠️ Bumping only works on a clean git repository — the tool will automatically commit and tag the new version.

For now this is a manual proces, we aim to include dev bumps in the ci.

> 🔗 **TODO:** Automate this with GitHub Actions
> 
> See 👉 [bump-my-version docs](https://github.com/callowayproject/bump-my-version)

--- 






## 🧪 Local GitHub Actions Testing with `act`

You can use [`act`](https://github.com/nektos/act) to run your GitHub Actions workflows locally for faster feedback during development.

#### ✅ Basic Usage (Linux/macOS)
```bash
# Run CI workflow
act -W .github/workflows/ci.yml

# Run Build workflow
act -W .github/workflows/build.yml
```


#### 🪟 Running Windows Jobs (Self-hosted Only)
`act` does not support native Windows runners out of the box. You need to simulate them using the `-P` flag with a self-hosted label:

```bash
# Simulate windows-latest using a self-hosted runner
act -W .github/workflows/ci.yml -P windows-latest=self-hosted

act -W .github/workflows/build.yml -P windows-latest=self-hosted
```

> ℹ️ Make sure your local machine has the necessary tools (e.g. Python, uv, etc.) installed when simulating Windows.

---

### 💡 Conditional Steps for `act`

You can use the `ACT` environment variable in your workflow to skip or adapt steps when running locally:

```yaml
if: matrix.os == 'windows-latest' && !env.ACT
```

This lets you:
- Skip setup that doesn't work in `act`
- Mock or echo long-running tasks during local testing

To set the `ACT` variable automatically when running `act`, add this flag:

```bash
act -s ACT=true
```

Or, set it inline:

```bash
ACT=true act -W .github/workflows/ci.yml
```
