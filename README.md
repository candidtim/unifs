# unifs

Unified FS-like CLI for S3, GCS, ADLS, HDFS, SMB, Dropbox, Google Drive, and
dozens of other [fsspec](https://github.com/fsspec)-supported "file systems".

    unifs conf use my-s3-bucket  # or a dropbox acount, an ftp server, etc.
    unifs ls -l /
    unifs mv /foo.txt /bar.txt
    unifs download /bar.txt ~/Downloads/local.copy.txt

`unifs` uses the term "file system" in an open sense for anything that can be
represented as a file storage and be manipulated with the commands one would
usually expect, such as `ls`, `cat`, and `mv` for example, as well as commands
to upload and download the data when working with remote back-ends (e.g., a
cloud-based BLOB storage).

`unifs` supports multiple back-ends, such as a local file system, (S)FTP,
Google Drive, various blob storage such as S3, GCS, ADLS, and dozens of other
implementations. It is based on `fsspec` and it supports any available `fsspec`
implementation. Use `unifs impl list` to list supported protocols, but know
that other protocols can be added, including any custom implementations users
may provide.

`unifs` is different from FUSE implementations in that it doesn't mount a file
system. Instead, it provides a unified CLI that uses target back-end API to
execute the issued commands.

## Installation

`unifs` is a Python package:

    pip install unifs

Default `unifs` installation only supports a few basic protocols (e.g., a local
file system). To support other protocols you may need to install their
implementation packages. Because there are too many, `unifs` doesn't install
them for you by default, but it will tell which packages are missing if you
attempt to use a protocol that is not supported out of the box.

For example, to add the support for the GCS:

    pip install gcsfs

Make sure to install the additional packages to the same (virtual) environment
where `unifs` is installed.

To list known implementations and their prerequisites, use:

    unifs impl list
    unifs impl info NAME

To avoid conflicts with other Python packages, it is recommended to install
this application into a dedicated virtual environment. For example, you may use
`pipx`, or create a virtual environment manually. At very least, install with a
`--user` option (`pip install --user unifs`).

## Quick start

By default, `unifs` will use the local file system and will behave much like
issuing the similar commands directly in the shell:

    unifs ls -l /
    unifs cat /tmp/foo.txt
    unifs mv /tmp/foo.tx /tmp/bar.txt
    unifs --help

You need to configure `unifs` to let it know about other file systems you will
use.

## Configuration

You may either modify the configuration file, or use `unifs conf` command to
manipulate it.

### Using `unifs conf`

Get the list of configured file systems (currently active one is highlighted):

    unifs conf list

Set the active file system:

    unifs conf use NAME

### Configuration file

`unifs` configuration is stored in the default OS configuration directory. You
can obtain a config file path with:

    unifs conf path

If you didn't change your defualt OS settings, most likely it will
be:

    ~/.config/unifs/config.toml  # Linux
    ~/Library/Application Support/unifs/config.toml  # MacOS
    ~\AppData\Local\unifs\Config\config.toml # Windows

Configuration file is a TOML file that consists of:

 - a single `[unifs]` section where the currently active file system is set
 - any number of `[unifs.fs.NAME]` sections that declare the file systems

Example:

    [unifs]
    current = "local"

    [unifs.fs.local]
    protocol = "file"
    auto_mkdir = false

File system configuration is a set of key-value pairs that correspond exactly
to the key-worded arguments expected by the `fsspec` implementation. `protocol`
value is mandatory and is used to select the implementation, all other values
are passed to the specific implementation. Use `unifs impl info NAME` to the
list of accepted parameters for any protocol.

For example, for a GCS bucket:

    [unifs.fs.my-gcs-bucket]
    protocol = gcs
    project = "my-gcp-project"
    token = "/path/to/token.json"

## Status

Available `unifs` features are considered stable. `unifs` is being actively
developed and more features are coming.

## Word of caution

Beware that `unifs` may change data in the target back-end. Among other things,
it can move or remove (erase, without a possibility to restore) the data, if it
is instructed to do so by a user. Remember that `unifs` is only a command-line
layer between you as a user and the target file storage, and `unifs` only does
what the user instructs it to do.

`unifs` tries its best to prevent errors (e.g., uses interactive confirmations
for some commands), but ultimately **the user is responsible** for the
operations performed on files or BLOBs. Use at your own risk.

`unifs` is designed to be used on a workstation in an interactive shell, not on
a server, not in headless mode.

## License

MIT License. See the LICENSE document in the root of the source code
repository.
