#!/usr/bin/env python3
"""东风日历命令行：读写仓库根的 events.json，并 git commit/push 到 GitHub Pages。

子命令:
  add           --title T --start "YYYY-MM-DD HH:MM" [--end "YYYY-MM-DD HH:MM"] [--person P] [--place L] [--note N]
                [--status pending|confirmed|rescheduled] [--remind 30,15] [--no-push]
                (--start 只写日期则为全天事件。不带子命令、直接以 --title 开头也可以)
  list          [--date YYYY-MM-DD] [--all]     列出事件（默认仅今天及以后）
  delete        --id ID [--no-push]
  due           [--now "YYYY-MM-DD HH:MM"] [--no-pull]   输出开始时间在未来 25–35 分钟内且未提醒过的事件(JSON 数组)
  mark-reminded --id ID [--no-push]              写入 remindedAt 并 push

仓库位置: 默认是本脚本所在目录的上一级；可用环境变量 DFC_REPO 覆盖。所有时间按 UTC+8。
目录里没有 .git 时(例如本地测试副本)只改文件，不做 git 操作。
"""
import argparse, json, os, random, string, subprocess, sys, time
from datetime import datetime, timedelta, timezone

TZ = timezone(timedelta(hours=8))
REPO = os.environ.get("DFC_REPO") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EV = os.path.join(REPO, "events.json")


def now_dt():
    return datetime.now(TZ)


def parse_dt(s):
    s = s.strip().replace("T", " ")
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(s, fmt).replace(tzinfo=TZ), True
        except ValueError:
            pass
    try:
        return datetime.strptime(s, "%Y-%m-%d").replace(tzinfo=TZ), False
    except ValueError:
        sys.exit('时间格式应为 "YYYY-MM-DD HH:MM"（或仅日期 YYYY-MM-DD）：' + s)


def iso(d):
    return d.strftime("%Y-%m-%dT%H:%M:%S+08:00")


def is_git():
    return os.path.isdir(os.path.join(REPO, ".git"))


def git(*a, check=True):
    r = subprocess.run(["git", "-C", REPO, *a], capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError("git %s 失败: %s" % (" ".join(a), (r.stderr or r.stdout).strip()))
    return r


def pull():
    if is_git():
        git("pull", "--rebase", "--autostash", "-q")


def load():
    try:
        with open(EV, encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except FileNotFoundError:
        return []


def save(events):
    tmp = EV + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, EV)


def commit_push(msg, push=True):
    if not is_git():
        print("(无 .git，已跳过 commit/push)", file=sys.stderr)
        return
    git("add", "events.json")
    if git("diff", "--cached", "--quiet", "--", "events.json", check=False).returncode == 0:
        return
    git("commit", "-q", "-m", msg, "--", "events.json")
    if not push:
        return
    for i in range(3):
        r = git("push", "-q", "origin", "HEAD:main", check=False)
        if r.returncode == 0:
            return
        git("pull", "--rebase", "--autostash", "-q")  # 远端有新提交：先 rebase 再重试
    raise RuntimeError("git push 失败: " + (r.stderr or r.stdout).strip())


def mutate(fn, msg, push=True):
    """pull --rebase → 读 → 改 → 写 → commit/push"""
    pull()
    events = load()
    out = fn(events)
    save(events)
    commit_push(msg, push)
    return out


def new_id():
    return "a" + format(int(time.time() * 1000), "x") + "".join(random.choices(string.ascii_lowercase + string.digits, k=3))


def cmd_add(a):
    start, timed = parse_dt(a.start)
    if a.end:
        end, _ = parse_dt(a.end)
        if end < start:
            sys.exit("--end 早于 --start")
    else:
        end = start + timedelta(minutes=60) if timed else start
    dur = int((end - start).total_seconds() // 60) if timed else 0
    reminders = [int(x) for x in a.remind.split(",") if x.strip()] if a.remind else [30]
    ev = {
        "id": new_id(), "source": "agent", "kind": "event", "title": a.title,
        "who": a.person or "", "where": a.place or "",
        "date": start.strftime("%Y-%m-%d"), "time": start.strftime("%H:%M") if timed else "",
        "dur": dur, "start": iso(start), "end": iso(end),
        "repeat": "none", "until": "", "status": a.status, "notes": a.note or "",
        "reminders": reminders, "createdAt": int(time.time() * 1000),
    }
    mutate(lambda evs: evs.append(ev), "add event: %s (%s)" % (a.title, ev["date"] + (" " + ev["time"] if ev["time"] else "")), not a.no_push)
    print(json.dumps(ev, ensure_ascii=False))


def start_of(ev):
    if ev.get("start"):
        try:
            return datetime.fromisoformat(ev["start"]).astimezone(TZ)
        except ValueError:
            pass
    if ev.get("date") and ev.get("time"):
        return datetime.strptime(ev["date"] + " " + ev["time"], "%Y-%m-%d %H:%M").replace(tzinfo=TZ)
    return None


def cmd_list(a):
    evs = load()
    today = now_dt().strftime("%Y-%m-%d")
    for ev in sorted(evs, key=lambda e: (e.get("date", ""), e.get("time", ""))):
        if a.date and ev.get("date") != a.date:
            continue
        if not a.date and not a.all and ev.get("date", "") < today:
            continue
        print("%s  %s %s  %s%s%s%s" % (ev.get("id"), ev.get("date"), ev.get("time") or "全天", ev.get("title"),
              ("  👤" + ev["who"]) if ev.get("who") else "", ("  📍" + ev["where"]) if ev.get("where") else "",
              "  [已提醒]" if ev.get("remindedAt") else ""))
    if not evs:
        print("(没有事件)")


def cmd_delete(a):
    def fn(evs):
        n = len(evs)
        evs[:] = [e for e in evs if e.get("id") != a.id]
        if len(evs) == n:
            sys.exit("找不到 id: " + a.id)
    mutate(fn, "delete event " + a.id, not a.no_push)
    print("已删除 " + a.id)


def cmd_due(a):
    if not a.no_pull:
        try:
            pull()
        except Exception as e:  # 拉取失败不影响用本地数据判断
            print("警告: " + str(e), file=sys.stderr)
    now = parse_dt(a.now)[0] if a.now else now_dt()
    lo, hi = now + timedelta(minutes=25), now + timedelta(minutes=35)
    out = []
    for ev in load():
        if ev.get("remindedAt") or ev.get("kind", "event") != "event":
            continue
        s = start_of(ev)
        if s and lo <= s <= hi:
            out.append(ev)
    print(json.dumps(out, ensure_ascii=False, indent=2))


def cmd_mark(a):
    stamp = iso(now_dt())

    def fn(evs):
        for e in evs:
            if e.get("id") == a.id:
                e["remindedAt"] = stamp
                return
        sys.exit("找不到 id: " + a.id)
    mutate(fn, "mark reminded " + a.id, not a.no_push)
    print("remindedAt=" + stamp)


def main():
    argv = sys.argv[1:]
    if argv and argv[0].startswith("--") and argv[0] not in ("-h", "--help"):
        argv = ["add"] + argv
    p = argparse.ArgumentParser(description="东风日历命令行", formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    sp = p.add_subparsers(dest="cmd", required=True)
    s = sp.add_parser("add"); s.set_defaults(f=cmd_add)
    s.add_argument("--title", required=True); s.add_argument("--start", required=True); s.add_argument("--end")
    s.add_argument("--person"); s.add_argument("--place"); s.add_argument("--note")
    s.add_argument("--status", default="confirmed", choices=["pending", "confirmed", "rescheduled"])
    s.add_argument("--remind", help="网页内提醒的提前分钟数，逗号分隔，默认 30")
    s.add_argument("--no-push", action="store_true")
    s = sp.add_parser("list"); s.set_defaults(f=cmd_list); s.add_argument("--date"); s.add_argument("--all", action="store_true")
    s = sp.add_parser("delete"); s.set_defaults(f=cmd_delete); s.add_argument("--id", required=True); s.add_argument("--no-push", action="store_true")
    s = sp.add_parser("due"); s.set_defaults(f=cmd_due); s.add_argument("--now"); s.add_argument("--no-pull", action="store_true")
    s = sp.add_parser("mark-reminded"); s.set_defaults(f=cmd_mark); s.add_argument("--id", required=True); s.add_argument("--no-push", action="store_true")
    a = p.parse_args(argv)
    try:
        a.f(a)
    except RuntimeError as e:
        sys.exit("错误: " + str(e))


if __name__ == "__main__":
    main()
