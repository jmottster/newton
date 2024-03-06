# Compilation mode, standalone everywhere, except on macOS there app bundle
# nuitka-project-if: {OS} in ("Windows", "Linux", "FreeBSD", "Darwin"):
#    nuitka-project: --onefile
#    nuitka-project: --output-filename=newton3D.exe
# nuitka-project-if: {OS} in ("Windows"):
#    nuitka-project: --windows-icon-from-ico=newtons_blobs/img/newton_icon.ico
# nuitka-project-if: {OS} in ("Linux"):
#    nuitka-project: --linux-icon=newtons_blobs/img/newton_icon.ico
# nuitka-project-if: {OS} == "Darwin":
#    nuitka-project: --standalone
#    nuitka-project: --macos-create-app-bundle
#    nuitka-project: --macos-app-icon=newtons_blobs/img/newton_icon.ico
#
# Debugging options, controlled via environment variable at compile time.
# nuitka-project-if: os.getenv("DEBUG_COMPILATION", "no") == "yes":
#     nuitka-project: --enable-console
# nuitka-project-else:
#     nuitka-project: --disable-console
#
# nuitka-project:  --include-data-dir=./models_compressed=models_compressed
# nuitka-project:  --include-data-dir=./nb_ursina/models=nb_ursina/models
# nuitka-project:  --include-data-dir=./nb_ursina/textures=nb_ursina/textures
# nuitka-project:  --include-data-dir=./newtons_blobs/font=newtons_blobs/font
# nuitka-project:  --include-data-dir=./newtons_blobs/img=newtons_blobs/img

"""
Newton's Laws, a simulator of physics at the scale of space

Main file to run application with

by Jason Mott, copyright 2024
"""

import newtons_blobs as nb
from nb_ursina import BlobUrsinaFactory


__author__ = "Jason Mott"
__copyright__ = "Copyright 2024"
__license__ = "GPL 3.0"
__version__ = nb.VERSION
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


if __name__ == "__main__":
    blober: nb.BlobRunner = nb.BlobRunner(BlobUrsinaFactory())
    blober.run()
