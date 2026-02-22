# Security Policy

*[Deutsche Version](SECURITY.de.md)*

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| latest  | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in PixelGroomer, please report it
by opening a private security advisory on GitHub:

1. Go to the repository's **Security** tab
2. Click **Report a vulnerability**
3. Provide a detailed description of the issue

We will respond as quickly as possible and work with you to address the issue.

## Security Considerations

PixelGroomer processes local files and does not:

- Connect to external servers (except for package installation)
- Store or transmit personal data
- Require elevated privileges

However, when using this tool:

- Be cautious with `.import.yaml` files from untrusted sources
- Review scripts before running them with sensitive photo collections
- Keep dependencies updated (`pip install -U -r requirements.txt`)
