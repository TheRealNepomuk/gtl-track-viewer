#!/usr/bin/env python3
"""Extract track layouts from a GT Legends install into compact JSON for the web viewer.

One layout = one .gdb file (that's what the game lists). Its geometry comes from
the .AIW file next to it (AI waypoints: road centre, width, pit lane, grid).
Only this derived line data is written; no meshes, textures or other mod files.

Usage:
  python3 -I tools/extract.py <GameData/Locations> <output dir>

Writes <out>/tracks/<id>.json per layout and <out>/index.json ({"generated", "layouts"}), and prints a
summary of layouts that could not be converted.
"""
import datetime
import json
import math
import os
import re
import sys

# some AIWs write ".9678" / "-.5" without the leading zero
NUM = r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?"
TODAY = datetime.date.today().isoformat()   # shown on the site as "data as of"
GDB_KEYS = {"trackname", "eventname", "venuename", "location", "length", "tracktype"}


def tup(s):
    return [float(x) for x in re.findall(NUM, s)]


def read_text(path):
    with open(path, "rb") as f:
        return f.read().decode("latin-1")


def parse_gdb(path):
    out = {}
    for line in read_text(path).splitlines():
        m = re.match(r"\s*([A-Za-z][\w ]*?)\s*=\s*(.*)$", line)
        if not m:
            continue
        key = m.group(1).replace(" ", "").lower()
        val = m.group(2).split("//")[0].strip().strip('"').strip()
        if key in GDB_KEYS and key not in out and val:
            out[key] = val
    return out


def parse_aiw(path):
    head, grid, wps = {}, [], []
    cur, section = None, None
    for raw in read_text(path).splitlines():
        line = raw.split("//")[0].strip()
        if not line:
            continue
        if line.startswith("["):
            section = line.strip("[]").upper()
            continue
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        k, v = k.strip().lower(), v.strip()
        if section == "GRID" and k == "pos":
            grid.append(tup(v))
        elif section == "WAYPOINT":
            if k == "wp_pos":
                cur = {"pos": tup(v)}
                wps.append(cur)
            elif cur is not None and k.startswith("wp_"):
                cur[k[3:]] = tup(v)
            elif cur is None:
                head[k] = v
    return head, grid, wps


def num(s, default=0.0):
    try:
        return float(re.findall(NUM, s or "")[0])
    except (IndexError, ValueError):
        return default


def convert(aiw_path):
    head, grid, wps = parse_aiw(aiw_path)
    r1 = lambda x: round(x, 1)
    rows = []
    for w in wps:
        bits = int(w.get("bitfields", [0])[0])
        if bits & 1:            # non-path waypoint (pit stall, garage): not part of a line
            continue
        p = w["pos"]
        if len(p) < 3:
            continue
        q = (w.get("perp") or [0, 0, 0]) + [0, 0, 0]
        wd = (w.get("width") or [5, 5, 5, 5]) + [5, 5, 5, 5]
        sc = (w.get("score") or [0, 0]) + [0, 0]
        rows.append([
            r1(p[0]), r1(p[1]), r1(p[2]),           # 0-2 position (x east, y up, z north)
            round(q[0], 3), round(q[2], 3),          # 3-4 sideways direction (x, z)
            r1(wd[0]), r1(wd[1]), r1(wd[2]), r1(wd[3]),  # 5-8 road L/R, outer L/R
            int(w.get("branchid", [0])[0]),          # 9 0 = main loop, 1+ = pit lane
            r1(sc[1]), int(sc[0]),                   # 10 distance into lap, 11 sector
        ])
    main = [r for r in rows if r[9] == 0]
    pits = [r for r in rows if r[9] != 0]
    if len(main) < 20:
        raise ValueError(f"only {len(main)} main-loop waypoints")
    lap = num(head.get("lap_length"))
    if lap <= 0:
        raise ValueError("no lap_length")

    # Order the main loop: normally by "distance into lap", but a few AIWs have
    # broken distances. Use whichever order has the smaller biggest step, and
    # rebuild the distances from the geometry if we fall back to file order.
    def max_step(seq):
        return max(math.dist((seq[i][0], seq[i][2]), (seq[i - 1][0], seq[i - 1][2])) for i in range(1, len(seq)))
    by_dist = sorted(main, key=lambda r: r[10])
    if max_step(by_dist) > max_step(main) * 1.5:
        cum = [0.0]
        for i in range(1, len(main)):
            cum.append(cum[-1] + math.dist(main[i][:3], main[i - 1][:3]))
        loop = cum[-1] + math.dist(main[0][:3], main[-1][:3])
        for r, c in zip(main, cum):
            r[10] = r1(c / loop * lap)
    else:
        main = by_dist

    data = {
        "lap_length": round(lap, 1),
        "sector_1": round(num(head.get("sector_1_length")), 1),
        "sector_2": round(num(head.get("sector_2_length")), 1),
        "grid": [[r1(c) for c in g[:3]] for g in grid if len(g) >= 3],
        "wp": main + pits,      # main loop first, in lap order, then pit lane(s)
    }
    return data, track_stats(main, pits, data)


def track_stats(main, pits, data):
    n = len(main)
    ys = [r[1] for r in main]

    def grad(i):            # gradient over the next ~100 m, in % (shorter windows pick up AIW bumps)
        j, d = i, 0.0
        while d < 100:
            k = (j + 1) % n
            d += math.dist((main[k][0], main[k][2]), (main[j][0], main[j][2]))
            j = k
            if j == i:
                break
        return (main[j][1] - main[i][1]) / d * 100 if d > 0 else 0.0
    grads = [grad(i) for i in range(n)]
    climb = sum(max(0.0, main[i][1] - main[i - 1][1]) for i in range(1, n))
    widths = [max(0.0, r[5]) + max(0.0, r[6]) for r in main]

    # small outline for list thumbnails: ~64 points, scaled to 0..100, north up
    step = max(1, n // 64)
    pts = main[::step]
    xs, zs = [p[0] for p in pts], [p[2] for p in pts]
    span = max(max(xs) - min(xs), max(zs) - min(zs)) or 1
    ox = (100 - (max(xs) - min(xs)) / span * 100) / 2
    oz = (100 - (max(zs) - min(zs)) / span * 100) / 2
    outline = []
    for p in pts:
        outline += [round(ox + (p[0] - min(xs)) / span * 100), round(oz + (max(zs) - p[2]) / span * 100)]

    return {
        "elev": round(max(ys) - min(ys), 1),
        "climb": round(climb),
        "up": round(max(grads), 1),
        "down": round(-min(grads), 1),
        "width": round(sum(widths) / n, 1),
        "grid": len(data["grid"]),
        "pit": bool(pits),
        "wps": n,
        "outline": outline,
    }


def slug(rel):
    return re.sub(r"[^a-z0-9]+", "-", rel.lower()).strip("-")


def main():
    src, out = sys.argv[1], sys.argv[2]
    os.makedirs(os.path.join(out, "tracks"), exist_ok=True)
    index, problems, used_aiw = [], [], set()
    gdbs = []
    for root, _, files in os.walk(src):
        for f in files:
            if f.lower().endswith(".gdb"):
                gdbs.append(os.path.join(root, f))
    for gdb in sorted(gdbs, key=str.lower):
        rel = os.path.relpath(gdb, src)
        folder = os.path.dirname(gdb)
        stem = os.path.splitext(os.path.basename(gdb))[0].lower()
        aiws = [f for f in os.listdir(folder) if f.lower().endswith(".aiw")]
        match = [f for f in aiws if os.path.splitext(f)[0].lower() == stem]
        if not match and len(aiws) == 1:
            match = aiws
        if not match:
            problems.append((rel, f"no matching AIW (found {len(aiws)})"))
            continue
        aiw = os.path.join(folder, match[0])
        used_aiw.add(aiw)
        try:
            data, stats = convert(aiw)
        except Exception as e:  # report and carry on with the next layout
            problems.append((rel, f"AIW: {e}"))
            continue
        meta = parse_gdb(gdb)
        tid = slug(os.path.splitext(rel)[0])
        data["id"] = tid
        data["meta"] = meta
        data["path"] = rel.replace(os.sep, "/")
        data["generated"] = TODAY
        with open(os.path.join(out, "tracks", tid + ".json"), "w") as f:
            json.dump(data, f, separators=(",", ":"))
        index.append({
            "id": tid,
            "name": meta.get("trackname") or meta.get("eventname") or stem,
            "venue": meta.get("venuename", ""),
            "location": meta.get("location", ""),
            "type": meta.get("tracktype", ""),
            "folder": rel.replace(os.sep, "/").split("/")[0],
            "km": round(data["lap_length"] / 1000, 3),
            **stats,
        })
    with open(os.path.join(out, "index.json"), "w") as f:
        json.dump({"generated": TODAY, "layouts": index}, f, separators=(",", ":"), ensure_ascii=False)

    orphans = []
    for root, _, files in os.walk(src):
        for f in files:
            p = os.path.join(root, f)
            if f.lower().endswith(".aiw") and p not in used_aiw:
                orphans.append(os.path.relpath(p, src))
    print(f"layouts (.gdb): {len(gdbs)}   converted: {len(index)}   problems: {len(problems)}")
    for rel, why in problems:
        print(f"  ! {rel}: {why}")
    print(f"AIW files not used by any layout: {len(orphans)}")
    for o in sorted(orphans, key=str.lower):
        print(f"  - {o}")


if __name__ == "__main__":
    main()
