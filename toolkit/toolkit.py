"""Claude Agent Toolkit - CLI interface for autonomous capabilities.

Usage:
    python toolkit.py vision screenshot [--region x,y,w,h] [--save PATH]
    python toolkit.py vision ocr IMAGE_PATH
    python toolkit.py vision see

    python toolkit.py gui click X Y
    python toolkit.py gui type "text"
    python toolkit.py gui press KEY
    python toolkit.py gui hotkey KEY1 KEY2 ...
    python toolkit.py gui pos
    python toolkit.py gui screen
    python toolkit.py gui windows
    python toolkit.py gui focus "window title"
    python toolkit.py gui open "app path"

    python toolkit.py web search "query"
    python toolkit.py web fetch URL
    python toolkit.py web scrape URL [--selector CSS]
    python toolkit.py web js URL

    python toolkit.py sys info
    python toolkit.py sys procs [--filter NAME]
    python toolkit.py sys ls [PATH]
    python toolkit.py sys read FILE
    python toolkit.py sys find DIR PATTERN
    python toolkit.py sys run "command"
    python toolkit.py sys clipboard

    python toolkit.py kb save CATEGORY TITLE CONTENT [--source SRC] [--tags t1,t2]
    python toolkit.py kb search QUERY [--category CAT]
    python toolkit.py kb categories
    python toolkit.py kb mem-set KEY VALUE
    python toolkit.py kb mem-get KEY
    python toolkit.py kb mem-list
"""

import sys
import json
import argparse


def cmd_vision(args):
    from modules import vision

    if args.action == "screenshot":
        region = tuple(map(int, args.region.split(","))) if args.region else None
        img, err = vision.screenshot(region=region, save_path=args.save)
        if err:
            print(f"ERROR: {err}")
        else:
            path = args.save or "screenshot.png"
            if not args.save:
                img.save(path)
            print(f"Saved to {path}")

    elif args.action == "ocr":
        text, err = vision.ocr_image(args.image)
        if err:
            print(f"ERROR: {err}")
        else:
            print(text)

    elif args.action == "see":
        text, err = vision.see_screen()
        if err:
            print(f"ERROR: {err}")
        else:
            print(text)


def cmd_gui(args):
    from modules import gui

    if args.action == "click":
        ok, err = gui.click(int(args.x), int(args.y))
        print("OK" if ok else f"ERROR: {err}")

    elif args.action == "type":
        ok, err = gui.type_text(args.text)
        print("OK" if ok else f"ERROR: {err}")

    elif args.action == "press":
        ok, err = gui.press(args.key)
        print("OK" if ok else f"ERROR: {err}")

    elif args.action == "hotkey":
        ok, err = gui.hotkey(*args.keys)
        print("OK" if ok else f"ERROR: {err}")

    elif args.action == "pos":
        pos, err = gui.get_mouse_pos()
        print(pos if pos else f"ERROR: {err}")

    elif args.action == "screen":
        size, err = gui.get_screen_size()
        print(size if size else f"ERROR: {err}")

    elif args.action == "windows":
        out, err = gui.list_windows()
        print(out if out else f"ERROR: {err}")

    elif args.action == "focus":
        out, err = gui.focus_window(args.title)
        print(out if out else f"ERROR: {err}")

    elif args.action == "open":
        ok, err = gui.open_app(args.path)
        print("OK" if ok else f"ERROR: {err}")


def cmd_web(args):
    from modules import web

    if args.action == "search":
        results, err = web.search_ddg(args.query, num_results=args.num or 5)
        if err:
            print(f"ERROR: {err}")
        else:
            for i, r in enumerate(results, 1):
                print(f"\n[{i}] {r['title']}")
                print(f"    {r['url']}")
                print(f"    {r['snippet']}")

    elif args.action == "fetch":
        text, err = web.fetch(args.url)
        if err:
            print(f"ERROR: {err}")
        else:
            print(text[:5000])

    elif args.action == "scrape":
        text, err = web.scrape_text(args.url, selector=args.selector)
        if err:
            print(f"ERROR: {err}")
        else:
            print(text)

    elif args.action == "js":
        text, err = web.fetch_js_page(args.url)
        if err:
            print(f"ERROR: {err}")
        else:
            print(text[:5000])


def cmd_sys(args):
    from modules import system

    if args.action == "info":
        info, err = system.system_info()
        print(json.dumps(info, indent=2, ensure_ascii=False) if info else f"ERROR: {err}")

    elif args.action == "procs":
        procs, err = system.list_processes(filter_name=args.filter)
        if err:
            print(f"ERROR: {err}")
        else:
            for p in (procs or [])[:30]:
                print(f"  PID {p['Id']:>6}  {p['ProcessName']}")

    elif args.action == "ls":
        entries, err = system.list_dir(args.path or ".")
        if err:
            print(f"ERROR: {err}")
        else:
            for e in (entries or []):
                size = f"{e['size']:>10}" if e["type"] == "file" else "     <DIR>"
                print(f"  {size}  {e['name']}")

    elif args.action == "read":
        text, err = system.read_file(args.file)
        print(text if text else f"ERROR: {err}")

    elif args.action == "find":
        results, err = system.search_files(args.dir, args.pattern)
        if err:
            print(f"ERROR: {err}")
        else:
            for r in (results or []):
                print(f"  {r}")

    elif args.action == "run":
        out, err = system.run_command(args.command)
        if err:
            print(f"ERROR: {err}")
        else:
            if out["stdout"]:
                print(out["stdout"])
            if out["stderr"]:
                print(f"STDERR: {out['stderr']}", file=sys.stderr)

    elif args.action == "clipboard":
        text, err = system.clipboard_get()
        print(text if text else f"ERROR: {err}")


def cmd_kb(args):
    from modules import knowledge

    if args.action == "save":
        tags = args.tags.split(",") if args.tags else None
        ok, err = knowledge.save(args.category, args.title, args.content, source=args.source, tags=tags)
        print("Saved." if ok else f"ERROR: {err}")

    elif args.action == "search":
        results, err = knowledge.search(args.query, category=args.category)
        if err:
            print(f"ERROR: {err}")
        else:
            for r in results:
                print(f"\n[{r['category']}] {r['title']}")
                print(f"  {r['content'][:200]}")

    elif args.action == "categories":
        cats, err = knowledge.list_categories()
        if err:
            print(f"ERROR: {err}")
        else:
            for c in cats:
                print(f"  {c['category']}: {c['count']} entries")

    elif args.action == "mem-set":
        ok, err = knowledge.memory_set(args.key, args.value)
        print("OK" if ok else f"ERROR: {err}")

    elif args.action == "mem-get":
        val, err = knowledge.memory_get(args.key)
        print(val if val else f"Not found. {err or ''}")

    elif args.action == "mem-list":
        mems, err = knowledge.memory_list()
        if err:
            print(f"ERROR: {err}")
        else:
            for m in mems:
                print(f"  {m['key']}: {m['value'][:100]}")


def main():
    parser = argparse.ArgumentParser(description="Claude Agent Toolkit")
    sub = parser.add_subparsers(dest="module")

    # Vision
    p_vision = sub.add_parser("vision")
    sp = p_vision.add_subparsers(dest="action")
    p = sp.add_parser("screenshot")
    p.add_argument("--region", help="x,y,w,h")
    p.add_argument("--save", help="Save path")
    p = sp.add_parser("ocr")
    p.add_argument("image")
    sp.add_parser("see")

    # GUI
    p_gui = sub.add_parser("gui")
    sp = p_gui.add_subparsers(dest="action")
    p = sp.add_parser("click")
    p.add_argument("x")
    p.add_argument("y")
    p = sp.add_parser("type")
    p.add_argument("text")
    p = sp.add_parser("press")
    p.add_argument("key")
    p = sp.add_parser("hotkey")
    p.add_argument("keys", nargs="+")
    sp.add_parser("pos")
    sp.add_parser("screen")
    sp.add_parser("windows")
    p = sp.add_parser("focus")
    p.add_argument("title")
    p = sp.add_parser("open")
    p.add_argument("path")

    # Web
    p_web = sub.add_parser("web")
    sp = p_web.add_subparsers(dest="action")
    p = sp.add_parser("search")
    p.add_argument("query")
    p.add_argument("--num", type=int, default=5)
    p = sp.add_parser("fetch")
    p.add_argument("url")
    p = sp.add_parser("scrape")
    p.add_argument("url")
    p.add_argument("--selector")
    p = sp.add_parser("js")
    p.add_argument("url")

    # System
    p_sys = sub.add_parser("sys")
    sp = p_sys.add_subparsers(dest="action")
    sp.add_parser("info")
    p = sp.add_parser("procs")
    p.add_argument("--filter")
    p = sp.add_parser("ls")
    p.add_argument("path", nargs="?", default=".")
    p = sp.add_parser("read")
    p.add_argument("file")
    p = sp.add_parser("find")
    p.add_argument("dir")
    p.add_argument("pattern")
    p = sp.add_parser("run")
    p.add_argument("command")
    sp.add_parser("clipboard")

    # Knowledge
    p_kb = sub.add_parser("kb")
    sp = p_kb.add_subparsers(dest="action")
    p = sp.add_parser("save")
    p.add_argument("category")
    p.add_argument("title")
    p.add_argument("content")
    p.add_argument("--source")
    p.add_argument("--tags")
    p = sp.add_parser("search")
    p.add_argument("query")
    p.add_argument("--category")
    sp.add_parser("categories")
    p = sp.add_parser("mem-set")
    p.add_argument("key")
    p.add_argument("value")
    p = sp.add_parser("mem-get")
    p.add_argument("key")
    sp.add_parser("mem-list")

    args = parser.parse_args()

    dispatch = {
        "vision": cmd_vision,
        "gui": cmd_gui,
        "web": cmd_web,
        "sys": cmd_sys,
        "kb": cmd_kb,
    }

    if args.module in dispatch:
        dispatch[args.module](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
