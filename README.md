# tikatree

## Directory tree metadata parser using [Apache Tika](http://tika.apache.org/)

tikatree parses all files in a directory and creates a:

- _Metadata.json - A single file with the metdata from each file that was parsed
- _File_Tree.json - A list of all files and directories with some basic information
- _Directory_Tree.txt - A graphical representation of the directory

### Installation

`pip install tikatree`

tikatree uses [tika-python](https://github.com/chrismattmann/tika-python) for interacting with Apache Tika. You may need to refer to the [tika-python](https://github.com/chrismattmann/tika-python) documentation if you have any issues with Tika.

### Usage

Open up a command line and type `tikatree <directory>`, by default it'll create all files at or above that directory.

optional arguments:
  -h, --help           show this help message and exit
  -v, --version        show program's version number and exit
  -d, --directorytree  create directory tree
  -m, --metadata       parse metadata
  -f, --filetree       create file tree

### Example

I've included some output examples in the `output_examples` folder.

### Part of the Keep Dreaming Project

#### [Main Repository](https://phabricator.kairohm.dev/diffusion/49/)

#### [Project](https://phabricator.kairohm.dev/project/view/51/)

#### [Contributing](https://bookstack.kairohm.dev/books/keep-dreaming-project/page/contributing-to-the-keep-dreaming-project)
