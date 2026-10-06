---
name: preserve-existing-tests-and-add-regressions
description: Use this skill when fixing codebases and test suites to ensure original test files remain unmodified while new regression tests are added properly.
---
- Never modify or delete any existing test files provided in the repository's test suite.
- Create new, separate test files (e.g., for regressions or additional coverage) when testing bug fixes.
- Add at least one regression test function per fixed bug into a dedicated test module.
- Ensure all tests pass successfully before finishing the task.