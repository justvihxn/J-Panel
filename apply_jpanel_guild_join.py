#!/usr/bin/env python3
from pathlib import Path
import base64, gzip, os, shutil, subprocess, sys, time

APP = Path("/opt/jpanel")
BOT = APP / "bot.py"
WEB = APP / "webssh.html"
REQ = APP / "requirements.txt"
ENV = APP / ".env"
GUILD_ID = "1540619481494200371"
PATCH_DATA = "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"

if os.geteuid() != 0:
    raise SystemExit("Run with sudo/root: python3 apply_jpanel_guild_join.py")
for path in (BOT, WEB, REQ, ENV):
    if not path.exists():
        raise SystemExit(f"Missing {path}")

stamp = time.strftime("%Y%m%d-%H%M%S")
backup = APP / f"guild-join-backup-{stamp}"
backup.mkdir()
for path in (BOT, WEB, REQ, ENV):
    shutil.copy2(path, backup / path.name)
print("Backup:", backup)

code = BOT.read_text()
if "async def bringback_authorized_members" not in code:
    patch_file = APP / ".guild-join.patch"
    patch_file.write_bytes(gzip.decompress(base64.b64decode(PATCH_DATA)))
    try:
        subprocess.run(["patch", "--batch", "--forward", "-p0", "-i", str(patch_file)], cwd=APP, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"Patch failed. Restore files from {backup}. Error: {exc}")
    finally:
        patch_file.unlink(missing_ok=True)
else:
    print("Guild-join code already present; skipped bot.py patch")

requirements = REQ.read_text()
if "cryptography>=" not in requirements:
    REQ.write_text(requirements.rstrip() + "\ncryptography>=42,<46\n")

web = WEB.read_text()
web = web.replace(
    "Discord shares your identity and email only after consent.",
    "Discord shares your identity, email, and server-join permission only after consent.",
)
WEB.write_text(web)

subprocess.run([str(APP / "venv/bin/pip"), "install", "-r", str(REQ)], check=True)

existing = {}
kept = []
for line in ENV.read_text().splitlines():
    if line.startswith("DISCORD_GUILD_ID="):
        existing["DISCORD_GUILD_ID"] = line.split("=", 1)[1]
    elif line.startswith("OAUTH_TOKEN_ENCRYPTION_KEY="):
        existing["OAUTH_TOKEN_ENCRYPTION_KEY"] = line.split("=", 1)[1]
    else:
        kept.append(line)
key = existing.get("OAUTH_TOKEN_ENCRYPTION_KEY", "").strip()
if not key or key == "GENERATED_FERNET_KEY":
    key = subprocess.check_output([
        str(APP / "venv/bin/python"), "-c",
        "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())",
    ], text=True).strip()
kept += ["", f"DISCORD_GUILD_ID={GUILD_ID}", f"OAUTH_TOKEN_ENCRYPTION_KEY={key}"]
ENV.write_text("\n".join(kept).rstrip() + "\n")
os.chmod(ENV, 0o600)

subprocess.run([str(APP / "venv/bin/python"), "-m", "py_compile", str(BOT)], check=True)
print("Guild ID configured:", GUILD_ID)
print("Encryption key: SET")
print("Patch complete. Restart with: systemctl restart jpanel")
