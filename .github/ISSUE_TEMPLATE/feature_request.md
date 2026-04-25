---
name: Feature Request
about: Propose a new feature or enhancement for the virtual-test-harness
title: "[Feature] "
labels: enhancement
assignees: ""
---

## Summary
<!-- A clear and concise description of the feature you are proposing. -->

## Motivation
<!-- Why is this feature needed? What problem does it solve or value does it add? -->

## Proposed Solution
<!-- Describe how you envision the feature working. Include any relevant design details. -->

## Acceptance Criteria
<!-- A checklist of conditions that must be true for this feature to be considered complete. -->
- [ ] 
- [ ] 

## Additional Context
<!-- Any mockups, references, related issues, or other information. -->

---

## Agent Checklist
All agents **must** contribute to the pull request that implements this feature. The implementing PR will not be merged until every box below is checked.

- [ ] **Developer** – Application code implemented (`app.py`, Dockerfile, Helm chart, etc.)
- [ ] **Test-Engineer** – Unit/integration tests added or updated to cover the new behaviour
- [ ] **Telemetry-Engineer** – OpenTelemetry instrumentation added or verified for new code paths
- [ ] **Doc-Writer** – `README.md` and/or `docs/` updated to reflect the new feature
- [ ] **Security-Engineer** – Security review completed; no new vulnerabilities introduced ✅
- [ ] **Automation-Engineer** – devcontainer, VS Code tasks, and CI/CD workflows updated if affected
- [ ] **Data-Engineer** – Sample data in `inbox/` created or updated if schema/format changed
- [ ] **Dev-Manager** – Final quality review completed; all agent contributions verified ✅
