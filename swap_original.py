#!/usr/bin/env python3
"""替换仓库图片为原图: 删压缩版 -> 复制原图 -> git commit (不push, push单独跑)"""
import os, shutil, subprocess, sys

REPO = "/mnt/e/sjr/img-repo"
SRC = "/mnt/e/sjr/重拍"

# 1. 删除仓库中现有 jpg (保留 .git, compress.py, compress.log)
removed = 0
for root, dirs, files in os.walk(REPO):
    if ".git" in root:
        continue
    for f in files:
        if f.lower().endswith(".jpg"):
            os.remove(os.path.join(root, f))
            removed += 1
# 清掉空目录(1/2/3)
for b in ["1", "2", "3"]:
    p = os.path.join(REPO, b)
    if os.path.isdir(p):
        shutil.rmtree(p)
print(f"removed {removed} jpg + old dirs", flush=True)

# 2. 复制原图
copied = 0
for b in ["1", "2", "3"]:
    src_b = os.path.join(SRC, b)
    dst_b = os.path.join(REPO, b)
    shutil.copytree(src_b, dst_b)
    for root, dirs, files in os.walk(dst_b):
        for f in files:
            if f.lower().endswith(".jpg"):
                copied += 1
print(f"copied {copied} jpg", flush=True)

# 3. 统计
total = 0
size = 0
for root, dirs, files in os.walk(REPO):
    if ".git" in root:
        continue
    for f in files:
        if f.lower().endswith(".jpg"):
            total += 1
            size += os.path.getsize(os.path.join(root, f))
print(f"repo now: {total} jpg, {size/1e6:.0f} MB", flush=True)

# 4. git add + commit
r = subprocess.run(["git", "add", "-A"], cwd=REPO, capture_output=True, text=True)
if r.returncode != 0:
    print("git add FAIL:", r.stderr[:500]); sys.exit(1)
r = subprocess.run(["git", "commit", "-q", "-m",
                    "replace with original full-resolution images (292 files, 466MB)"],
                   cwd=REPO, capture_output=True, text=True)
if r.returncode != 0:
    print("git commit FAIL:", r.stderr[:500]); sys.exit(1)
print("COMMIT_OK", flush=True)
