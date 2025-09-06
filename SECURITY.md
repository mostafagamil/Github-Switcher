# Security Policy

## Reporting Security Vulnerabilities

We take the security of GitHub Switcher seriously. If you believe you have found a security vulnerability, please report it responsibly.

### Reporting Process

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, please send an email to: **mostafa_gamil@yahoo.com**

Include the following information:
- Type of issue (buffer overflow, SQL injection, cross-site scripting, etc.)
- Full paths of source file(s) related to the manifestation of the issue
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

### Response Timeline

- **Initial Response**: Within 48 hours of report receipt
- **Status Update**: Weekly updates on investigation progress
- **Resolution**: Security fixes prioritized and released as soon as possible

### Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

### Security Measures

GitHub Switcher implements several security best practices:

**SSH Key Security:**
- Ed25519 keys (GitHub recommended, cryptographically secure)
- Proper file permissions (600 for private keys, 644 for public keys)
- No private key storage in configuration files or exports
- Secure key generation using cryptography library

**Configuration Security:**
- No plaintext credential storage
- Input validation and sanitization
- Atomic configuration updates with backup creation
- Protected configuration directory permissions

**Code Security:**
- Type safety with comprehensive type hints
- Input validation for all user inputs
- Secure file operations with proper error handling
- No shell injection vulnerabilities

### Responsible Disclosure

We believe in responsible disclosure and will:
- Acknowledge your report within 48 hours
- Work with you to understand and reproduce the issue
- Keep you informed of our progress
- Credit you in our security advisory (if desired)
- Notify you when the issue is resolved

Thank you for helping keep GitHub Switcher secure!