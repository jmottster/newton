# Newton's Blobs

### Version 0.0.4 Alpha Prototype 3D

*A simulator of Newton's laws of physics, using space scale objects*

This is a small project just for me to learn and experiment. In spite of a life long interest in physics, I've never brought it to my programming skills. This is my playground for doing so. I am not a physicist though, so don't hold this to that standard! Feedback and/or help building this out is always welcome.

Alpha release 0.0.4! In this release, there is nothing different in terms of user experience, this was a major code refactoring in preparation for replacing pygame as the graphics engine. In the last version the feature of auto save and load was added, on top of the many improvements from 0.0.2: window resizing and full-screen now supported, many performance tweaks that allow up to 150 blobs at 60/fps, new pallet of colors, "elapsed years" display, and of course, now in 3D! While it's fully 3D under the hood, the graphics are still 2D and the 3D effect is faked by adjusting blob size according to position on the z axis and a lighting effect on the blobs that point to the center blob.

To toggle auto save and load, just press the E key.

#### Installation

Two ways, the easy way (Windows only) and the nerdy way . . .

###### The easy way (Windows only)

1. Download Windows executable here:
   1. [Release 0.0.4](https://github.com/jmottster/newton/releases/download/Release%2Fv0.0.4/newton.exe)
2. Save where you want to store it
3. Double click and enjoy (runs as is, no system installation)

###### The nerdy way

1. **Requirements:**
   1. git and github account
   2. python 3.11 or newer
      1. Ursina 6.1.2
      2. Numpy 1.26.3
      3. Pygame-CE 2.4.0 (only to run fake 3D version)
2. **In terminal:**
   1. **cd** to desired working dir
   2. **git clone https://github.com/jmottster/newton.git**
      1. ^ or whatever method you use to pull a repository from github
   3. run **python main.py**
   4. for fake 3D version: run **python main_pyg.py** (no movement controls)

#### Instructions

This is a space-level gravity and collision simulator. At the center is a sun mass blob, and orbiting it are randomly created Earth to Moon mass blobs. This simulation uses real space level values for distance, mass, velocity, and acceleration. The size of the blobs are exaggerated, of course, and distance is scaled when rendered on the screen. :D Time is sped up to about 600 hours per second.

This is a prototype, a proof of concept. Thus, it's not very interactive yet, it's just showing what it can simulate. However, there are some controls here while you watch it go.

* Movement controls:
  * W - Move forward
  * S - Move backward
  * A - Move left
  * D - Move right
  * E - Move up
  * X - Move down
  * MOUSE WHEEL SCROLL UP - increase speed
  * MOUSE WHEEL SCROLL DOWN - decrease speed
  * R - Return to default speed
* Rotation controls:
  * Z - Roll left
  * C - Roll right
  * MOUSE MOVE LEFT - Yaw left
  * MOUSE MOVE RIGHT - Yaw right
  * MOUSE MOVE FORWARD - Pitch up
  * MOUSE MOVE BACKWARD - Pitch down
* Miscellaneous Controls:
  * Q - Disengage/reengage mouse
  * V - Toggle ambient light (helps to see dark side of blobs)
  * SPACEBAR - Pause/Unpause
  * ESC - Quit
  * F - Toggle fullscreen/windowed mode
  * 1 - Start over based on options selected with keys 1 and 2
  * 2 - Toggle Start pattern between square and circular (see below)
  * 3 - Toggle start velocities between perfect orbit and random (it'll be within a range that works)
  * 4 - Toggle stat displays
  * 5 - Toggle auto save/load feature (if on, will save app state upon exit and reload it on next startup)

Some screen shots:

<img src="./resources/screen_shot004.png"/>

<img src="./resources/screen_shot005.png"/>

<img src="./resources/screen_shot006.png"/>

<img src="./resources/screen_shot007.png"/>

<img src="./resources/screen_shot008.png"/>
