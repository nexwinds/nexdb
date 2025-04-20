# Security Policy

## Our Commitment

At NEXDB, we take security seriously. We're committed to ensuring our software is as secure as possible and addressing any vulnerabilities promptly. We appreciate the efforts of security researchers and our community in helping us maintain a secure product.

## Supported Versions

We provide security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability in NEXDB, please follow these steps:

1. **Do not disclose the vulnerability publicly** until we've had a chance to address it.
2. Email your findings to `security@nexwinds.com`.
3. Include detailed information about the vulnerability, including:
   - A clear description of the issue
   - Steps to reproduce the vulnerability
   - Potential impact
   - Any suggestions for mitigation

We will acknowledge receipt of your report within 48 hours and provide an estimated timeline for a fix.

## Security Response Process

Our process for handling security reports:

1. Initial assessment (within 48 hours)
2. Investigation and validation
3. Develop and test a fix
4. Release patched version
5. Public disclosure (if appropriate, and only after a fix is available)

## Best Practices for Secure Usage

When using NEXDB, we recommend the following security practices:

### Database Security

- Use strong, unique passwords for all database accounts
- Implement the principle of least privilege for database users
- Regularly audit user permissions and access
- Keep your database servers behind firewalls with restricted access

### Application Security

- Run NEXDB behind a secure reverse proxy when exposed to the internet
- Keep NEXDB and all its dependencies up to date
- Use TLS/SSL for all connections
- Consider implementing additional authentication mechanisms
- Regularly review application logs for suspicious activity

### Deployment Security

- Deploy in environments with appropriate security controls
- Use secure, unique credentials for NEXDB's admin account
- Separate production and development environments
- Perform regular backups of your configuration and data
- Consider a Web Application Firewall (WAF) for additional protection

## Security Updates and Announcements

We announce security issues in the following ways:

- Security advisories on our GitHub repository
- Notices in our release notes
- Email notifications for critical vulnerabilities (subscribe through our website)

Stay informed by:
- Watching our GitHub repository
- Following us on social media
- Subscribing to our security mailing list

## Security Audits

We conduct regular internal security reviews of our codebase. We welcome feedback from security researchers and our community to help improve our security posture.

---

Remember, no software is 100% secure. If you have concerns or questions about NEXDB's security, please contact us at security@nexwinds.com.
