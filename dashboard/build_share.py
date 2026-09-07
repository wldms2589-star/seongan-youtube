# -*- coding: utf-8 -*-
"""
공유본 빌드 — 대시보드를 GitHub Pages 로 올릴 정적 페이지로 굽는다.

원본 대시보드(claude.ai 아티팩트)는 저장 기능 때문에 조직 밖으로 공유되지 않는다.
그래서 지금 데이터를 페이지 안에 그대로 박아 넣은 읽기 전용 사본을 만든다.

    dashboard/board.html      원본 (여기서 편집)
    dashboard/snapshot/       아티팩트 db 에서 내려받은 데이터
        topics/*.json  series/*.json  custom/*.json  guide.json(선택)
    docs/index.html           결과물 (GitHub Pages 가 이 폴더를 본다)

사용법:
    python dashboard/build_share.py
    python dashboard/build_share.py --no-scripts     대본 본문을 빼고 굽는다
"""
import argparse
import json
import os
import sys
from datetime import date

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "dashboard", "board.html")
SNAP = os.path.join(ROOT, "dashboard", "snapshot")
OUT = os.path.join(ROOT, "docs", "index.html")
MARK = "const SNAPSHOT = null; /*__SNAPSHOT__*/"


def load_dir(name):
    d = os.path.join(SNAP, name)
    if not os.path.isdir(d):
        return []
    out = []
    for fn in sorted(os.listdir(d)):
        if fn.endswith(".json"):
            with open(os.path.join(d, fn), encoding="utf-8") as f:
                out.append(json.load(f))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-scripts", action="store_true",
                    help="대본 본문을 빼고 목록·일정만 공유한다")
    args = ap.parse_args()

    if not os.path.exists(SRC):
        print(f"[!] {SRC} 가 없습니다.", file=sys.stderr)
        sys.exit(1)

    topics = load_dir("topics")
    series = load_dir("series")
    custom = load_dir("custom")

    guide = ""
    gpath = os.path.join(SNAP, "guide.json")
    if os.path.exists(gpath):
        with open(gpath, encoding="utf-8") as f:
            guide = (json.load(f) or {}).get("text", "")

    if args.no_scripts:
        for t in topics:
            t["script"] = ""
            t["draft"] = ""

    # 원고(draft)는 공유본에 넣지 않는다 — 작업 중인 초안이라 밖에 나갈 이유가 없다
    for t in topics:
        t.pop("draft", None)

    snapshot = {
        "builtAt": date.today().isoformat(),
        "topics": topics,
        "series": series,
        "custom": custom,
        "guide": guide,
    }

    html = open(SRC, encoding="utf-8").read()
    if MARK not in html:
        print("[!] board.html 에서 스냅샷 자리를 찾지 못했습니다.", file=sys.stderr)
        sys.exit(1)

    payload = json.dumps(snapshot, ensure_ascii=False, separators=(",", ":"))
    # </script> 가 데이터 안에 있으면 스크립트가 조기 종료되므로 끊어준다
    payload = payload.replace("</script>", "<\\/script>")
    html = html.replace(MARK, "const SNAPSHOT = " + payload + ";")

    # 아티팩트가 감싸주던 부분을 정적 페이지에서는 직접 넣는다
    head = (
        "<!doctype html>\n<html lang=\"ko\">\n<head>\n"
        "<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        "<meta name=\"robots\" content=\"noindex, nofollow\">\n"
        "<style>html{color-scheme:light dark}body{margin:0}"
        "img{max-width:100%}[hidden]{display:none!important}</style>\n"
        "</head>\n<body>\n"
    )
    html = head + html + "\n</body>\n</html>\n"

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)

    with_script = sum(1 for t in topics if t.get("script"))
    size = len(html.encode("utf-8"))
    print(f"[완료] {OUT}")
    print(f"  주제 {len(topics)}건 (대본 {with_script}건) / 시리즈 {len(series)} / 직접 추가 {len(custom)}")
    print(f"  크기 {size:,} bytes")
    if args.no_scripts:
        print("  대본 본문은 빼고 구웠습니다.")
    print("\n올리려면:  git add docs && git commit -m \"공유본 갱신\" && git push")


if __name__ == "__main__":
    main()
