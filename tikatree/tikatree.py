#!/usr/bin/env python
import json
from argparse import ArgumentParser
from datetime import datetime
from hashlib import md5, sha256
from pathlib import Path
from zlib import crc32

from tika import parser

from .DisplayablePath import DisplayablePath

BLOCK_SIZE = 65536
VERSION = "0.0.6"


def createMetadata(basepath, file):
    parents = basepath.parents[0]
    file = parents.joinpath(file)
    if Path(file).exists() is True:
        raise FileExistsError(f"{file} exists")
    print("Creating : ", file)
    for item in basepath.rglob("*"):
        if item.is_file():
            try:
                # Get file info
                i = Path(item)
                p = Path.resolve(item)
                parsed = parser.from_file(f"{p}")

                # Create json data from file info
                file_data = {}
                file_data[f"{i.name}"] = parsed["metadata"]
                createJson(basepath, file, item, file_data)
            except OSError as oserr:
                print(f"{oserr}: Error parsing : {i.name}")


def createDirectoryTree(basepath, file):
    parents = basepath.parents[0]
    file = parents.joinpath(file)
    if Path(file).exists() is True:
        raise FileExistsError(f"{file} exists")
    print("Creating : ", file)
    paths = DisplayablePath.make_tree(Path(basepath))
    dirtree_list = []
    for path in paths:
        dirtree_list.append(f"{path.displayable()}\n")
    with open(file, "a", encoding="utf-8") as outfile:
        try:
            outfile.writelines(dirtree_list)
        except OSError as oserr:
            print(f"{oserr}: Error creating : {file}")


def createFileTree(basepath, file):
    parents = basepath.parents[0]
    file = parents.joinpath(file)
    if Path(file).exists() is True:
        raise FileExistsError(f"{file} exists")
    print("Creating : ", file)
    for item in basepath.rglob("*"):
        if item.is_file():
            try:
                # Get file info
                i = Path(item)
                filename = i.name
                # Get file size, convert to KB
                size = i.stat().st_size
                size = round(size / 1024, 2)
                # Get modification time (creation time can vary by OS)
                mod_time = datetime.fromtimestamp(i.stat().st_mtime)
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
                file_info["modified"] = f"{mod_time}"
                file_info["size"] = f"{size}KB"
                file_info["md5"] = md.hexdigest()
                file_info["sha256"] = sha.hexdigest()
                file_data[f"{filename}"] = file_info
                createJson(basepath, file, item, file_data)
            except OSError as oserr:
                print(f"{oserr}: Error parsing : {filename}")


def createJson(basepath, jsonfile, item, file_data):
    i = Path(item)
    relative = i.relative_to(basepath)
    parents = relative.parents[0]
    directory = []
    base_directory = {}
    directory.append(file_data)

    # Write or append to json file
    if Path(jsonfile).exists() is False:
        # Create initial json data
        base_directory[f"{parents}"] = directory
        writeJson(base_directory, jsonfile)
        print(relative)
    else:
        with open(jsonfile, encoding="utf-8") as outfile:
            try:
                data = json.load(outfile)
                try:
                    temp = data[f"{parents}"]
                    temp.append(file_data)
                except KeyError:
                    # Create directory if it doesn't exist
                    data[f"{parents}"] = directory
                print(relative)
                writeJson(data, jsonfile)
            except OSError as oserr:
                print(f"{oserr}: Error reading : {outfile}")


def writeJson(data, jsonfile):
    try:
        with open(jsonfile, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except OSError as oserr:
        print(f"{oserr}: Error appending : {jsonfile}")


def createSfv(basepath, file):
    parents = basepath.parents[0]
    file = parents.joinpath(file)
    if Path(file).exists() is True:
        raise FileExistsError(f"{file} exists")
    print("Creating : ", file)
    sfvdict = {}
    for item in basepath.rglob("*"):
        if item.is_file():
            try:
                # Get file info
                i = Path(item)
                relative = i.relative_to(parents)
                crc = 0
                with open(i, "rb") as f:
                    fb = f.read(BLOCK_SIZE)
                    while len(fb) > 0:
                        crc = crc32(fb, crc)
                        fb = f.read(BLOCK_SIZE)
                crc = format(crc & 0xFFFFFFFF, "08x")
                sfvdict[f"{relative}"] = f"{crc}"
                print(f"{relative} {crc}\n")
            except OSError as oserr:
                print(f"{oserr}: Error creating checksums for : {file}")
        try:
            with open(f"{file}", "a", encoding="utf-8") as f:
                for k, v in sfvdict.items():
                    f.writelines(f"{relative} {crc}\n")
        except OSError as oserr:
            print(f"{oserr}: Error writing : {file}")


def initArgparse() -> ArgumentParser:
    parser = ArgumentParser(
        description="A directory tree metadata parser using Apache Tika, by default it runs arguments: -d, -f, -m, -s",
    )
    parser.add_argument(
        "-v", "--version", action="version", version=f"{parser.prog} version {VERSION}",
    )
    parser.add_argument("DIRECTORY", type=Path, default=".", help="directory to parse")
    parser.add_argument(
        "-d", "--directorytree", action="store_true", help="create directory tree"
    )
    parser.add_argument(
        "-f", "--filetree", action="store_true", help="create file tree"
    )
    parser.add_argument("-m", "--metadata", action="store_true", help="parse metadata")
    parser.add_argument("-s", "--sfv", action="store_true", help="create sfv file")
    return parser


def main():
    """Run tikatree from command line"""

    parser = initArgparse()
    args = parser.parse_args()
    d = args.directorytree
    f = args.filetree
    m = args.metadata
    s = args.sfv

    if Path(args.DIRECTORY).exists() is True:
        basepath = Path(args.DIRECTORY)
        directorytree = f"{basepath.stem}_directory_tree.txt"
        filetree = f"{basepath.stem}_file_tree.json"
        metadata = f"{basepath.stem}_metadata.json"
        sfv = f"{basepath.stem}.sfv"
    else:
        raise NotADirectoryError(f"{args.DIRECTORY} does not exist")

    if d is True:
        createDirectoryTree(basepath, directorytree)
    elif f is True:
        createFileTree(basepath, filetree)
    elif m is True:
        createMetadata(basepath, metadata)
    elif s is True:
        createSfv(basepath, sfv)
    else:
        createDirectoryTree(basepath, directorytree)
        createFileTree(basepath, filetree)
        createMetadata(basepath, metadata)
        createSfv(basepath, sfv)


if __name__ == "__main__":
    main()
