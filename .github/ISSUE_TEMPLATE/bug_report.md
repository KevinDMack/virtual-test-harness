---
name: Bug Report
about: Report a defect or unexpected behaviour in the virtual-test-harness
title: "[Bug] "
labels: bug
assignees: ""
---

## Description
<!-- A clear and concise description of the bug. -->

## Steps to Reproduce
1. 
2. 
3. 

## Expected Behaviour
<!-- What you expected to happen. -->

## Actual Behaviour
<!-- What actually happened. Include error messages, stack traces, or log output. -->

## Environment
<!-- Fill in relevant details. -->
| Field | Value |
|---|---|
| Python version | |
| Kubernetes / k3s version | |
| Azure Service Bus SDK version | |
| Deployment method (local / Helm / devcontainer) | |

## Additional Context
<!-- Screenshots, config snippets, related issues, or anything else that helps. -->

---

## Agent Checklist
All agents **must** review and contribute to the pull request that fixes this bug. The fixing PR will not be merged until every box below is checked.

- [ ] **Developer** – Root cause identified and fix implemented (`app.py`, Dockerfile, Helm chart, etc.)
- [ ] **Test-Engineer** – Regression test added to prevent recurrence; existing tests updated if needed
- [ ] **Telemetry-Engineer** – Telemetry verified or updated to correctly capture the failure scenario
- [ ] **Doc-Writer** – Documentation updated if the bug revealed a gap or inaccuracy
- [ ] **Security-Engineer** – Security implications of the bug and the fix reviewed ✅
- [ ] **Automation-Engineer** – CI/CD, devcontainer, or VS Code tasks updated if the bug affected tooling
- [ ] **Data-Engineer** – Sample data updated if the bug was related to inbox format or data handling
- [ ] **Dev-Manager** – Final quality review completed; all agent contributions verified ✅
