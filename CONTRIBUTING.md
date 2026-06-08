# Contributing to SupportGPT Enterprise

Thank you for contributing to SupportGPT Enterprise! To ensure a high level of code quality and alignment, please follow these guidelines when pushing code.

---

## 🛠️ Style Guide and Standards

1. **Python Coding Standards**:
   - Follow PEP 8 style recommendations.
   - Use `black` for automatic code formatting (line limit 88).
   - Use `isort` to organize import files.
2. **Pydantic Schemas**:
   - Always specify default values and parameter field descriptions where applicable to ensure auto-documenting swagger guides are clean.
3. **Database Transactions**:
   - Use async connections (`AsyncSession`) and make sure sessions are closed or committed inside context blocks/dependencies.

---

## 🧪 Testing Guidelines

We enforce a **90%+ test coverage** threshold on all repository check-ins.

1. **Before pushing**:
   - Run the testing suite:
     ```bash
     pytest --cov=src --cov-report=term-missing
     ```
   - Ensure all test assertions pass and no warnings are thrown.
2. **Adding features**:
   - If adding a new agent, write unit tests in `tests/test_agents.py`.
   - If modifying database tables, verify schema creation in `tests/conftest.py`.
