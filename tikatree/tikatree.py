#!/usr/bin/env python
import argparse
import json
from hashlib import md5, sha256
from pathlib import Path
from pprint import pprint

from tika import parser

from .DisplayablePath import DisplayablePath

BLOCK_SIZE = 65536


def saveMetadata(basepath, metadata):
    if Path(metadata).exists() is True:
        raise FileExistsError(f"{metadata} exists")
    print("Creating : ", metadata)
    for item in basepath.rglob("*"):
        if item.is_file():
            try:
                with open(metadata, "a", encoding="utf-8") as outfile:
                    try:
                        i = Path(item)
                        relatives = i.relative_to(basepath)
                        outfile.writelines(f"\n\n{relatives}\n")
                        p = Path.resolve(item)
                        parsed = parser.from_file(f"{p}")
                        pprint(parsed["metadata"], stream=outfile)
                        print(p)
                    except OSError as oserr:
                        print(f"{oserr}: Error parsing : {item.name}")
            except OSError as oserr:
                print(f"{oserr}: Error opening : {metadata}")


def saveDirectoryTree(basepath, directorytree):
    if Path(directorytree).exists() is True:
        raise FileExistsError(f"{directorytree} exists")
    print("Creating : ", directorytree)
    paths = DisplayablePath.make_tree(Path(basepath))
    for path in paths:
        with open(directorytree, "a", encoding="utf-8") as outfile:
            try:
                outfile.writelines(f"{path.displayable()}\n")
            except OSError as oserr:
                print(f"{oserr}: Error creating : {directorytree}")


def saveFileTree(basepath, filetree):
    if Path(filetree).exists() is True:
        raise FileExistsError(f"{filetree} exists")
    print("Creating : ", filetree)
    for item in basepath.rglob("*"):
        if item.is_file():
            try:
                # Get file info
                i = Path(item)
                relative = i.relative_to(basepath)
                parents = relative.parents[0]

                # Get file size, convert to Kb
                size = i.stat().st_size
                size = round(size / 1024, 2)

                # Get hashes of file contents
                sha = sha256()
                md = md5()
                with open(i, "rb") as f:
                    fb = f.read(BLOCK_SIZE)
                    while len(fb) > 0:
                        sha.update(fb)
                        md.update(fb)
                        fb = f.read(BLOCK_SIZE)

                # Create json data from file info
                file_info = {}
                file_data = {}
                directory = []
                base_directory = {}
                file_info["size"] = f"{size}Kb"
                file_info["md5"] = md.hexdigest()
                file_info["sha256"] = sha.hexdigest()
                file_data[f"{i.name}"] = file_info
                directory.append(file_data)

                # Write or append to filetree
                if Path(filetree).exists() is False:
                    # Create initial json data
                    base_directory[f"{parents}"] = directory
                    print(relative)
                    writeJson(base_directory, filetree)
                else:
                    with open(filetree, encoding="utf-8") as outfile:
                        try:
                            data = json.load(outfile)
                            try:
                                temp = data[f"{parents}"]
                                temp.append(file_data)
                            except KeyError:
                                # Create directory if it doesn't exist
                                data[f"{parents}"] = directory
                            print(relative)
                            writeJson(data, filetree)
                        except OSError as oserr:
                            print(f"{oserr}: Error reading : {outfile}")
            except OSError as oserr:
                print(f"{oserr}: Error parsing : {relative}")


def writeJson(data, file):
    try:
        with open(file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except OSError as oserr:
        print(f"{oserr}: Error appending : {file}")


def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="A directory tree metadata parser using Apache Tika, by default it runs -d, -m, -f in the current directory",
    )
    parser.add_argument(
        "-v", "--version", action="version", version=f"{parser.prog} version 0.0.3",
    )
    parser.add_argument("DIRECTORY", type=Path, default=".", help="directory to parse")
    parser.add_argument(
        "-d", "--directorytree", action="store_true", help="create directory tree"
    )
    parser.add_argument("-m", "--metadata", action="store_true", help="parse metadata")
    parser.add_argument(
        "-f", "--filetree", action="store_true", help="create file tree"
    )
    return parser


def main():
    """Run tikatree from command line"""

    parser = init_argparse()
    args = parser.parse_args()
    d = args.directorytree
    m = args.metadata
    f = args.filetree

    if Path(args.DIRECTORY).exists() is True:
        basepath = Path(args.DIRECTORY)
        metadata = f"{basepath.stem}_Metadata.txt"
        directorytree = f"{basepath.stem}_Directory_Tree.txt"
        filetree = f"{basepath.stem}_File_Tree.json"
    else:
        raise NotADirectoryError(f"{args.DIRECTORY} does not exist")

    if m is True:
        saveMetadata(basepath, metadata)
    elif d is True:
        saveDirectoryTree(basepath, directorytree)
    elif f is True:
        saveFileTree(basepath, filetree)
    else:
        saveMetadata(basepath, metadata)
        saveDirectoryTree(basepath, directorytree)
        saveFileTree(basepath, filetree)


if __name__ == "__main__":
    main()
