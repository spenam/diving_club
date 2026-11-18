# Linux installation notes

Install Docker Engine and the Docker Compose plugin from the official Docker
documentation for your Linux distribution. Clone the repository, create `.env`
from `.env.example`, set strong credentials, then run the README quick-start
commands.

For LAN use, assign the host a DHCP reservation or static IP. Allow inbound
TCP 8080 only from the trusted club LAN until HTTPS is configured.

For remote use, prefer VPN access. If exposing a web endpoint, add TLS,
authentication, rate limiting and firewall controls first. The starter app
does not yet implement user authentication.
