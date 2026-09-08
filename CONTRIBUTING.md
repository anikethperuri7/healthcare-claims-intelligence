# Contributing

Pull requests and issues are welcome.

```bash
git clone https://github.com/anikethperuri7/healthcare-claims-intelligence.git
cd healthcare-claims-intelligence
pip install -e ".[dev]"
ruff check src tests scripts
black --check src tests scripts
pytest --cov=claims_intelligence
```

Use synthetic data only. Never commit PHI, proprietary payer data, or real provider/member identifiers.
