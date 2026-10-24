#!/usr/bin/env python3
"""Audit .deb links in zh_CN against M5Stack APT indexes.

Reports:
- HTTP status for every linked .deb
- platform directory mismatch between the link and its APT source tag
- whether the linked package version is current in the matching Packages index
"""
import concurrent.futures
import pathlib
import re
import subprocess
import sys
import urllib.request

BASE = "https://repo.llm.m5stack.com/m5stack-apt-repo"
INDEXES = {
    "ax630c": ("jammy", "ax630c"),
    "ax650c": ("jammy", "ax650c"),
    "llm8850": ("bookworm", "llm8850"),
}
URL_RE = re.compile(r"https://repo\.llm\.m5stack\.com[^ )\"'>]*\.deb")


def latest_versions():
    result = {}
    for arch, (distro, component) in INDEXES.items():
        url = f"{BASE}/dists/{distro}/{component}/binary-arm64/Packages"
        data = urllib.request.urlopen(url, timeout=60).read().decode()
        versions = {}
        for block in data.split("\n\n"):
            pkg = re.search(r"^Package: (.+)$", block, re.M)
            ver = re.search(r"^Version: (.+)$", block, re.M)
            if not (pkg and ver):
                continue
            key = pkg.group(1)
            value = ver.group(1)
            parsed = tuple(int(x) if x.isdigit() else x for x in re.split(r"[.\-+~]", value))
            if key not in versions or parsed > versions[key][0]:
                versions[key] = (parsed, value)
        result[arch] = {k: v[1] for k, v in versions.items()}
    return result


def head_status(url):
    proc = subprocess.run(
        ["curl", "-sSIL", "--max-time", "30", url],
        capture_output=True, text=True,
    )
    status = ""
    size = ""
    for line in proc.stdout.splitlines():
        if line.startswith("HTTP/"):
            status = line.split()[1]
        elif line.lower().startswith("content-length:"):
            size = line.split(":", 1)[1].strip()
    return status, size


def main(root):
    root = pathlib.Path(root)
    latest = latest_versions()
    rows = []
    for path in root.rglob("*.md"):
        text = path.read_text(encoding="utf-8", errors="replace")
        doc_arches = set(re.findall(r"deb \[[^\]]+\]\s+\S+\s+\S+\s+(ax\d+[a-z]?|llm8850)\b", text))
        for match in URL_RE.finditer(text):
            url = match.group(0)
            line = text.count("\n", 0, match.start()) + 1
            parsed = re.search(r"/pool/(?:jammy|bookworm)/([^/]+)/([^/]+)/([^/]+\.deb)$", url)
            if not parsed:
                rows.append((str(path.relative_to(root)), line, url, "", "", "", "unparsed"))
                continue
            arch, version_dir, filename = parsed.groups()
            pkg = re.match(r"(.+)_(.+)-m5stack\d+_arm64\.deb$", filename)
            package, version = pkg.groups() if pkg else ("", "")
            status, size = head_status(url)
            issues = []
            if status != "200":
                issues.append(f"HTTP {status}")
            if doc_arches and arch not in doc_arches:
                issues.append(f"platform {arch} not in {sorted(doc_arches)}")
            current = latest.get(arch, {}).get(package)
            if current and version != current:
                issues.append(f"version {version} != latest {current}")
            rows.append((str(path.relative_to(root)), line, url, arch, size, package, version, "; ".join(issues) or "OK"))
    print("file\tline\turl\tplatform\tsize\tpackage\tversion\tissues")
    for row in rows:
        print("\t".join(map(str, row)))
    bad = [r for r in rows if r[-1] != "OK"]
    print(f"SUMMARY links={len(rows)} flagged={len(bad)}", file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "zh_CN")
