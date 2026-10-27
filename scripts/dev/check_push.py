"""Local pre-push guard: backup refs and delivery blobs must never reach GitHub."""

import subprocess
import sys


def git(*args):
    return subprocess.check_output(["git", *args], text=True)


def main():
    blocked = []
    for line in sys.stdin:
        local, oid, remote, _ = line.split()
        if local.startswith("refs/heads/backup/") or remote.startswith("refs/heads/backup/"):
            blocked.append("Local backup branches must not be pushed")
            continue
        if set(oid) == {"0"}:
            continue
        for entry in git("rev-list", "--objects", oid).splitlines():
            blob, _, path = entry.partition(" ")
            if not path or git("cat-file", "-t", blob).strip() != "blob":
                continue
            forbidden = (
                path.startswith(("artifacts/", "data/", "models/", "upstream/"))
                and not path.endswith(("/.gitkeep", "/README.md"))
            ) or path.lower().endswith((".tar", ".tar.gz", ".tgz", ".zip", ".oci", ".img", ".iso"))
            if forbidden or int(git("cat-file", "-s", blob)) >= 50 * 1024 * 1024:
                blocked.append("Excluded artifact or oversized blob: " + path)
    if blocked:
        print("Push blocked:\n" + "\n".join(sorted(set(blocked))), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
