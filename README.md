# tikatree

## Directory tree metadata parser using [Apache Tika](http://tika.apache.org/)

tikatree parses all files in a directory and creates a:

- _metadata.json - A single file with the metdata from each file that was parsed
- _file_tree.json and _file_tree.csv - A list of all files and directories with some basic information. One file that's easy to read and another for importing into excel and things like that
- _directory_tree.txt - A graphical representation of the directory
- .sfv - A CRC32 checksum

### Installation

`pip install tikatree`

tikatree uses [tika-python](https://github.com/chrismattmann/tika-python) for interacting with Apache Tika. You may need to refer to the [tika-python](https://github.com/chrismattmann/tika-python) documentation if you have any issues with Tika.

### Usage

Open up a command line and type `tikatree <directory>`, by default it'll create all files at or above that directory. You can target multiple directories, just put a space in between each one on the command line.

```PowerShell
usage: tikatree [-h] [-v] [-d] [-e EXCLUDE [EXCLUDE ...]] [-f] [-m] [-nm] [-s] [-y] DIRECTORY [DIRECTORY ...]

A directory tree metadata parser using Apache Tika, by default it runs arguments: -d, -f, -m, -s

positional arguments:
  DIRECTORY             directory(s) to parse

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -d, --directorytree   create directory tree
  -e EXCLUDE [EXCLUDE ...], --exclude EXCLUDE [EXCLUDE ...]
                        directory(s) to exclude, includes subdirectories
  -f, --filetree        creates a json and csv file tree
  -m, --metadata        parse metadata
  -nm, --newmetadata    create individual metadata files in a 'tikatree' directory
  -s, --sfv             create sfv file
  -y, --yes             automatically overwrite older files
```

### Example

I've included some output examples in the `output_examples` folder.

### Windows Fixes

When parsing files too fast there can be connection errors to Apache Tika. In order to get around this run these commands in Powershell as Admin

```PowerShell
$KeyPath = "HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters"
Set-ItemProperty -Path $KeyPath -Name "MaxUserPort" -Value 65534
```

```PowerShell
$KeyPath = "HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters"
Set-ItemProperty -Path $KeyPath -Name "TcpTimedWaitDelay" -Value 30
```

### Part of the Keep Dreaming Project

#### [Main Repository](https://phabricator.kairohm.dev/diffusion/49/)

#### [Project](https://phabricator.kairohm.dev/project/view/51/)

#### [GitHub Mirror](https://github.com/kairohm/tikatree)

#### [Contributing](https://bookstack.kairohm.dev/books/keep-dreaming-project/page/contributing-to-the-keep-dreaming-project)
