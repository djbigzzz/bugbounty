# Burp Suite Bug Bounty Testing Checklist

## Setup
- [ ] Configure browser proxy (127.0.0.1:8080)
- [ ] Install Burp CA certificate in browser
- [ ] Add target to scope (Target > Scope settings)
- [ ] Enable "Use advanced scope control"
- [ ] Start Burp logging (Project > Project options > Misc > Logging)

---

## 1. RECONNAISSANCE (Passive)

### 1.1 Sitemap Analysis
- [ ] Browse entire application manually with Burp intercepting
- [ ] Review Target > Site map for all discovered endpoints
- [ ] Look for hidden/backup files: `.bak`, `.old`, `.swp`, `~`
- [ ] Check for exposed config files: `web.config`, `.env`, `config.php`
- [ ] Look for API endpoints: `/api/`, `/v1/`, `/graphql`
- [ ] Note authentication endpoints: `/login`, `/register`, `/forgot-password`
- [ ] Identify admin panels: `/admin`, `/dashboard`, `/manage`

### 1.2 Response Analysis
- [ ] Check HTTP headers for info disclosure (Server, X-Powered-By)
- [ ] Look for comments in HTML source
- [ ] Check JavaScript files for API keys, secrets, endpoints
- [ ] Review cookies (HttpOnly, Secure, SameSite flags)
- [ ] Note session token format and entropy

---

## 2. AUTHENTICATION TESTING

### 2.1 Login Mechanism
- [ ] Test for username enumeration (different error messages)
- [ ] Test for timing-based username enumeration
- [ ] Check for default credentials (admin:admin, test:test)
- [ ] Test password reset for token leakage
- [ ] Check if password reset token is predictable
- [ ] Test for account lockout bypass
- [ ] Check "Remember me" token security

### 2.2 Session Management
- [ ] Check if session token changes after login
- [ ] Test session fixation (can you set your own session?)
- [ ] Check session timeout behavior
- [ ] Test concurrent session handling
- [ ] Verify logout actually invalidates session
- [ ] Check session token in URL (bad practice)

### 2.3 Multi-Factor Authentication (if present)
- [ ] Can MFA be bypassed by modifying response?
- [ ] Is MFA code reusable?
- [ ] Test MFA code brute-force protection
- [ ] Check if MFA can be disabled without re-authentication

---

## 3. AUTHORIZATION TESTING (IDOR/BAC)

### 3.1 Horizontal Privilege Escalation
- [ ] Create two accounts (user A and user B)
- [ ] Access user A's resources, note the IDs/parameters
- [ ] Try accessing same resources with user B's session
- [ ] Test ID parameters: `id=`, `user_id=`, `account=`, `uid=`
- [ ] Check for predictable IDs (sequential integers)
- [ ] Try UUIDs from other users if exposed

### 3.2 Vertical Privilege Escalation
- [ ] Identify admin-only functions
- [ ] Try accessing admin endpoints as regular user
- [ ] Modify role parameters: `role=admin`, `isAdmin=true`
- [ ] Check if API endpoints have different auth than web UI
- [ ] Test parameter manipulation: `admin=1`, `access_level=9`

### 3.3 IDOR Locations to Test
- [ ] User profile: `/api/users/123`
- [ ] Documents/files: `/files/download?id=456`
- [ ] Orders/transactions: `/orders/789`
- [ ] Messages/notifications: `/messages/321`
- [ ] Settings/preferences: `/settings?user=123`

---

## 4. INJECTION TESTING

### 4.1 SQL Injection
- [ ] Test all input fields with: `'`, `"`, `\`
- [ ] Try: `' OR '1'='1`, `' OR 1=1--`, `" OR ""="`
- [ ] Test numeric fields: `1 OR 1=1`, `1' OR '1'='1`
- [ ] Check ORDER BY: `1,2,3` (incrementing until error)
- [ ] Test UNION-based: `' UNION SELECT NULL--`
- [ ] Try time-based: `'; WAITFOR DELAY '0:0:5'--`
- [ ] Use Burp Intruder with SQLi wordlist

### 4.2 Cross-Site Scripting (XSS)
**Reflected XSS:**
- [ ] Test all URL parameters with: `<script>alert(1)</script>`
- [ ] Try: `"><script>alert(1)</script>`
- [ ] Test: `javascript:alert(1)` in href/src attributes
- [ ] Try event handlers: `" onmouseover="alert(1)`
- [ ] Test SVG: `<svg onload=alert(1)>`
- [ ] Check error messages for reflection

**Stored XSS:**
- [ ] Test all user input that gets displayed: names, comments, bios
- [ ] Test file upload names
- [ ] Check profile fields, forum posts, reviews

**DOM XSS:**
- [ ] Check for `document.location`, `document.URL` in JS
- [ ] Test URL fragments: `#<script>alert(1)</script>`
- [ ] Review JavaScript for dangerous sinks

### 4.3 Command Injection
- [ ] Test with: `; ls`, `| cat /etc/passwd`, `&& whoami`
- [ ] Try: `` `id` ``, `$(whoami)`
- [ ] Test common injection points: filename, host, IP inputs

### 4.4 Server-Side Template Injection (SSTI)
- [ ] Test: `{{7*7}}`, `${7*7}`, `<%= 7*7 %>`
- [ ] Try: `{{config}}`, `{{self}}`
- [ ] Test in email templates, PDF generators, error pages

### 4.5 XML/XXE Injection
- [ ] Test file uploads accepting XML
- [ ] Try: `<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>`
- [ ] Check SOAP endpoints

---

## 5. BUSINESS LOGIC TESTING

### 5.1 Price/Quantity Manipulation
- [ ] Modify price in request: `price=0.01`
- [ ] Test negative quantities: `quantity=-1`
- [ ] Apply coupon codes multiple times
- [ ] Test race conditions on limited offers

### 5.2 Workflow Bypass
- [ ] Skip steps in multi-step process
- [ ] Access final step directly via URL
- [ ] Modify state parameters: `step=final`
- [ ] Test what happens if you go backwards

### 5.3 Rate Limiting
- [ ] Test login brute force protection
- [ ] Check API rate limits
- [ ] Test OTP/verification code limits
- [ ] Look for rate limit bypass via headers (X-Forwarded-For)

---

## 6. FILE UPLOAD TESTING

- [ ] Upload file with double extension: `file.php.jpg`
- [ ] Change Content-Type to `image/jpeg` for PHP file
- [ ] Try null byte: `file.php%00.jpg`
- [ ] Upload `.htaccess` file
- [ ] Test SVG with XSS payload
- [ ] Check if uploaded file path is disclosed
- [ ] Try path traversal in filename: `../../../etc/passwd`
- [ ] Test file size limits

---

## 7. API TESTING

### 7.1 Common API Issues
- [ ] Test API without authentication
- [ ] Check for verbose error messages
- [ ] Test mass assignment: add extra fields like `isAdmin`
- [ ] Check for API versioning issues: `/v1/` vs `/v2/`
- [ ] Test HTTP method switching (GET to POST, etc.)

### 7.2 GraphQL (if present)
- [ ] Query introspection: `{__schema{types{name}}}`
- [ ] Test for batching attacks
- [ ] Check for deeply nested queries (DoS)
- [ ] Test field suggestions in errors

---

## 8. MISCELLANEOUS

### 8.1 Information Disclosure
- [ ] Check `/robots.txt`, `/sitemap.xml`
- [ ] Look for `.git/`, `.svn/`, `.DS_Store`
- [ ] Test debug endpoints: `/debug`, `/trace`, `/status`
- [ ] Check error pages for stack traces
- [ ] Review JavaScript source maps

### 8.2 Security Headers Missing
- [ ] X-Frame-Options (clickjacking)
- [ ] Content-Security-Policy
- [ ] X-Content-Type-Options
- [ ] Strict-Transport-Security

### 8.3 CORS Misconfiguration
- [ ] Test with Origin header: `Origin: https://evil.com`
- [ ] Check if `Access-Control-Allow-Origin: *`
- [ ] Test `null` origin

### 8.4 CSRF
- [ ] Check if state-changing requests have CSRF tokens
- [ ] Test if CSRF token is validated
- [ ] Try removing CSRF token entirely
- [ ] Test if token is tied to session

---

## BURP TIPS

### Useful Burp Extensions
- AuthMatrix - Authorization testing
- Autorize - Automatic authorization testing
- Param Miner - Hidden parameter discovery
- JSON Web Tokens - JWT testing
- Hackvertor - Encoding/decoding
- Logger++ - Advanced logging

### Intruder Attack Types
- **Sniper**: Single payload set, one position at a time
- **Battering Ram**: Same payload in all positions
- **Pitchfork**: Multiple payload sets, synchronized
- **Cluster Bomb**: All payload combinations

### Repeater Tips
- Right-click > "Send to Repeater" for manual testing
- Use Ctrl+R to send request
- Compare responses with Comparer tool

---

## REPORTING

When you find a bug:
1. Document exact reproduction steps
2. Take screenshots/video
3. Capture the vulnerable request from Burp
4. Assess impact (what can attacker do?)
5. Suggest remediation
6. Calculate severity (CVSS if required)

---

## Quick Payloads Reference

```
# XSS
<script>alert(document.domain)</script>
"><img src=x onerror=alert(1)>
javascript:alert(1)

# SQLi
' OR '1'='1
' UNION SELECT NULL,NULL--
'; DROP TABLE users--

# SSTI
{{7*7}}
${7*7}
<%= 7*7 %>

# Command Injection
; whoami
| cat /etc/passwd
`id`

# Path Traversal
../../../etc/passwd
....//....//....//etc/passwd
```
