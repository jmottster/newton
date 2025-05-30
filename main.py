# Nuitka Configuration
#
# nuitka-project: --company-name="Jason Mott"
# nuitka-project: --product-name="Newton's Blobs"
# nuitka-project: --product-version=0.2.0
# nuitka-project: --file-version=0.0.1
# nuitka-project: --file-description="A randomly generated solar system simulator with planets and moons"
# nuitka-project: --copyright="GPL-3.0 license"
# nuitka-project: --include-data-dir=./nb_ursina/models=nb_ursina/models
# nuitka-project: --include-data-dir=./nb_ursina/models/models_compressed=ursina/models_compressed
# nuitka-project: --include-data-dir=./nb_ursina/textures=nb_ursina/textures
# nuitka-project: --include-data-dir=./newtons_blobs/font=newtons_blobs/font
# nuitka-project: --include-data-dir=./newtons_blobs/img=newtons_blobs/img
# nuitka-project: --onefile-tempdir-spec="{CACHE_DIR}/jason_mott/newtons_blobs/{VERSION}"
#
# Compilation mode, standalone everywhere
# nuitka-project-if: {OS} in ("Windows", "Linux", "Darwin"):
#    nuitka-project: --onefile
#    nuitka-project: --file-reference-choice="runtime"
# nuitka-project-if: {OS} in ("Windows"):
#    nuitka-project: --windows-console-mode="disable"
#    nuitka-project: --output-filename=newton3D.exe
#    nuitka-project: --windows-icon-from-ico=newtons_blobs/img/newton_icon.ico
# nuitka-project-if: {OS} in ("Linux"):
#    nuitka-project: --output-filename=newton3D.bin
#    nuitka-project: --linux-icon=newtons_blobs/img/newton_icon.ico
#    nuitka-project: --include-data-files=./newtons_blobs/font/OpenSans-Regular.ttf=OpenSans-Regular.ttf
# nuitka-project-if: {OS} in ("Darwin"):
#    nuitka-project: --macos-create-app-bundle
#    nuitka-project: --output-filename=newton3D
#    nuitka-project: --macos-app-icon=newtons_blobs/img/newton_icon.ico
#
# Debugging options, controlled via environment variable at compile time.
# nuitka-project-if: os.getenv("DEBUG_COMPILATION", "no") == "yes":
#    nuitka-project: --force-stdout-spec={MAIN_DIRECTORY}/log.out.txt
#    nuitka-project: --force-stderr-spec={MAIN_DIRECTORY}/log.err.txt

"""
Newton's Laws, a simulator of physics at the scale of space

Main file to run application with

by Jason Mott, copyright 2025
"""

import newtons_blobs as nb
from nb_ursina import BlobUrsinaFactory

import os, sys


__author__ = "Jason Mott"
__copyright__ = "Copyright 2025"
__license__ = "GPL 3.0"
__version__ = nb.VERSION
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


if __name__ == "__main__":

    if "NUITKA_LAUNCH_TOKEN" in os.environ:
        sys.exit("Error, launch token must not be present or else fork bomb suspected.")
    os.environ["NUITKA_LAUNCH_TOKEN"] = "1"

    blober: nb.BlobRunner = nb.BlobRunner(BlobUrsinaFactory())
    blober.run()
