#!/usr/bin/env python
from argparse import ArgumentParser
from collections import defaultdict
from csv import DictWriter
from datetime import datetime
from functools import lru_cache
from hashlib import md5, sha256
from json import dump
from pathlib import Path
from time import time
from zlib import crc32

from psutil import Process
from tika import parser
from tqdm import tqdm

BLOCK_SIZE = 65536
VERSION = "0.1.0"
MASK = []


def createMetadata(basepath, file):
    tqdm.write(f"Creating: {file}")
    file = basepath.parents[0].joinpath(file)
    jsondata = defaultdict(dict)
    for item in tqdm(filesCache(basepath)):
        try:
            # Get file info
            p = Path.resolve(item)
            parsed = parser.from_file(f"{p}")
            # Create data from file info
            file_info = parsed["metadata"]
            createJson(basepath, item, file_info, jsondata)
        except OSError as oserr:
            print(f"{oserr}: Error parsing : {item.name}")
    writeJson(jsondata, file)


def createNewMetadata(basepath):
    tqdm.write("Parsing Metadata")
    parents = basepath.parents[0]
    for item in filesCache(basepath):
        try:
            # Get file info
            parsed = parser.from_file(f"{Path.resolve(item)}")
            # Create data from file info
            file_info = {}
            file_info[item.name] = getFileInfo(item)
            file_info["Metadata"] = parsed["metadata"]
            relative = item.relative_to(parents)
            *y, z = relative.parts
            p = Path(parents).joinpath("tikatree", *y)
            if p.exists():
                pass
            else:
                p.mkdir(parents=True)
            file = Path(p).joinpath(f"{item.name}.json")
        except OSError as oserr:
            print(f"{oserr}: Error parsing : {item.name}")
        writeJson(file_info, file)


@lru_cache(maxsize=None)
def getFileInfo(item):
    # Get file size, convert to KB
    size = round(item.stat().st_size / 1024, 2)
    # Get modification time (creation time can vary by OS)
    # Get hashes of file contents
    sha = sha256()
    md = md5()
    with open(item, "rb") as f:
        fb = f.read(BLOCK_SIZE)
        while len(fb) > 0:
            sha.update(fb)
            md.update(fb)
            fb = f.read(BLOCK_SIZE)
    # Create json data from file info
    file_info = {}
    file_info["modified"] = f"{datetime.fromtimestamp(item.stat().st_mtime)}"
    file_info["size"] = f"{size}KB"
    file_info["md5"] = md.hexdigest()
    file_info["sha256"] = sha.hexdigest()
    return file_info


def createDirectoryTree(basepath, file):
    tqdm.write(f"Creating: {file}")
    file = basepath.parents[0].joinpath(file)
    paths = DisplayablePath.make_tree(Path(basepath))
    dirtree_list = []
    for path in tqdm(paths):
        dirtree_list.append(f"{path.displayable()}\n")
    with open(file, "a", encoding="utf-8") as outfile:
        try:
            outfile.writelines(dirtree_list)
        except OSError as oserr:
            print(f"{oserr}: Error creating : {file}")


def createFileTree(basepath, file, csvfile):
    tqdm.write(f"Creating: {file}")
    parents = basepath.parents[0]
    file = parents.joinpath(file)
    csvfile = parents.joinpath(csvfile)
    jsondata = defaultdict(dict)
    for item in tqdm(filesCache(basepath)):
        try:
            # Get file info
            file_info = getFileInfo(item)
            createJson(basepath, item, file_info, jsondata)
        except OSError as oserr:
            print(f"{oserr}: Error parsing : {item.name}")
    writeJson(jsondata, file)
    createCsv(basepath, jsondata, csvfile)


def createSfv(basepath, file):
    tqdm.write(f"Creating: {file}")
    parents = basepath.parents[0]
    file = parents.joinpath(file)
    sfv_dict = {}
    for item in tqdm(filesCache(basepath)):
        try:
            # Get file info
            relative = item.relative_to(parents)
            crc = 0
            # Get CRC32 of file contents
            with open(item, "rb") as f:
                fb = f.read(BLOCK_SIZE)
                while len(fb) > 0:
                    crc = crc32(fb, crc)
                    fb = f.read(BLOCK_SIZE)
            crc = format(crc & 0xFFFFFFFF, "08x")
            sfv_dict[f"{relative}"] = f"{crc}"
        except OSError as oserr:
            print(f"{oserr}: Error creating checksums for : {file}")
    try:
        with open(f"{file}", "a", encoding="utf-8") as f:
            for k, v in sfv_dict.items():
                f.writelines(f"{k} {v}\n")
    except OSError as oserr:
        print(f"{oserr}: Error writing : {file}")


def createJson(basepath, pathitem, file_info, jsondata):
    relative = pathitem.relative_to(basepath)
    file_data = {}
    file_data[f"{pathitem.name}"] = file_info
    jsondata[f"{relative.parents[0]}"].update(file_data)


def writeJson(data, jsonfile):
    try:
        with open(jsonfile, "w", encoding="utf-8") as f:
            dump(data, f, indent=4, ensure_ascii=False)
    except OSError as oserr:
        print(f"{oserr}: Error writing : {jsonfile}")


def checkFileExists(basepath, file, yes):
    file = basepath.parents[0].joinpath(file)
    if Path(file).exists() is True:
        if yes is False:
            tqdm.write("Warning")
            del_file = input(f"{file} exists, would you like to delete it? Y or N: ")
        if yes is True:
            del_file = "Y"
        if del_file == "Y" or del_file == "y":
            tqdm.write(f"Deleting: {file}")
            Path(file).unlink()
        else:
            raise FileExistsError(f"{file} exists")


@lru_cache(maxsize=None)
def filesCache(basepath):
    filescache = []
    for item in basepath.rglob("*"):
        if item.is_file():
            if MASK:
                if not any(x in f"{item.parents[0]}" for x in MASK):
                    filescache.append(item)
            else:
                filescache.append(item)
    return filescache


def createCsv(basepath, data, file):
    tqdm.write(f"Creating: {file}")
    basepath = basepath.name
    try:
        with open(file, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["path", "filename", "modified", "size", "sha256", "root"]
            writer = DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for path, filename in data.items():
                for k, v in filename.items():
                    temp = {}
                    temp["path"] = path
                    temp["filename"] = k
                    temp["modified"] = v["modified"]
                    temp["size"] = v["size"]
                    temp["sha256"] = v["sha256"]
                    temp["root"] = basepath
                    writer.writerow(temp)
    except OSError as oserr:
        print(f"{oserr}: Error writing : {file}")


# https://stackoverflow.com/questions/9727673/list-directory-tree-structure-in-python
class DisplayablePath(object):
    display_filename_prefix_middle = "├──"
    display_filename_prefix_last = "└──"
    display_parent_prefix_middle = "    "
    display_parent_prefix_last = "│   "

    def __init__(self, path, parent_path, is_last):
        self.path = Path(str(path))
        self.parent = parent_path
        self.is_last = is_last
        if self.parent:
            self.depth = self.parent.depth + 1
        else:
            self.depth = 0

    @property
    def displayname(self):
        if self.path.is_symlink():
            pass
        elif self.path.is_dir():
            return self.path.name + "/"
        return self.path.name

    @classmethod
    def make_tree(cls, root, parent=None, is_last=False, criteria=None):
        root = Path(str(root))
        criteria = criteria or cls._default_criteria

        displayable_root = cls(root, parent, is_last)
        yield displayable_root

        children = sorted(
            list(path for path in root.iterdir() if criteria(path)),
            key=lambda s: str(s).lower(),
        )
        count = 1
        for path in children:
            is_last = count == len(children)
            try:
                if MASK:
                    parents = path.parents[0]
                    if not any(x in f"{parents}" for x in MASK):
                        if path.is_symlink():
                            pass
                        elif path.is_dir():
                            yield from cls.make_tree(
                                path,
                                parent=displayable_root,
                                is_last=is_last,
                                criteria=criteria,
                            )
                        else:
                            yield cls(path, displayable_root, is_last)
                else:
                    if path.is_symlink():
                        pass
                    elif path.is_dir():
                        yield from cls.make_tree(
                            path,
                            parent=displayable_root,
                            is_last=is_last,
                            criteria=criteria,
                        )
                    else:
                        yield cls(path, displayable_root, is_last)
            except PermissionError:
                pass
            count += 1

    @classmethod
    def _default_criteria(cls, path):
        return True

    def displayable(self):
        if self.parent is None:
            return self.displayname

        _filename_prefix = (
            self.display_filename_prefix_last
            if self.is_last
            else self.display_filename_prefix_middle
        )

        parts = ["{!s} {!s}".format(_filename_prefix, self.displayname)]

        parent = self.parent
        while parent and parent.parent is not None:
            parts.append(
                self.display_parent_prefix_middle
                if parent.is_last
                else self.display_parent_prefix_last
            )
            parent = parent.parent

        return "".join(reversed(parts))


def killTika():
    tikatree_proc = Process()
    parent = tikatree_proc.parent()
    tikatree_children = parent.children(recursive=True)
    for child in tikatree_children:
        if child.name() == "java.exe":
            child.terminate()


def initArgparse() -> ArgumentParser:
    parser = ArgumentParser(
        description="A directory tree metadata parser using Apache Tika, by default it runs arguments: -d, -f, -m, -s",
    )
    parser.add_argument(
        "-v", "--version", action="version", version=f"{parser.prog} version {VERSION}",
    )
    parser.add_argument(
        "DIRECTORY", type=Path, default=".", nargs="+", help="directory(s) to parse"
    )
    parser.add_argument(
        "-d", "--directorytree", action="store_true", help="create directory tree"
    )
    parser.add_argument(
        "-e",
        "--exclude",
        nargs="+",
        help="directory(s) to exclude, includes subdirectories",
    )
    parser.add_argument(
        "-f", "--filetree", action="store_true", help="creates a json and csv file tree"
    )
    parser.add_argument("-m", "--metadata", action="store_true", help="parse metadata")
    parser.add_argument(
        "-nm",
        "--newmetadata",
        action="store_true",
        help="create individual metadata files in a 'tikatree' directory",
    )
    parser.add_argument("-s", "--sfv", action="store_true", help="create sfv file")
    parser.add_argument(
        "-y", "--yes", action="store_true", help="automatically overwrite older files"
    )
    return parser


def main():
    """Run tikatree from command line"""
    global MASK
    start_time = time()
    parser = initArgparse()
    args = parser.parse_args()
    dirtree = args.directorytree
    filetree = args.filetree
    meta = args.metadata
    newmeta = args.newmetadata
    sfv = args.sfv
    yes = args.yes
    MASK = args.exclude

    for i in args.DIRECTORY:
        if Path(i).exists() is True:
            basepath = Path(i)
        else:
            raise NotADirectoryError(f"{i} does not exist")
        default = False
        if dirtree == sfv == filetree == meta == newmeta is False:
            default = True
        if dirtree is True or default is True:
            dirtree_file = f"{basepath.name}_directory_tree.txt"
            checkFileExists(basepath, dirtree_file, yes)
            createDirectoryTree(basepath, dirtree_file)
        if sfv is True or default is True:
            sfv_file = f"{basepath.name}.sfv"
            checkFileExists(basepath, sfv_file, yes)
            createSfv(basepath, sfv_file)
        if filetree is True or default is True:
            csvtree_file = f"{basepath.name}_file_tree.csv"
            jsontree_file = f"{basepath.name}_file_tree.json"
            checkFileExists(basepath, jsontree_file, yes)
            checkFileExists(basepath, csvtree_file, yes)
            createFileTree(basepath, jsontree_file, csvtree_file)
        if meta is True or default is True:
            metadata_file = f"{basepath.name}_metadata.json"
            checkFileExists(basepath, metadata_file, yes)
            createMetadata(basepath, metadata_file)
        if newmeta is True:
            createNewMetadata(basepath)
        filesCache.cache_clear()
        getFileInfo.cache_clear()
        killTika()

    stop_time = time()
    print(f"Finished in {round(stop_time-start_time, 2)} seconds")


if __name__ == "__main__":
    main()
