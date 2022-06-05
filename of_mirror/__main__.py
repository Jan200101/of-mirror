from pathlib import Path
import urllib.request
import json
import hashlib
import sys
import os.path
import os

objects = set()

def mkdir(path: Path):
    if not path.is_dir():
        try:
            path.mkdir()
        except FileExistsError:
            print(f"\"{path}\" already exists and is not a directory")
            exit(1)

def cprint(*args, **kwargs):
    try:
        print("\r" + " " * (os.get_terminal_size().columns), end="")
    except OSError:
        pass
    return print(*args, **kwargs)

def urlopen(url, *args, **kwargs):
    try:
        req = urllib.request.Request(
            url, *args, **kwargs,
            headers={
                'User-Agent': 'Mozilla/5.0'
            }
        )
        retries = 0
        while (retries < 10):
            try:
                return urllib.request.urlopen(req, timeout=10).read()
            except (TimeoutError, ConnectionResetError):
                retries += 1
                continue

        print(f"Tried downloading {url} 10 times")
    except urllib.error.URLError as e:
        print(f"{url} {e.reason}")

    return None

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

    (output_dir / "reithreads").write_text("1")

    rei_version = urlopen(f"{url}/reiversion")
    if not rei_version:
        print(f"Could not fetch reiversion")
        exit(1)
    (output_dir / "reiversion").write_bytes(rei_version)    

    latest_rev = urlopen(f"{revisions_url}/latest")
    if not latest_rev:
        exit(1)
    
    latest_rev = int(latest_rev)
    if latest_rev < 1:
        print(f"Latest revision({latest_rev}) is invalid")
        exit(1)

    latest_rev_file = (revisions_dir / "latest")
    if latest_rev_file.is_file() and (int(latest_rev_file.read_text()) > latest_rev):
        print("Local mirror is newer than remote")
        exit(1)

    latest_rev_file.write_text(str(latest_rev))

    for r in range(latest_rev+1):
        print(f"Downloading Revision {r}", end="\r")

        raw_data = urlopen(f"{revisions_url}/{r}")
        if not raw_data:
            continue

        data = json.loads(raw_data)
        (revisions_dir / str(r)).write_bytes(raw_data)

        if not data:
            continue

        s = len(data)
        for i, o in enumerate(data):

            prefix = f"\r[{r}][{i+1}/{s}]{o['object']}:"

            if o["type"] == 0:
                if not o["object"]:
                    print(f"Missing object for {p['path']}")
                    continue

                objects.add(o["object"])

                cprint(f"{prefix} checking", end="")

                object_file = objects_dir / o["object"]
                if object_file.is_file():
                    object_hash = hashlib.md5(object_file.read_bytes()).hexdigest()
                    if object_hash == o["hash"]:
                        cprint(f"{prefix} done", end="")
                        continue

                cprint(f"{prefix} downloading", end="")
                raw_object = urlopen(f"{objects_url}/{o['object']}")
                if not raw_object:
                    continue
                cprint(f"{prefix} writing", end="")
                object_file.write_bytes(raw_object)
                cprint(f"{prefix} done", end="")
            else:
                cprint(f"{prefix} done", end="")

    unused = []
    for f in os.listdir(objects_dir):
        if f not in objects:
            unused.append(f)

    print("\n\nThe follow objects are unused:\n" + ", ".join(unused))


if __name__ == "__main__":
    main()
