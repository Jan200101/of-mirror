from pathlib import Path
import urllib.request
import json
import hashlib
import sys
import os.path

def mkdir(path: Path):
    if not path.is_dir():
        try:
            path.mkdir()
        except FileExistsError:
            print(f"\"{path}\" already exists and is not a directory")
            exit(1)

def urlopen(*args, **kwargs):
    try:
        return urllib.request.urlopen(*args, **kwargs)
    except urllib.error.URLError as e:
        print(e.reason)
        exit(1)

def main():
    if len(sys.argv) < 3:
        print(f"{os.path.basename(sys.argv[0])} [output dir] [url]")
        return

    output_dir = Path(sys.argv[1]).expanduser()
    mkdir(output_dir)

    revisions_dir = output_dir / "revisions"
    mkdir(revisions_dir)

    objects_dir = output_dir / "objects"
    mkdir(objects_dir)

    url = sys.argv[2]
    revisions_url = f"{url}/revisions"
    objects_url = f"{url}/objects"

    latest_rev = int(urlopen(f"{revisions_url}/latest").read())
    if (latest_rev < 1):
        print(f"Latest revision({latest_rev}) is invalid")
        exit(1)

    latest_rev_file = (revisions_dir / "latest")
    if latest_rev_file.is_file() and (int(latest_rev_file.read_text()) < latest_rev):
        print("Local mirror is newer than remote")
        exit(1)

    latest_rev_file.write_text(str(latest_rev))

    for r in range(1, latest_rev+1):
        raw_data = urlopen(f"{revisions_url}/{r}").read()
        data = json.loads(raw_data)
        (revisions_dir / str(r)).write_text(raw_data)

        for o in data:
            # other types are unimportant right now
            if o["type"] == 0:
                if not o["object"]:
                    print(f"Missing object for {p['path']}")
                    continue

                object_file = objects_dir / o["object"]
                if object_file.is_file():
                    object_hash = object_file.read_bytes()
                    if object_hash != o["hash"]:
                        raw_object = urlopen(f"{objects_url}/{o['hash']}").read()
                        object_file.write_bytes(raw_object)
                else:
                    raw_object = urlopen(f"{objects_url}/{o['hash']}").read()
                    object_file.write_bytes(raw_object)

if __name__ == "__main__":
    main()