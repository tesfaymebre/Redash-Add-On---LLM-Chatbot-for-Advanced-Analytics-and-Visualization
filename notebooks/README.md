# Notebooks

Exploratory analysis for the YouTube analytics dataset (Task 2c).

## Setup

```bash
make install          # includes jupyter, matplotlib, seaborn
make db-up db-init db-load
```

## Run EDA

**Interactive (recommended for learning):**

```bash
make eda
# Opens notebooks/task-02c-eda-youtube.ipynb in Jupyter
```

**Headless (exports figures + markdown summary):**

```bash
make eda-export
```

Outputs:
- `docs/architecture/figures/` — saved charts
- `docs/architecture/eda-findings.md` — written insights
