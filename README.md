# tikatree

## Directory tree metadata parser using [Apache Tika](http://tika.apache.org/)

tikatree parses all files in a directory for metadata, it then saves both the directory tree and metadata into two seperate text files.

### Installation

`pip install tikatree`

tikatree uses [tika-python](https://github.com/chrismattmann/tika-python) for interacting with Apache Tika. You may need to refer to the [tika-python](https://github.com/chrismattmann/tika-python) documentation if you have any issues with Tika.

### Usage

Open up a command line and type `tikatree <directory>`, it'll create a directorystub_Directory_Tree.txt and a directorystub_Metadata.txt.

optional arguments:
  -h, --help     show a help message and exit
  -v, --version  show the program's version number and exit

### Example

`tikatree .\VM_Hardware_J\` would create these two text files above `VM_Hardware_J`:

- VM_Hardware_J_Directory_Tree.txt
- VM_Hardware_J_Metadata.txt

### Part of the Keep Dreaming Project

#### [Main Repository](https://phabricator.kairohm.dev/diffusion/49/)

#### [Project](https://phabricator.kairohm.dev/project/view/51/)

#### [Contributing](https://bookstack.kairohm.dev/books/keep-dreaming-project/page/contributing-to-the-keep-dreaming-project)
