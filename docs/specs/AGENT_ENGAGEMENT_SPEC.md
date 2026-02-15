# Agent Engagement Model Specification

## Overview

This specification defines when and how different GitHub Copilot agents should be engaged during development work. It ensures that the right expertise is applied at the right time, maintaining quality, consistency, and adherence to project standards.

## Purpose

This specification:
- **Clarifies Responsibility:** Defines clear triggers for agent engagement
- **Ensures Quality:** Guarantees appropriate review and oversight for all work
- **Enables Coordination:** Facilitates collaboration between multiple agents
- **Prevents Gaps:** Ensures no critical aspect of development is overlooked
- **Maintains Standards:** Enforces consistent application of project practices

## Agent Engagement Matrix

### When Working On... Engage These Agents

| Work Type | Required Agents | Reason |
|-----------|----------------|---------|
| Any work | Security Engineer, Product Owner, Development Manager | All work requires security validation, requirements review, and quality oversight |
| Web app changes | Web App Agent, Test Agent, Telemetry Engineer, Security Engineer | Primary development, test coverage, telemetry validation, security validation |
| Function app changes | Function App Agent, Test Agent, Telemetry Engineer, Security Engineer | Primary development, test coverage, telemetry validation, security validation |
| UI changes | Web Designer, UI Tester, Web App Agent, Docs Agent | Design/accessibility, Playwright tests, implementation, documentation |
| Database changes | Database Agent, Test Agent, Telemetry Engineer | Schema design, migrations, proto models, test coverage, telemetry validation |
| Entity Framework changes | Database Agent, Web App Agent/Function App Agent, Telemetry Engineer | Data model updates, code generation, integration, telemetry validation |
| Infrastructure changes | Automation Engineer | Deployment configuration, CI/CD pipeline updates |
| CI/CD workflow changes | Automation Engineer, Security Engineer | Pipeline maintenance, security validation |
| New features | Docs Agent, Test Agent, Telemetry Engineer, Product Owner, Development Manager | Documentation, test coverage, telemetry validation, requirements validation, quality review |
| New tools/dependencies | Dev-Tools Developer, Security Engineer | Devcontainer updates, vulnerability scanning |
| Documentation updates | Docs Agent | Technical writing, consistency, completeness |
| Test additions | Test Agent, relevant domain agent | Test coverage, test quality, domain expertise |

## Detailed Agent Engagement Rules

### 1. Automation Engineer Agent

**Engage When:**
- Making changes to `.github/workflows/` (CI/CD pipelines)
- Adding or modifying deployment scripts
- Changing build configurations that affect CI/CD
- Adding new automated tests that need CI/CD integration
- Updating infrastructure deployment processes
- Troubleshooting CI/CD pipeline failures

**Responsibilities:**
- Ensure all parts of the application are deployable
- Validate all automated tests execute on PRs to main branch
- Maintain GitHub Actions workflows
- Optimize CI/CD pipeline performance and reliability
- Document workflow changes

**Engagement Pattern:**
```
Primary: Infrastructure and workflow changes
Consulting: When new features need CI/CD integration
```

### 2. Database Agent

**Engage When:**
- Creating or modifying Entity Framework entities
- Adding or updating database migrations
- Designing new data models
- Changing database schemas
- Creating proto files for data models
- Optimizing database queries
- Troubleshooting database performance issues

**Responsibilities:**
- Design and implement data models as proto3 files in `proto/` directory
- Create and maintain Entity Framework migrations
- Ensure database changes are compatible across web-app and function-app
- Implement database operations with proper telemetry
- Validate data access patterns follow best practices

**Engagement Pattern:**
```
Primary: All Entity Framework and database schema work
Consulting: When features require new data models
```

### 3. Dev-Tools Developer Agent

**Engage When:**
- Adding new development tools to the repository
- Updating devcontainer configuration
- Modifying Dockerfile
- Changing VS Code tasks or settings
- Adding or updating development dependencies
- Troubleshooting development environment issues

**Responsibilities:**
- Maintain devcontainer and development environment
- Ensure all required tools are available and properly configured
- Document tool setup and usage
- Keep development dependencies up to date
- Validate development environment consistency

**Engagement Pattern:**
```
Primary: Devcontainer and tooling changes
Consulting: When new tools are needed for features
```

### 4. Docs Agent

**Engage When:**
- Creating any new feature (always)
- Making user-facing changes
- Updating APIs or interfaces
- Changing configuration options
- Adding new components or services
- Modifying deployment procedures
- Creating specifications or guidelines

**Responsibilities:**
- Draft and maintain all technical documentation
- Create user-facing documentation for new features
- Update README files and guides
- Document API changes and examples
- Maintain consistency in documentation style
- Ensure documentation completeness

**Engagement Pattern:**
```
Primary: All documentation work
Required: For every new feature or user-facing change
```

### 5. Function App Agent

**Engage When:**
- Creating or modifying Azure Functions
- Changing function app configuration
- Adding new endpoints to function-app
- Updating function app dependencies
- Implementing background processing logic
- Troubleshooting function app issues

**Responsibilities:**
- Implement all function app features and changes
- Ensure proper dependency injection usage
- Implement telemetry and logging
- Follow Azure Functions best practices
- Maintain function app test coverage

**Engagement Pattern:**
```
Primary: All function-app/ directory changes
```

### 6. Web App Agent

**Engage When:**
- Creating or modifying ASP.NET Core controllers
- Changing web app views (non-UI styling)
- Adding new web app endpoints
- Updating web app configuration
- Implementing business logic in web-app
- Troubleshooting web app issues

**Responsibilities:**
- Implement all web application features and changes
- Ensure proper MVC patterns are followed
- Implement authentication and authorization
- Maintain web app test coverage
- Integrate with database and services properly

**Engagement Pattern:**
```
Primary: All web-app/ directory changes (excluding pure CSS)
Collaboration: With Web Designer for UI implementations
```

### 7. Web Designer Agent

**Engage When:**
- Creating or modifying UI components
- Changing CSS styles or layouts
- Updating visual design elements
- Implementing responsive design
- Ensuring accessibility compliance (WCAG 2.1 AA)
- Maintaining fantasy RPG theme consistency
- Making any changes to user-facing interface

**Responsibilities:**
- Design and implement UI/UX styling
- Maintain fantasy RPG aesthetic across the application
- Ensure responsive design for all screen sizes
- Validate WCAG 2.1 AA accessibility compliance
- Provide UI consistency recommendations
- Review all UI changes for design quality

**Engagement Pattern:**
```
Primary: All CSS and visual design work
Consulting: For all UI changes to ensure consistency and accessibility
```

### 8. UI Tester Agent

**Engage When:**
- Making any UI changes (always)
- Creating new user-facing features
- Modifying existing UI components
- Changing user workflows or navigation
- Adding new pages or views

**Responsibilities:**
- Create Playwright tests for all UI changes
- Ensure UI test coverage meets standards
- Validate user workflows end-to-end
- Test accessibility requirements
- Maintain and update existing UI tests
- Ensure tests run successfully in CI/CD

**Engagement Pattern:**
```
Primary: Creating and maintaining Playwright tests
Required: For every UI change
```

### 9. Security Engineer Agent

**Engage When:**
- On all work (security review is required for everything)
- Adding or updating dependencies
- Implementing authentication or authorization
- Handling user input
- Making database queries
- Exposing new APIs or endpoints
- Changing security configurations
- Adding external integrations

**Responsibilities:**
- Review all code changes for security vulnerabilities
- Validate OWASP Top 10 compliance
- Check dependencies for known vulnerabilities using GitHub Advisory Database
- Ensure input validation and output encoding
- Verify secrets are not committed
- Run CodeQL security scanning
- Document security findings and recommendations

**Engagement Pattern:**
```
Primary: Security reviews and vulnerability assessments
Required: For all work before deployment
```

### 10. Product Owner Agent

**Engage When:**
- On all work (requirements review is required for everything)
- Starting new features or projects
- Defining acceptance criteria
- Creating definition of done
- Validating completed work
- Making architectural decisions
- Changing project standards

**Responsibilities:**
- Review requirements for completeness and clarity
- Define and validate definition of done (DoD)
- Ensure work meets acceptance criteria
- Verify standards compliance
- Work with Development Manager on quality assurance
- Approve work that meets all DoD criteria

**Engagement Pattern:**
```
Primary: Requirements definition and validation
Required: For all work - upfront for scoping, at end for validation
```

### 11. Development Manager Agent

**Engage When:**
- On all work (quality oversight is required for everything)
- Scoping new features with Product Owner
- Coordinating work across multiple agents
- Conducting architectural reviews
- Validating work quality before completion
- Resolving integration conflicts
- Making technical decisions

**Responsibilities:**
- Oversee and coordinate all development agents
- Ensure quality, consistency, and compatibility
- Validate work meets Product Owner requirements
- Enforce coding standards and best practices
- Conduct architectural and technical reviews
- Coordinate agent collaboration for complex changes

**Engagement Pattern:**
```
Primary: Quality oversight and agent coordination
Required: For all work - during scoping and final review
```

### 12. Test Agent

**Engage When:**
- Implementing new features (always)
- Adding new business logic
- Creating new services or components
- Modifying existing functionality
- Fixing bugs (add regression tests)

**Responsibilities:**
- Ensure unit test coverage on all new features
- Maintain minimum 85% code coverage threshold
- Write integration tests where appropriate
- Follow test organization patterns (#region directives)
- Ensure all tests pass in CI/CD
- Review test quality and effectiveness

**Engagement Pattern:**
```
Primary: Writing and maintaining unit/integration tests
Required: For all new features and functionality changes
```

### 13. Telemetry Engineer Agent

**Engage When:**
- Web app agent makes changes to services or controllers
- Function app agent makes changes to functions
- Database agent makes changes affecting query performance
- Any agent adds new services or operations
- Any agent modifies error handling or logging
- New features are implemented (always)
- Performance-critical code is added or modified

**Responsibilities:**
- Review code for telemetry completeness and quality
- Ensure performance monitoring is in place for all operations
- Verify logging standards are followed
- Validate error handling and exception tracking
- Ensure Azure Application Insights integration
- Check that sensitive data is not logged
- Update TELEMETRY.md documentation
- Provide telemetry implementation guidance

**Engagement Pattern:**
```
Primary: Telemetry review and validation
Required: After implementation, before dev manager/product owner review
Timing: After web app/function app/database agents complete work
```

## Engagement Workflows

### Workflow 1: New Feature Implementation

```
1. Product Owner Agent
   └─> Define requirements, acceptance criteria, DoD

2. Development Manager Agent
   └─> Review requirements, plan architecture, coordinate agents

3. Database Agent (if data model changes needed)
   └─> Design proto models, create migrations

4. Web App Agent OR Function App Agent
   └─> Implement feature logic

5. Web Designer Agent (if UI changes)
   └─> Design and style UI components

6. Docs Agent
   └─> Create feature documentation

7. Test Agent
   └─> Write unit and integration tests

8. UI Tester Agent (if UI changes)
   └─> Write Playwright tests

9. Telemetry Engineer Agent
   └─> Review telemetry completeness and logging

10. Security Engineer Agent
    └─> Conduct security review

11. Development Manager Agent
    └─> Final quality review and integration validation

12. Product Owner Agent
    └─> Final quality review and integration validation

11. Product Owner Agent
    └─> Validate against DoD and accept
```

### Workflow 2: UI Change

```
1. Web Designer Agent
   └─> Design UI/UX, ensure accessibility

2. Web App Agent
   └─> Implement UI components

3. UI Tester Agent
   └─> Create Playwright tests

4. Docs Agent
   └─> Document UI changes

5. Security Engineer Agent
   └─> Review for XSS, CSRF, etc.

6. Development Manager Agent
   └─> Coordinate and validate integration
```

### Workflow 3: Infrastructure/Deployment Change

```
1. Automation Engineer Agent
   └─> Implement workflow/deployment changes

2. Security Engineer Agent
   └─> Review for security issues

3. Product Owner Agent
   └─> Validate requirements met

4. Development Manager Agent
   └─> Validate compatibility with all components
```

### Workflow 4: Database Schema Change

```
1. Database Agent
   └─> Design proto models, create migrations

2. Web App Agent AND Function App Agent (if both use the model)
   └─> Update code to use new schema

3. Test Agent
   └─> Update or create tests for new data access

4. Docs Agent
   └─> Document schema changes

5. Security Engineer Agent
   └─> Review for SQL injection, data protection

6. Development Manager Agent
   └─> Validate compatibility across components
```

## Agent Coordination Principles

### 1. Always-Engaged Agents

These agents must be engaged on **every** piece of work:
- **Security Engineer Agent** - Security is non-negotiable
- **Product Owner Agent** - Requirements validation is required
- **Development Manager Agent** - Quality oversight is mandatory

### 2. Feature-Driven Engagement

For new features, the engagement chain is:
```
Product Owner (requirements) 
  → Development Manager (planning)
  → Domain Agents (implementation)
  → Test Agent (coverage)
  → Docs Agent (documentation)
  → Telemetry Engineer (telemetry/logging)
  → Security Engineer (security)
  → Development Manager (integration)
  → Product Owner (acceptance)
```

### 3. Change-Type-Driven Engagement

Engage agents based on what's changing:
- **UI changes** → Web Designer + UI Tester (always)
- **Data changes** → Database Agent (always)
- **Infrastructure** → Automation Engineer (always)
- **New tools** → Dev-Tools Developer (always)

### 4. Parallel vs. Sequential Engagement

**Parallel (can work simultaneously):**
- Docs Agent and Test Agent (once implementation is stable)
- Web Designer and Web App Agent (for UI work)

**Sequential (must follow order):**
- Product Owner → Development Manager (requirements before planning)
- Database Agent → Domain Agents (models before implementation)
- Domain Agents → Test Agent (implementation before tests)
- Test Agent → Telemetry Engineer (tests before telemetry review)
- Telemetry Engineer → Security Engineer (telemetry before security review)
- Security Engineer → Development Manager → Product Owner (final reviews)

## Verification Checklist

Before considering work complete, verify:

- [ ] **Security Engineer Agent** reviewed all code changes
- [ ] **Product Owner Agent** validated requirements and DoD
- [ ] **Development Manager Agent** conducted quality review
- [ ] **Test Agent** ensured test coverage ≥85%
- [ ] **Telemetry Engineer Agent** reviewed telemetry and logging
- [ ] **Docs Agent** created/updated documentation (for features)
- [ ] **Domain Agent(s)** implemented and tested changes
- [ ] **Database Agent** created migrations (if data changes)
- [ ] **Web Designer Agent** reviewed UI (if UI changes)
- [ ] **UI Tester Agent** created Playwright tests (if UI changes)
- [ ] **Automation Engineer** validated CI/CD integration (if needed)
- [ ] **Dev-Tools Developer** updated devcontainer (if new tools)

## Exception Handling

### When Can Agents Be Skipped?

**Never Skip:**
- Security Engineer Agent
- Product Owner Agent
- Development Manager Agent

**May Skip With Justification:**
- Telemetry Engineer (ONLY for documentation-only changes or infrastructure changes)
- Database Agent (if no data model changes)
- Automation Engineer (if no CI/CD changes)
- Dev-Tools Developer (if no tool changes)
- Web Designer (if no UI changes)
- UI Tester (if no UI changes)
- Docs Agent (ONLY for internal tooling not visible to users)

**Documentation Required:**
- Any agent skipped must be documented in PR description
- Justification must be provided
- Development Manager must approve the skip

## Communication Patterns

### How Agents Should Communicate

1. **Handoffs:** When passing work to another agent, provide:
   - What was completed
   - What needs to be done next
   - Any issues or concerns
   - Files or areas to focus on

2. **Collaboration:** When working with another agent simultaneously:
   - Agree on interface boundaries
   - Communicate frequently about changes
   - Avoid conflicting modifications

3. **Reviews:** When reviewing another agent's work:
   - Be specific and actionable
   - Reference specifications and standards
   - Suggest improvements constructively
   - Approve only when standards are met

4. **Escalations:** When issues arise:
   - Report to Development Manager Agent
   - Provide details and context
   - Suggest possible solutions
   - Wait for guidance before proceeding

## Integration with Definition of Done

This engagement model directly supports the Definition of Done framework defined by the Product Owner Agent. Each agent's engagement ensures specific DoD criteria are met:

| DoD Criteria | Agent(s) Responsible |
|--------------|---------------------|
| Functional requirements | Domain Agents, Product Owner |
| Code quality | All Agents, Development Manager |
| Testing (unit/integration) | Test Agent |
| Testing (UI) | UI Tester Agent |
| Security | Security Engineer Agent |
| Telemetry & Logging | Telemetry Engineer Agent |
| Documentation | Docs Agent |
| Performance | Telemetry Engineer Agent, Domain Agents, Development Manager |
| Integration | Development Manager |

## Continuous Improvement

### Monitoring Engagement Effectiveness

Track these metrics to improve the engagement model:
- **Defects found post-deployment** (by type) → Which agent should have caught them?
- **Rework required** → Was the right agent engaged at the right time?
- **Agent coordination issues** → Are workflows clear enough?
- **DoD criteria missed** → Which agent engagement was skipped or ineffective?

### Updating This Specification

When to update:
- New agent types are added
- Agent responsibilities change significantly
- Workflows prove inefficient or ineffective
- New technologies or practices are adopted
- Patterns emerge that should be standardized

Process:
1. Propose changes via discussion with Development Manager and Product Owner
2. Update specification document
3. Communicate changes to all agents
4. Update agent configurations if needed
5. Document in Change History section

## Quick Reference Card

### For Any Work
✅ **Always Engage:** Security Engineer, Product Owner, Development Manager

### For Specific Changes
- 📱 **UI Changes:** Web Designer → Web App Agent → UI Tester → Docs
- 🗄️ **Data Changes:** Database Agent → Domain Agents → Test Agent → Telemetry Engineer
- 🚀 **CI/CD Changes:** Automation Engineer → Security Engineer
- 🆕 **New Features:** Product Owner → Dev Manager → Domain → Test → Docs → Telemetry Engineer → Security → Dev Manager → Product Owner
- 🔧 **New Tools:** Dev-Tools Developer → Security Engineer
- 📊 **Service/Function Changes:** Domain Agent → Test Agent → Telemetry Engineer → Security Engineer

## Examples

### Example 1: Adding a New Campaign Management Feature

**Agents Engaged (in order):**
1. **Product Owner** - Define requirements, acceptance criteria, DoD
2. **Development Manager** - Review requirements, plan architecture
3. **Database Agent** - Create Campaign proto model, EF migrations
4. **Web App Agent** - Implement controllers, services, view models
5. **Web Designer** - Design campaign cards, fantasy RPG styling
6. **UI Tester** - Create Playwright tests for campaign CRUD
7. **Test Agent** - Write unit tests for services and controllers
8. **Docs Agent** - Document campaign feature in user guide
9. **Telemetry Engineer** - Review telemetry, logging, performance monitoring
10. **Security Engineer** - Review for authorization, input validation, XSS
11. **Development Manager** - Validate integration, test coverage, quality
12. **Product Owner** - Validate against DoD, accept feature

### Example 2: Updating GitHub Actions Workflow

**Agents Engaged:**
1. **Automation Engineer** - Update workflow configuration
2. **Security Engineer** - Review for secrets exposure, permissions
3. **Development Manager** - Validate impact on all components
4. **Product Owner** - Confirm workflow meets deployment requirements

### Example 3: Fixing a Security Vulnerability

**Agents Engaged (in order):**
1. **Security Engineer** - Identify vulnerability, recommend fix
2. **Development Manager** - Prioritize fix, coordinate implementation
3. **Web App Agent OR Function App Agent** - Implement fix
4. **Test Agent** - Add regression tests
5. **Security Engineer** - Validate fix, re-scan
6. **Development Manager** - Approve for deployment
7. **Product Owner** - Validate fix meets requirements

## Resources

### Internal Resources
- [Product Owner Agent](.github/agents/product-owner-agent.md)
- [Development Manager Agent](.github/agents/development-manager-agent.md)
- [Security Engineer Agent](.github/agents/security-engineer-agent.md)
- [All Agent Configurations](.github/agents/)
- [Development Specifications](./README.md)

### Related Specifications
- [UI Testing Specification](./UI_TESTING_SPEC.md) - UI change workflows
- [Security Practices Specification](./SECURITY_SPEC.md) - Security requirements
- [Test Coverage Specification](./TEST_COVERAGE_SPEC.md) - Testing requirements

## Change History

- 2026-02-14: Added Telemetry Engineer Agent v1.1
  - Added Telemetry Engineer Agent to agent engagement model
  - Updated engagement matrix for web app, function app, database, and feature changes
  - Added telemetry engineer to new feature workflow
  - Updated sequential engagement order to include telemetry review before security review
  - Updated verification checklist and DoD integration
  - Added telemetry engineer to quick reference and examples
- 2026-02-13: Initial Agent Engagement Model Specification v1.0
  - Defined engagement rules for all 12 agent types
  - Created engagement workflows for common scenarios
  - Established always-engaged agents (Security, Product Owner, Dev Manager)
  - Defined verification checklist and exception handling
  - Integrated with Definition of Done framework