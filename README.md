# Justvihxn Docker Bot 

Justvihxn is a Discord-based VPS/container management bot with WebSSH, resource controls, per-instance persistent storage, port forwarding, expiration, billing, and admin tooling.

## What changed

- Docker replaces the previous LXC/LXD runtime.
- Every VPS gets its own named volume: `justvihxn_<container>_data`, mounted at `/data`.
- CPU and RAM are enforced with Docker limits.
- Requested disk size is recorded as Docker labels. **Docker named volumes do not enforce a quota by themselves**; use an XFS project-quota Docker data root or a storage plugin when hard per-volume quotas are required.
- Port forwards are managed through the host's `JUSTVIHXN_DOCKER` iptables chain.
- Each VPS receives password-based root SSH. WebSSH connects from the control plane directly to the VPS private Docker IP on port 22, so no public VPS IP is required.
- The bot, service, commands, website title, database tables, and visible copy use Justvihxn branding.

## Requirements

- A fresh Debian 12 or Ubuntu 22.04/24.04 server
- Root or sudo access
- Recommended: 2 CPU, 4 GB RAM, 20 GB free disk
- A Discord bot token with Message Content intent enabled
- Ports required for WebSSH and your configured forwarding range

## Installation

```bash
unzip Justvihxn-Docker.zip
cd Justvihxn-Docker
sudo bash install.sh
sudo justvihxn config
```

Set at least:

```dotenv
DISCORD_TOKEN=your_discord_bot_token
MAIN_ADMIN_ID=your_discord_user_id
YOUR_SERVER_IP=203.0.113.10
```

Then start and verify:

```bash
sudo justvihxn start
sudo justvihxn status
sudo justvihxn logs
sudo justvihxn doctor
```

## Discord website login

Create an OAuth2 application in the Discord Developer Portal and add this
redirect URL:

```text
https://YOUR-DOMAIN/oauth/callback
```

Generate a strong session secret:

```bash
openssl rand -hex 32
```

Set the following values in `/opt/justvihxn/.env`:

```dotenv
DISCORD_CLIENT_ID=your_application_id
DISCORD_CLIENT_SECRET=your_oauth_client_secret
DISCORD_REDIRECT_URI=https://YOUR-DOMAIN/oauth/callback
WEB_SESSION_SECRET=your_generated_random_secret
WEB_COOKIE_SECURE=true
```

The website requests Discord's `identify` and `email` OAuth scopes. Discord
only returns an email after the user consents. The dashboard stores the
Discord ID, username, display name, consented email, verification state, login
timestamps, login count, and connecting IP. Only configured Justvihxn admins
can open the user tracker.

Authenticated users can claim a free VPS, manage start/stop/restart actions,
and open their console without seeing the private IP, SSH port, or root
password. Console authorization is checked against the logged-in Discord ID
on every connection.

Useful commands:

```bash
sudo justvihxn containers
sudo justvihxn volumes
sudo justvihxn restart
```

## VPS SSH and WebSSH

During creation and reinstall, Justvihxn installs and starts OpenSSH inside the
managed container. The VPS receives a Docker-private address such as
`172.17.0.4` and listens on port `22`.

The Discord bot sends the private IP, port, root username, password, and a link
to the WebSSH website. The WebSSH backend runs on the same Docker host, so it can
connect directly to that private address even though internet users cannot.
Private Docker addresses may change after a container is recreated; the bot
refreshes the saved address whenever the VPS starts or WebSSH is opened.

This design does not use any external reverse SSH tunnel. Direct SSH
from a user's device to `172.17.x.x` will not work; users should use the WebSSH
website unless the host has separate public port forwarding.

## Firewall

If UFW is enabled, allow the WebSSH port and forwarding range (adjust as needed):

```bash
sudo ufw allow 6767/tcp
sudo ufw allow 20000:67670/tcp
sudo ufw allow 20000:67670/udp
```

## Persistent storage

User data should be kept in `/data` inside each VPS container. Deleting a VPS through Justvihxn removes both its container and dedicated volume. Normal container restarts/recreates preserve the volume.

Back up a volume:

```bash
docker run --rm -v justvihxn_CONTAINER_data:/data -v "$PWD":/backup ubuntu:24.04 \
  tar czf /backup/CONTAINER-data.tgz -C /data .
```

## Hard disk quotas (optional)

The `PUBLIC_VPS_MAX_DISK`/plan disk value is retained as metadata. To enforce hard quotas, configure Docker's `overlay2.size` support on an XFS filesystem mounted with `pquota`, or use a quota-aware volume driver. Test this on a staging host before production.

## Remote nodes

The included installer configures the local Docker node. Existing remote-node entries must point to an API agent that executes the supplied Docker shell command and returns `returncode`, `stdout`, and `stderr`. Install Docker and iptables on every node and protect the node API with its key and a firewall.

## Security notes

Managed containers receive elevated capabilities (`NET_ADMIN`, `SYS_ADMIN`, `/dev/fuse`) for compatibility with the existing VPS feature set. This is not suitable for untrusted public multi-tenancy without additional isolation. For hostile tenants, use rootless Docker, gVisor/Kata Containers, or full KVM VMs and remove unnecessary capabilities.

## Updating an existing Justvihxn installation

The redesigned dashboard keeps the existing Docker creation and private-console backend. Back up your live files, copy the new frontend and bot, then restart:

```bash
sudo cp /opt/justvihxn/bot.py /opt/justvihxn/bot.py.backup
sudo cp /opt/justvihxn/webssh.html /opt/justvihxn/webssh.html.backup
sudo cp ./bot.py ./webssh.html /opt/justvihxn/
sudo chown root:root /opt/justvihxn/bot.py /opt/justvihxn/webssh.html
sudo systemctl restart justvihxn
sudo systemctl status justvihxn --no-pager -l
```

The Discord Developer Portal redirect URL must exactly match `DISCORD_REDIRECT_URI`, including `https://` and `/oauth/callback`.

## Port 6767 and admin fleet manager

The website now defaults to port `6767`. Existing installations keep their current `.env`, so change them explicitly:

```bash
sed -i 's/^WEBSSH_PORT=.*/WEBSSH_PORT=6767/' /opt/justvihxn/.env
systemctl restart justvihxn
ss -lntp | grep ':6767'
```

Users manage their own Docker VPS from Dashboard. Accounts listed in `MAIN_ADMIN_ID` or the bot admin database also receive Fleet manager and User tracker navigation. Fleet manager can search all VPS instances, open the existing private console, start, restart, suspend, unsuspend, reinstall, and permanently delete a VPS and its dedicated volume.
