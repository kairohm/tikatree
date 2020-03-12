#!/usr/bin/env python
from argparse import ArgumentParser
from collections import defaultdict
from datetime import datetime
from functools import lru_cache
from hashlib import md5, sha256
from json import dump
from pathlib import Path
from time import time
from zlib import crc32

from tika import parser

from .DisplayablePath import DisplayablePath

BLOCK_SIZE = 65536
VERSION = "0.0.6"


def createMetadata(basepath, file):
    print(f"Creating: {file}")
    parents = basepath.parents[0]
    file = parents.joinpath(file)
    jsondata = defaultdict(dict)
    for item in filesCache(basepath):
        if item.is_file():
            try:
                # Get file info
                pathitem = Path(item)
                p = Path.resolve(item)
                parsed = parser.from_file(f"{p}")
                # Create data from file info
                file_info = parsed["metadata"]
                createJson(basepath, pathitem, file_info, jsondata)
            except OSError as oserr:
                print(f"{oserr}: Error parsing : {pathitem.name}")
    writeJson(jsondata, file)


def createDirectoryTree(basepath, file):
    print(f"Creating: {file}")
    parents = basepath.parents[0]
    file = parents.joinpath(file)
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
    print(f"Creating: {file}")
    parents = basepath.parents[0]
    file = parents.joinpath(file)
    jsondata = defaultdict(dict)
    for item in filesCache(basepath):
        if item.is_file():
            try:
                # Get file info
                pathitem = Path(item)
                filename = pathitem.name
                # Get file size, convert to KB
                size = pathitem.stat().st_size
                size = round(size / 1024, 2)
                # Get modification time (creation time can vary by OS)
                mod_time = datetime.fromtimestamp(pathitem.stat().st_mtime)
                # Get hashes of file contents
                sha = sha256()
                md = md5()
                with open(pathitem, "rb") as f:
                    fb = f.read(BLOCK_SIZE)
                    while len(fb) > 0:
                        sha.update(fb)
                        md.update(fb)
                        fb = f.read(BLOCK_SIZE)

                # Create json data from file info
                file_info = {}
                file_info["modified"] = f"{mod_time}"
                file_info["size"] = f"{size}KB"
                file_info["md5"] = md.hexdigest()
                file_info["sha256"] = sha.hexdigest()
                createJson(basepath, pathitem, file_info, jsondata)
            except OSError as oserr:
                print(f"{oserr}: Error parsing : {filename}")
    writeJson(jsondata, file)


def createSfv(basepath, file):
    print(f"Creating: {file}")
    parents = basepath.parents[0]
    file = parents.joinpath(file)
    sfv_dict = {}
    for item in filesCache(basepath):
        if item.is_file():
            try:
                # Get file info
                pathitem = Path(item)
                relative = pathitem.relative_to(parents)
                crc = 0
                # Get CRC32 of file contents
                with open(pathitem, "rb") as f:
                    fb = f.read(BLOCK_SIZE)
                    while len(fb) > 0:
                        crc = crc32(fb, crc)
                        fb = f.read(BLOCK_SIZE)
                crc = format(crc & 0xFFFFFFFF, "08x")
                sfv_dict[f"{relative}"] = f"{crc}"
                print(f"{relative} {crc}\n")
            except OSError as oserr:
                print(f"{oserr}: Error creating checksums for : {file}")
    try:
        with open(f"{file}", "a", encoding="utf-8") as f:
            for k, v in sfv_dict.items():
                f.writelines(f"{relative} {crc}\n")
    except OSError as oserr:
        print(f"{oserr}: Error writing : {file}")


def createJson(basepath, pathitem, file_info, jsondata):
    relative = pathitem.relative_to(basepath)
    parents = relative.parents[0]
    pathname = pathitem.name
    file_data = {}
    file_data[f"{pathname}"] = file_info
    jsondata[f"{parents}"].update(file_data)
    print(relative)


def writeJson(data, jsonfile):
    try:
        with open(jsonfile, "w", encoding="utf-8") as f:
            dump(data, f, indent=4, ensure_ascii=False)
    except OSError as oserr:
        print(f"{oserr}: Error writing : {jsonfile}")


def checkFileExists(file):
    if Path(file).exists() is True:
        print("Warning")
        del_file = input(f"{file} exists, would you like to delete it? Y or N: ")
        if del_file == "Y" or del_file == "y":
            print(f"Deleting: {file}")
            Path(file).unlink()
        else:
            raise FileExistsError(f"{file} exists")


@lru_cache(maxsize=None)
def filesCache(basepath):
    filescache = []
    for item in basepath.rglob("*"):
        filescache.append(item)
    return filescache


def initArgparse() -> ArgumentParser:
    parser = ArgumentParser(
        description="A directory tree metadata parser using Apache Tika, by default it runs arguments: -d, -f, -m, -s",
    )
    parser.add_argument(
        "-v", "--version", action="version", version=f"{parser.prog} version {VERSION}",
    )
    parser.add_argument("DIRECTORY", type=Path, default=".", help="directory to parse")
    # parser.add_argument("FILETYPE", type=str, default="*", nargs='*', help="filetypes to parse, separate with spaces")
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
    start_time = time()
    parser = initArgparse()
    args = parser.parse_args()
    d = args.directorytree
    f = args.filetree
    m = args.metadata
    s = args.sfv

    if Path(args.DIRECTORY).exists() is True:
        basepath = Path(args.DIRECTORY)
        directorytree = f"{basepath.name}_directory_tree.txt"
        filetree = f"{basepath.name}_file_tree.json"
        metadata = f"{basepath.name}_metadata.json"
        sfv = f"{basepath.name}.sfv"
    else:
        raise NotADirectoryError(f"{args.DIRECTORY} does not exist")

    if d is True:
        checkFileExists(directorytree)
        createDirectoryTree(basepath, directorytree)
    elif f is True:
        checkFileExists(filetree)
        createFileTree(basepath, filetree)
    elif m is True:
        checkFileExists(metadata)
        createMetadata(basepath, metadata)
    elif s is True:
        checkFileExists(sfv)
        createSfv(basepath, sfv)
    else:
        checkFileExists(directorytree)
        checkFileExists(filetree)
        checkFileExists(metadata)
        checkFileExists(sfv)
        createDirectoryTree(basepath, directorytree)
        createFileTree(basepath, filetree)
        createMetadata(basepath, metadata)
        createSfv(basepath, sfv)

    stop_time = time()
    print(f"Finished in {round(stop_time-start_time, 2)} seconds")


if __name__ == "__main__":
    main()
