# Security Practices Specification

## Overview

This document specifies the security requirements and practices for the TTRPG Game Notes project. Security is a critical aspect of development that must be considered at every stage from design through deployment.

## Purpose

Security practices ensure:
- **Protection:** User data and application assets are protected
- **Compliance:** Application meets security standards and regulations
- **Prevention:** Common vulnerabilities are prevented proactively
- **Detection:** Security issues are identified before production
- **Response:** Security incidents can be handled effectively

## Security Review Requirements

### Mandatory Security Reviews

All code changes must undergo security review:

1. **Pre-Commit Review**
   - Developer self-review using security checklist
   - Automated security scanning (if available locally)
   - No secrets or credentials in code

2. **Pull Request Review**
   - Security engineer agent review (for security-sensitive changes)
   - Development manager review
   - Automated CodeQL scanning

3. **Pre-Deployment Review**
   - Final security verification
   - Dependency vulnerability check
   - Infrastructure security review

### Review Triggers

Security review is **required** for changes involving:
- Authentication or authorization logic
- Input validation or sanitization
- Database queries or data access
- API endpoints or HTTP handlers
- Secrets management or credentials
- Infrastructure configuration
- Third-party library additions/updates
- File upload or download functionality
- Session management
- Cryptographic operations

## OWASP Top 10 Compliance

All code must be reviewed against the OWASP Top 10 (2021):

### A01:2021 – Broken Access Control

**Requirements:**
- Implement authorization checks for all protected resources
- Verify user permissions before allowing access
- Use role-based or claim-based authorization
- Deny by default (explicit allow required)
- Prevent insecure direct object references

**Implementation:**
```csharp
[Authorize(Roles = "Admin")]
public async Task<IActionResult> DeleteCampaign(int id)
{
    // Verify user owns the resource
    var campaign = await _service.GetByIdAsync(id);
    if (campaign.UserId != User.GetUserId())
    {
        return Forbid();
    }
    
    await _service.DeleteAsync(id);
    return Ok();
}
```

### A02:2021 – Cryptographic Failures

**Requirements:**
- Enforce HTTPS for all connections
- Encrypt sensitive data at rest
- Use strong encryption algorithms (AES-256)
- Store secrets in Azure Key Vault
- Never log sensitive data
- Use hashing (bcrypt, Argon2) for passwords

**Implementation:**
```csharp
// Use managed identities for Azure resources
services.AddDbContext<ApplicationDbContext>(options =>
{
    options.UseSqlServer(configuration.GetConnectionString("DefaultConnection"));
    // Connection uses managed identity, not password
});
```

### A03:2021 – Injection

**Requirements:**
- Use parameterized queries or ORM (Entity Framework Core)
- Never concatenate user input into queries
- Validate and sanitize all input
- Use allowlists for validation
- Encode output appropriately

**Implementation:**
```csharp
// ✅ GOOD: Parameterized query via EF Core
public async Task<Campaign> GetByIdAsync(int id)
{
    return await _context.Campaigns
        .Where(c => c.Id == id)
        .FirstOrDefaultAsync();
}

// ❌ BAD: String concatenation (SQL injection risk)
// var query = $"SELECT * FROM Campaigns WHERE Id = {id}";
```

### A04:2021 – Insecure Design

**Requirements:**
- Follow secure design principles
- Implement defense in depth
- Use principle of least privilege
- Separate concerns appropriately
- Design for security from the start
- Threat modeling for new features

**Practices:**
- Security review during design phase
- Security requirements documented
- Secure defaults configured
- Failure states handled securely

### A05:2021 – Security Misconfiguration

**Requirements:**
- Remove unnecessary features and frameworks
- Keep all software up to date
- Use secure default configurations
- Implement security headers
- Disable directory browsing
- Remove debug features in production

**Implementation:**
```csharp
// Configure security headers
app.Use(async (context, next) =>
{
    context.Response.Headers.Add("X-Content-Type-Options", "nosniff");
    context.Response.Headers.Add("X-Frame-Options", "DENY");
    context.Response.Headers.Add("X-XSS-Protection", "1; mode=block");
    context.Response.Headers.Add("Referrer-Policy", "no-referrer");
    await next();
});
```

### A06:2021 – Vulnerable and Outdated Components

**Requirements:**
- Regularly update all dependencies
- Monitor for security advisories
- Remove unused dependencies
- Use GitHub Advisory Database
- Check dependencies before adding

**Commands:**
```bash
# Check for vulnerable packages
dotnet list package --vulnerable

# Check for outdated packages
dotnet list package --outdated

# Use gh-advisory-database tool (automated in workflow)
```

### A07:2021 – Identification and Authentication Failures

**Requirements:**
- Implement multi-factor authentication (where applicable)
- Use strong password requirements
- Secure session management
- Implement account lockout
- Log authentication failures
- Use secure password reset process

**Implementation:**
```csharp
services.AddAuthentication()
    .AddCookie(options =>
    {
        options.Cookie.HttpOnly = true;
        options.Cookie.SecurePolicy = CookieSecurePolicy.Always;
        options.Cookie.SameSite = SameSiteMode.Strict;
        options.ExpireTimeSpan = TimeSpan.FromHours(8);
        options.SlidingExpiration = true;
    });
```

### A08:2021 – Software and Data Integrity Failures

**Requirements:**
- Verify integrity of dependencies
- Use signed packages when available
- Implement CI/CD pipeline security
- Verify deployment artifacts
- Protect against deserialization attacks

**Practices:**
- Review all dependency updates
- Use trusted package sources only
- Sign commits for critical changes
- Verify build artifacts

### A09:2021 – Security Logging and Monitoring Failures

**Requirements:**
- Log all authentication events
- Log authorization failures
- Log input validation failures
- Monitor for suspicious patterns
- Protect log data
- Alert on critical security events

**Implementation:**
```csharp
public async Task<IActionResult> Login(LoginModel model)
{
    var user = await _userManager.FindByEmailAsync(model.Email);
    if (user == null)
    {
        _logger.LogWarning("Login attempt for non-existent user: {Email}", 
            model.Email);
        return Unauthorized();
    }
    
    var result = await _signInManager.PasswordSignInAsync(user, 
        model.Password, model.RememberMe, lockoutOnFailure: true);
    
    if (!result.Succeeded)
    {
        _logger.LogWarning("Failed login attempt for user: {UserId}", 
            user.Id);
    }
    else
    {
        _logger.LogInformation("Successful login for user: {UserId}", 
            user.Id);
    }
    
    return result.Succeeded ? Ok() : Unauthorized();
}
```

### A10:2021 – Server-Side Request Forgery (SSRF)

**Requirements:**
- Validate all URLs from user input
- Use allowlist for external URLs
- Implement network segmentation
- Limit outbound connections
- Validate redirect destinations

**Implementation:**
```csharp
public async Task<IActionResult> FetchResource(string url)
{
    // Validate URL is in allowlist
    if (!IsAllowedUrl(url))
    {
        _logger.LogWarning("SSRF attempt blocked: {Url}", url);
        return BadRequest("Invalid URL");
    }
    
    var response = await _httpClient.GetAsync(url);
    return Ok(await response.Content.ReadAsStringAsync());
}
```

## CodeQL Security Scanning

### Scanning Requirements

**Mandatory Scanning:**
- All pull requests must pass CodeQL scan
- Scan runs automatically in CI/CD pipeline
- No high or critical vulnerabilities allowed
- Medium vulnerabilities must be reviewed

### CodeQL Configuration

**Languages Scanned:**
- C# (web-app, function-app)
- JavaScript/TypeScript (ui-tests)
- Go (infra-tests)

**Queries Used:**
- security-extended (includes security and quality rules)
- security-and-quality (default set)

### Handling CodeQL Results

**Critical/High Severity:**
- ❌ Must be fixed before merge
- Security engineer review required
- Document fix in PR description

**Medium Severity:**
- Review and assess impact
- Fix if legitimate security concern
- Document if false positive

**Low Severity:**
- Review for context
- Fix if simple
- May defer if low risk

### Running CodeQL Locally

While CodeQL is primarily run in CI/CD, you can review patterns:
```bash
# Check for common SQL injection patterns
grep -rE "ExecuteSqlRaw|FromSqlRaw" --include="*.cs" .

# Check for hardcoded secrets (basic check)
grep -rIE "(password|secret|key|token)\s*=\s*['\"][^'\"]+['\"]" \
  --include="*.cs" --exclude-dir={bin,obj} .
```

## Dependency Vulnerability Checking

### GitHub Advisory Database

**Automated Checking:**
- All dependencies checked against GitHub Advisory Database
- Integrated in CI/CD pipeline
- Runs before adding new dependencies

**Manual Checking:**
```bash
# Check for vulnerable NuGet packages
dotnet list package --vulnerable

# Check specific package
dotnet list package --include-transitive | grep PackageName
```

### Dependency Management

**Adding Dependencies:**
1. Check GitHub Advisory Database first
2. Review package maintainer and reputation
3. Check for recent updates and activity
4. Verify license compatibility
5. Document reason for dependency

**Updating Dependencies:**
- Review changelogs for breaking changes
- Test thoroughly after updates
- Update regularly (monthly for non-breaking)
- Update immediately for security patches

**Example Workflow:**
```bash
# Before adding a dependency
# 1. Research the package
# 2. Check advisory database (automated via gh-advisory-database tool)
# 3. Add dependency
dotnet add package PackageName --version 1.2.3
# 4. Run tests
dotnet test
# 5. Run security scan
dotnet list package --vulnerable
```

## Secure Coding Practices

### Input Validation

**Requirements:**
- Validate all user input
- Use strong typing
- Implement data annotations
- Check length, format, and range
- Use allowlists over denylists

**Implementation:**
```csharp
public class CreateCampaignRequest
{
    [Required]
    [StringLength(200, MinimumLength = 1)]
    [RegularExpression(@"^[a-zA-Z0-9\s\-_]+$")]
    public string Name { get; set; }
    
    [StringLength(2000)]
    public string Description { get; set; }
}

[HttpPost]
public async Task<IActionResult> Create([FromBody] CreateCampaignRequest request)
{
    if (!ModelState.IsValid)
    {
        return BadRequest(ModelState);
    }
    
    // Proceed with validated input
}
```

### Output Encoding

**Requirements:**
- Encode all output by default (Razor does this automatically)
- Use `@Html.Raw()` only for trusted content
- Sanitize HTML input if allowed
- Use Content Security Policy headers

**Implementation:**
```cshtml
@* Razor automatically encodes output *@
<h1>@Model.Name</h1>

@* Only use Raw for trusted, sanitized content *@
@Html.Raw(Model.SanitizedHtml)
```

### Secrets Management

**Requirements:**
- ❌ Never commit secrets to source control
- ✅ Use Azure Key Vault for all secrets
- ✅ Use managed identities for authentication
- ✅ Use user secrets for local development
- ✅ Rotate secrets regularly

**Implementation:**
```csharp
// appsettings.json - NO secrets here
{
  "KeyVault": {
    "Url": "https://myvault.vault.azure.net/"
  }
}

// Program.cs - Load from Key Vault
builder.Configuration.AddAzureKeyVault(
    new Uri(builder.Configuration["KeyVault:Url"]),
    new DefaultAzureCredential());
```

**Local Development:**
```bash
# Set user secrets (not committed)
dotnet user-secrets set "ConnectionStrings:DefaultConnection" "connection-string"
```

### Error Handling

**Requirements:**
- Never expose stack traces to users in production
- Log detailed errors server-side
- Return generic error messages to clients
- Sanitize error messages (no sensitive data)
- Use appropriate HTTP status codes

**Implementation:**
```csharp
public async Task<IActionResult> GetCampaign(int id)
{
    try
    {
        var campaign = await _service.GetByIdAsync(id);
        if (campaign == null)
        {
            return NotFound();
        }
        return Ok(campaign);
    }
    catch (Exception ex)
    {
        // Log detailed error
        _logger.LogError(ex, "Error retrieving campaign {CampaignId}", id);
        
        // Return generic error to client
        return StatusCode(500, "An error occurred while processing your request.");
    }
}
```

### Database Security

**Requirements:**
- Use parameterized queries (EF Core handles this)
- Apply principle of least privilege to database users
- Use connection pooling
- Enable encryption in transit (SSL/TLS)
- Enable encryption at rest for sensitive data
- Use managed identities for authentication

**Implementation:**
```csharp
// Connection string using managed identity
services.AddDbContext<ApplicationDbContext>(options =>
{
    var connectionString = configuration.GetConnectionString("DefaultConnection");
    options.UseSqlServer(connectionString, sqlOptions =>
    {
        sqlOptions.EnableRetryOnFailure(
            maxRetryCount: 3,
            maxRetryDelay: TimeSpan.FromSeconds(30),
            errorNumbersToAdd: null);
    });
});
```

### Authentication and Authorization

**Requirements:**
- Implement authentication for protected resources
- Use authorization attributes on controllers/actions
- Verify user identity before sensitive operations
- Implement CSRF protection for state-changing operations
- Use SameSite cookies

**Implementation:**
```csharp
[Authorize]
[ValidateAntiForgeryToken]
public class CampaignsController : Controller
{
    [HttpPost]
    public async Task<IActionResult> Delete(int id)
    {
        // Authorization check
        var campaign = await _service.GetByIdAsync(id);
        if (campaign.UserId != User.GetUserId())
        {
            _logger.LogWarning(
                "User {UserId} attempted to delete campaign {CampaignId} " +
                "belonging to user {OwnerId}",
                User.GetUserId(), id, campaign.UserId);
            return Forbid();
        }
        
        await _service.DeleteAsync(id);
        return RedirectToAction(nameof(Index));
    }
}
```

## Infrastructure Security

### Azure Security Best Practices

**App Service:**
- Enable HTTPS only
- Use managed identities
- Configure authentication/authorization
- Enable diagnostic logging
- Configure custom domain with SSL

**Azure Functions:**
- Use function authorization levels appropriately
- Implement custom authentication for HTTP triggers
- Use managed identities for dependencies
- Enable Application Insights

**Azure SQL Database:**
- Use managed identity authentication
- Enable Advanced Threat Protection
- Enable auditing
- Configure firewall rules (minimal access)
- Enable transparent data encryption

**Key Vault:**
- Use RBAC for access control
- Enable soft delete
- Enable purge protection
- Monitor access logs
- Rotate secrets regularly

**Storage Accounts:**
- Use SAS tokens with minimal permissions
- Enable soft delete
- Configure network restrictions
- Enable encryption at rest
- Monitor access logs

### Infrastructure as Code Security

**Terraform Security:**
```bash
# Validate Terraform configuration
cd infra && terraform validate

# Check for security issues (if tfsec installed)
cd infra && tfsec .

# Check for secrets
grep -r "password\|secret\|key" infra/ --include="*.tf"
```

**Requirements:**
- No secrets in Terraform files
- Use secure defaults for resources
- Implement network security groups
- Enable encryption by default
- Use managed identities
- Follow least privilege principle

## Security Testing

### Security Test Categories

**Authentication Tests:**
```csharp
[Fact]
public async Task AccessProtectedResource_WithoutAuth_Returns401()
{
    // Test unauthorized access is denied
}
```

**Authorization Tests:**
```csharp
[Fact]
public async Task DeleteCampaign_ByNonOwner_Returns403()
{
    // Test users can't access others' resources
}
```

**Input Validation Tests:**
```csharp
[Theory]
[InlineData("")]
[InlineData("<script>alert('xss')</script>")]
[InlineData("'; DROP TABLE Campaigns; --")]
public async Task CreateCampaign_WithMaliciousInput_ReturnsValidationError(string input)
{
    // Test malicious input is rejected
}
```

**CSRF Tests:**
```csharp
[Fact]
public async Task StateChangingAction_WithoutCSRFToken_Returns400()
{
    // Test CSRF protection is enforced
}
```

## Security Checklist

Before merging any code:

### Code Review
- [ ] No secrets or credentials in code
- [ ] All input is validated
- [ ] All output is encoded
- [ ] SQL injection prevented (parameterized queries)
- [ ] XSS prevented (output encoding)
- [ ] CSRF protection implemented
- [ ] Authentication required for protected resources
- [ ] Authorization checked for sensitive operations
- [ ] Error handling doesn't expose sensitive info
- [ ] Logging doesn't include sensitive data

### Dependency Security
- [ ] New dependencies checked against GitHub Advisory Database
- [ ] All dependencies are up to date
- [ ] No vulnerable dependencies (dotnet list package --vulnerable)
- [ ] Dependencies are from trusted sources
- [ ] License compatibility verified

### Testing
- [ ] Security test cases added
- [ ] Authentication tests pass
- [ ] Authorization tests pass
- [ ] Input validation tests pass
- [ ] All tests pass locally

### Scanning
- [ ] CodeQL scan passes
- [ ] No high or critical vulnerabilities
- [ ] Medium vulnerabilities reviewed and addressed

### Infrastructure
- [ ] No secrets in infrastructure code
- [ ] Managed identities used where possible
- [ ] Secure defaults configured
- [ ] Network security configured
- [ ] Encryption enabled

## Security Incident Response

### If a Vulnerability is Discovered

1. **Assess Severity:**
   - Critical: Immediate exploitation possible
   - High: Exploitation likely with minimal effort
   - Medium: Exploitation requires specific conditions
   - Low: Theoretical or limited impact

2. **Document:**
   - What is the vulnerability?
   - How can it be exploited?
   - What is the impact?
   - Which versions are affected?

3. **Fix:**
   - Develop and test fix
   - Review fix for security impact
   - Test thoroughly

4. **Deploy:**
   - Deploy fix to production ASAP (critical/high)
   - Follow normal deployment (medium/low)

5. **Communicate:**
   - Notify stakeholders
   - Update security documentation
   - Conduct post-mortem if needed

## Documentation Requirements

### Security Documentation
Maintain documentation in `docs/`:
- `security-findings.md` - Vulnerability tracking
- `security-guidelines.md` - Security best practices
- This specification document

### Change Documentation
For security fixes, document:
- What was fixed
- Why it was a vulnerability
- How to verify the fix
- Any breaking changes

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP Cheat Sheets](https://cheatsheetseries.owasp.org/)
- [Microsoft Security Development Lifecycle](https://www.microsoft.com/en-us/securityengineering/sdl/)
- [Azure Security Best Practices](https://docs.microsoft.com/azure/security/)
- [ASP.NET Core Security](https://docs.microsoft.com/aspnet/core/security/)
- [GitHub Advisory Database](https://github.com/advisories)
- [CWE Top 25](https://cwe.mitre.org/top25/)

## Change History

- 2026-02-13: Initial specification created