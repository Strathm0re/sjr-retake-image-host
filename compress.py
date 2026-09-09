#!/usr/bin/env python3
"""批量压缩 E:\sjr\重拍 -> E:\sjr\重拍_web (1280px, JPEG q85)"""
from PIL import Image
import os, sys, time, json

Image.MAX_IMAGE_PIXELS = None  # 合法超大拼接图

SRC = "/mnt/e/sjr/重拍"
DST = "/mnt/e/sjr/重拍_web"

def compress_one(src_path, dst_path, max_w=1280, quality=85):
    img = Image.open(src_path)
    w, h = img.size
    if w > max_w:
        nh = int(h * max_w / w)
        img = img.resize((max_w, nh), Image.LANCZOS)
    img.convert("RGB").save(dst_path, "JPEG", quality=quality, optimize=True)

def main():
    t0 = time.time()
    stats = {"done": 0, "skipped": 0, "error": 0, "bytes_src": 0, "bytes_dst": 0}
    jobs = []
    for root, dirs, files in os.walk(SRC):
        rel = os.path.relpath(root, SRC)
        for f in sorted(files):
            if f.lower().endswith(".jpg"):
                jobs.append((os.path.join(root, f), rel, f))
    total = len(jobs)
    print(f"total jobs: {total}", flush=True)
    for i, (src_path, rel, f) in enumerate(jobs, 1):
        dst_dir = os.path.join(DST, rel)
        os.makedirs(dst_dir, exist_ok=True)
        dst_path = os.path.join(dst_dir, f)
        # 增量: 已存在且比源新则跳过
        if os.path.exists(dst_path) and os.path.getmtime(dst_path) >= os.path.getmtime(src_path):
            stats["skipped"] += 1
        else:
            try:
                compress_one(src_path, dst_path)
                stats["done"] += 1
            except Exception as e:
                print(f"ERROR {rel}/{f}: {e}", flush=True)
                stats["error"] += 1
                continue
        stats["bytes_src"] += os.path.getsize(src_path)
        stats["bytes_dst"] += os.path.getsize(dst_path)
        if i % 20 == 0 or i == total:
            pct = i / total * 100
            el = time.time() - t0
            eta = el / i * (total - i)
            print(f"[{i}/{total}] {pct:.0f}% done={stats['done']} skip={stats['skipped']} err={stats['error']} "
                  f"src={stats['bytes_src']/1e6:.0f}MB dst={stats['bytes_dst']/1e6:.1f}MB eta={eta:.0f}s", flush=True)
    print(json.dumps(stats), flush=True)
    print(f"ALL_DONE in {time.time()-t0:.0f}s", flush=True)

if __name__ == "__main__":
    main()
