[![CE-GEN](https://raw.githubusercontent.com/r3w0p/ce-gen/master/config/images/logo/400.png)](https://github.com/r3w0p/ce-gen)

[![License](https://img.shields.io/github/license/r3w0p/ce-gen.svg)](https://github.com/r3w0p/ce-gen/blob/master/LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/r3w0p/ce-gen.svg)](https://github.com/r3w0p/ce-gen/graphs/commit-activity)
[![Open Issues](https://img.shields.io/github/issues-raw/r3w0p/ce-gen)](https://github.com/r3w0p/ce-gen/issues)

## How to Use

Download the code locally and install the required dependencies using:

`pip install -r requirements.txt`

### Media Files

You will need to have video, audio, and image files stored locally.
By default, these directories are expected in a `media` directory within the same directory as `main.py`.
Within `media` should be the following directories:

- `videos`: supports `.mkv`, `.mp4`, `.gif`
- `audio`: supports `.mp3`
- `images`: supports `.jpg`, `.jpeg`, `.png`, `.gif`

In this software, `.gif` files are treated as videos and can be stored in the
`media/videos` or `media/images` directory.

### Arguments

All arguments have default values and can be accessed using:

`python3 main.py --help`
