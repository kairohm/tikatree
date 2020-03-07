#!/usr/bin/env python
import argparse
from pathlib import Path
from pprint import pprint

from tika import parser

from .DisplayablePath import DisplayablePath


def saveMetadata(basepath, metadata):
    print("Creating : ", metadata)
    for item in basepath.rglob("*"):
        if item.is_file():
            try:
                with open(metadata, "a", encoding="utf-8") as outfile:
                    try:
                        e = Path(item)
                        parents = e.relative_to(basepath)
                        outfile.writelines(f"\n\n{parents}\n")
                        p = Path.resolve(item)
                        parsed = parser.from_file(f"{p}")
                        pprint(parsed["metadata"], stream=outfile)
                        # outfile.writelines("\n")
                        print(p)
                    except OSError:
                        print("Error parsing : ", item.name)
            except OSError:
                print("Error opening : ", metadata)


def saveTree(basepath, tree):
    print("Creating : ", tree)
    paths = DisplayablePath.make_tree(Path(basepath))
    for path in paths:
        with open(tree, "a", encoding="utf-8") as outfile:
            try:
                outfile.writelines(f"{path.displayable()}\n")
            except OSError:
                print("Error saving : ", tree)


def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        usage="%(prog)s [-h, --help] [-v, --version] directory",
        description="A directory tree metadata parser using Apache Tika",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"{parser.prog} version 0.0.2",
    )
    parser.add_argument("directory", type=Path, help="directory to parse")
    return parser


def main() -> None:
    """Run tikatree from command line"""

    parser = init_argparse()
    args = parser.parse_args()
    directory = args.directory
    basepath = Path(directory)
    metadata = f"{basepath.stem}_Metadata.txt"
    tree = f"{basepath.stem}_Directory_Tree.txt"

    if Path(tree).exists() is False:
        saveTree(basepath, tree)
    else:
        print(tree, " exists")

    if Path(metadata).exists() is False:
        saveMetadata(basepath, metadata)
    else:
        print(metadata, " exists")


if __name__ == "__main__":
    main()
