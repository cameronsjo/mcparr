# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| latest  | Yes       |

## Reporting a Vulnerability

Please report security vulnerabilities through [GitHub private advisories](https://github.com/cameronsjo/mcparr/security/advisories/new).

**Do not** open a public issue for security vulnerabilities.

## Response Timeline

| Phase | Target |
|-------|--------|
| Acknowledgment | 48 hours |
| Initial assessment | 7 days |
| Fix release | 30 days |

## Disclosure Policy

We follow coordinated disclosure. After a fix is released, we will publish an advisory with credit to the reporter.

## Security Considerations

- API keys are passed via environment variables, never committed to code
- The server does not implement its own authentication — it relies on the upstream gateway (agentgateway) for auth
- All *arr service communication happens over internal Docker networks
