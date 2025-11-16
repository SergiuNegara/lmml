from pathlib import Path
import csv, re, shutil, collections

SRC = Path("data_cls")              # your extracted Roboflow export
DST = Path("data_cls_folders")      # YOLOv8-cls expected layout

def cid_from_name(name: str) -> int:
    m = re.match(r"^[^_]+_(\d+)_", name)
    if not m:
        raise ValueError(f"Cannot extract class id from '{name}'")
    return int(m.group(1))

def read_csv_rows(csv_path: Path):
    if not csv_path.exists():
        return []
    with csv_path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def infer_id_to_name():
    """
    Infer mapping 0/1/2 -> cola/fanta/sprite by majority vote on single-label rows.
    Falls back to {0:'cola',1:'sprite',2:'fanta'} if needed.
    """
    votes = {0: collections.Counter(), 1: collections.Counter(), 2: collections.Counter()}
    class_order = None

    for split in ("train", "valid", "test"):
        rows = read_csv_rows(SRC / split / "_classes.csv")
        if not rows:
            continue
        # header tells us the column order after 'filename'
        if class_order is None:
            fieldnames = list(rows[0].keys())
            class_order = [c for c in fieldnames if c != "filename"]
        for r in rows:
            fname = r["filename"]
            cid = cid_from_name(fname)
            # count only truly single-label rows
            labels = [int(r[c]) for c in class_order]
            if sum(labels) == 1:
                idx = labels.index(1)
                votes[cid][class_order[idx]] += 1

    # default mapping if we couldn't infer from CSVs
    default_map = {0: "cola", 1: "sprite", 2: "fanta"}

    id2name = {}
    for cid in (0, 1, 2):
        if votes[cid]:
            id2name[cid] = votes[cid].most_common(1)[0][0]
        else:
            id2name[cid] = default_map[cid]
    return id2name

def repack():
    id2name = infer_id_to_name()
    print(f"[INFO] Using id→name mapping: {id2name}")

    for split in ("train", "valid", "test"):
        src_split = SRC / split
        if not src_split.exists():
            print(f"[skip] {split}: not found")
            continue
        # make class folders
        for name in sorted(set(id2name.values())):
            (DST / split / name).mkdir(parents=True, exist_ok=True)

        moved = 0
        for img in src_split.glob("*.jpg"):
            cid = cid_from_name(img.name)
            cls = id2name.get(cid, f"class_{cid}")
            shutil.copy2(img, DST / split / cls / img.name)
            moved += 1
        print(f"[OK] {split}: copied {moved} images")

    print(f"\nDone → YOLOv8-cls dataset at: {DST.resolve()}")

if __name__ == "__main__":
    repack()