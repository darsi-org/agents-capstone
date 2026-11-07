#!/usr/bin/env python3
"""Darsi capstone check.

Looks at the files in this folder and writes darsi-check.json, which you send to Darsi with your milestone.
It only reads files: it never uploads anything, and Darsi never runs your code. Standard library only.

    python check.py              # every milestone
    python check.py --milestone m2
    python check.py --strict     # exit 1 if a milestone you asked for fails (used by CI if you want it)
"""
import glob
import json
import os
import re
import sys
from datetime import datetime, timezone

SPEC = json.loads(r'''{
 "track": "agents",
 "repo": "agents-capstone",
 "milestones": [
  {
   "id": "m1",
   "en": "Milestone 1: Write your tools as an MCP server",
   "ar": "المرحلة ١: اكتب أدواتك كسيرفر MCP",
   "checks": [
    {
     "type": "regex",
     "path": "tools/server.py",
     "pattern": "@mcp\\.tool",
     "min": 3,
     "en": "tools/server.py has three MCP tools",
     "ar": "يحتوي tools/server.py على ثلاث أدوات MCP"
    },
    {
     "type": "regex",
     "path": "tests/test_tools.py",
     "pattern": "def test_",
     "min": 3,
     "en": "tests/test_tools.py has at least three tests",
     "ar": "في tests/test_tools.py ثلاثة اختبارات على الأقل"
    }
   ]
  },
  {
   "id": "m2",
   "en": "Milestone 2: The loop: a LangGraph agent with a trace",
   "ar": "المرحلة ٢: الحلقة: وكيل LangGraph مع أثر",
   "checks": [
    {
     "type": "glob",
     "pattern": "traces/*.jsonl",
     "min": 5,
     "en": "Five traces in traces/",
     "ar": "خمسة آثار في traces/"
    },
    {
     "type": "regex",
     "path": "agent.py",
     "pattern": "StateGraph",
     "min": 1,
     "en": "agent.py builds a LangGraph graph",
     "ar": "يبني agent.py رسمًا بـ LangGraph"
    }
   ]
  },
  {
   "id": "m3",
   "en": "Milestone 3: Guardrails: allow-lists and asking first",
   "ar": "المرحلة ٣: حواجز الحماية: قوايم السماح والسؤال قبل التصرّف",
   "checks": [
    {
     "type": "regex",
     "path": "agent.py",
     "pattern": "interrupt\\(",
     "min": 1,
     "en": "agent.py asks for approval with interrupt()",
     "ar": "يطلب agent.py الموافقة بـ interrupt()"
    },
    {
     "type": "file",
     "path": "tests/test_guardrails.py",
     "en": "tests/test_guardrails.py exists",
     "ar": "الملف tests/test_guardrails.py موجود"
    }
   ]
  },
  {
   "id": "m4",
   "en": "Milestone 4: Evaluate before you trust",
   "ar": "المرحلة ٤: قيّم قبل ما تثق",
   "checks": [
    {
     "type": "lines",
     "path": "evals/tasks.jsonl",
     "min": 20,
     "en": "20 eval tasks",
     "ar": "٢٠ مهمة تقييم"
    },
    {
     "type": "json",
     "path": "results/eval.json",
     "key": "unapproved_writes",
     "en": "No write happened without approval",
     "ar": "لم تحدث أي كتابة دون موافقة",
     "eq": 0
    }
   ]
  },
  {
   "id": "m5",
   "en": "Milestone 5: Demo and design note",
   "ar": "المرحلة ٥: عرض وملاحظة تصميم",
   "checks": [
    {
     "type": "file",
     "path": "DESIGN.md",
     "en": "DESIGN.md exists",
     "ar": "الملف DESIGN.md موجود"
    },
    {
     "type": "nosecret",
     "en": "No passwords, tokens or keys are in the files",
     "ar": "لا توجد كلمات سر أو رموز أو مفاتيح في الملفات"
    }
   ]
  }
 ]
}''')

LOCAL = re.compile(r"^(https?://)?(localhost|127(\.\d{1,3}){3}|\[::1\]|[a-z0-9-]+\.localhost)(:\d+)?(/.*)?$", re.I)
SECRET = re.compile(r"(ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{30,}|(password|passwd|api_key|token)\s*=\s*['\"][^'\"\s]{4,}['\"])", re.I)
SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".ipynb_checkpoints"}


def here(p):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), p)


def read(p):
    try:
        with open(here(p), encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return None


def load_json(p):
    t = read(p)
    if t is None:
        return None
    try:
        return json.loads(t)
    except ValueError:
        return None


def files(pattern):
    return [f for f in glob.glob(here(pattern), recursive=True) if os.path.isfile(f)]


def dig(obj, key):
    for k in key.split("."):
        if not isinstance(obj, dict) or k not in obj:
            return None
        obj = obj[k]
    return obj


def ports_local(p):
    t = read(p)
    if t is None:
        return False
    found = re.findall(r"^\s*-\s*['\"]?([^'\"\s#]+:\d+(?::\d+)?)['\"]?\s*$", t, re.M)
    mapped = [x for x in found if re.match(r"^[\w.\[\]:]*\d+:\d+$", x)]
    return bool(mapped) and all(x.startswith("127.0.0.1:") for x in mapped)


def scan_meta(d):
    m = load_json(d + "/scan-meta.json")
    if not isinstance(m, dict):
        return None
    return {"tool": str(m.get("tool", ""))[:40], "target": str(m.get("target", ""))[:300]}


def no_secrets():
    root = here(".")
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in SKIP_DIRS]
        for fn in fns:
            if fn.endswith((".png", ".jpg", ".duckdb", ".db", ".zip", ".pdf")) or fn in ("check.py", "secrets.py", ".env"):
                continue
            try:
                with open(os.path.join(dp, fn), encoding="utf-8", errors="ignore") as f:
                    if SECRET.search(f.read(200000)):
                        return False
            except OSError:
                pass
    return True


def run(c):
    k = c["type"]
    if k == "file":
        return os.path.isfile(here(c["path"]))
    if k == "glob":
        return len(files(c["pattern"])) >= c.get("min", 1)
    if k == "text":
        t = (read(c["path"]) or "").lower()
        return bool(t) and all(n.lower() in t for n in c["needles"])
    if k == "regex":
        t = read(c["path"])
        return t is not None and len(re.findall(c["pattern"], t, re.M | re.I)) >= c.get("min", 1)
    if k == "lines":
        t = read(c["path"]) or ""
        return len([x for x in t.splitlines() if x.strip()]) >= c["min"]
    if k == "json":
        v = dig(load_json(c["path"]), c["key"])
        if "eq" in c:
            return v == c["eq"]
        return v is not None
    if k == "ports":
        return ports_local(c["path"])
    if k == "scan":
        m = scan_meta(c["dir"])
        return bool(m) and m["tool"] == c["tool"] and bool(LOCAL.match(m["target"]))
    if k == "nosecret":
        return no_secrets()
    raise ValueError(k)


def metrics():
    out = {}
    for f in sorted(files("results/*.json"))[:20]:
        try:
            with open(f, encoding="utf-8") as h:
                d = json.load(h)
        except (OSError, ValueError):
            continue
        name = os.path.splitext(os.path.basename(f))[0]
        if isinstance(d, dict):
            for k, v in d.items():
                if isinstance(v, (int, float, bool)) or (isinstance(v, str) and len(v) < 200):
                    out[f"{name}.{k}"[:60]] = v
    return dict(list(out.items())[:40])


def main(argv):
    only = argv[argv.index("--milestone") + 1] if "--milestone" in argv else None
    strict = "--strict" in argv
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    result = {"darsi": 1, "track": SPEC["track"], "starter": SPEC["repo"], "at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "milestones": {}}
    failed = False
    for m in SPEC["milestones"]:
        if only and m["id"] != only:
            continue
        checks = []
        for i, c in enumerate(m["checks"], 1):
            try:
                ok = bool(run(c))
            except Exception:  # a broken file is a failed check, never a crash
                ok = False
            checks.append({"id": f"{m['id']}-{i}", "ok": ok, "en": c["en"], "ar": c["ar"]})
        ok = all(x["ok"] for x in checks)
        failed = failed or not ok
        result["milestones"][m["id"]] = {"ok": ok, "checks": checks}
        print(f"\n{m['id']}  {'PASS' if ok else 'not yet'}  {m['en']}")
        print(f"    {'ناجح' if ok else 'لم يكتمل بعد'}  {m['ar']}")
        for x in checks:
            mark = "[x]" if x["ok"] else "[ ]"
            print(f"  {mark} {x['en']}")
            print(f"      {x['ar']}")
    result["metrics"] = metrics()
    scans = [s for s in (scan_meta(d) for d in ("reports/before", "reports/after")) if s]
    result["scans"] = scans
    for s in scans:
        if not LOCAL.match(s["target"]):
            print(f"\n!! A scan targeted {s['target']}: only this computer (localhost) is allowed.")
            print("!! استهدف أحد الفحوص عنوانًا غير هذا الكمبيوتر: المسموح به هو localhost فقط.")
    with open(here("darsi-check.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print("\nWrote darsi-check.json: send it with your milestone on Darsi.")
    print("كُتب الملف darsi-check.json: أرسله مع مرحلتك على درسي.")
    return 1 if strict and failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
