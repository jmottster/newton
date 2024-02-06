# Newton's Blobs

### Version 0.0.2 Alpha Prototype 3D

*A simulator of Newton's laws of physics, using space scale objects*

This is a small project just for me to learn and experiment. In spite of a life long interest in physics, I've never brought it to my programming skills. This is my playground for doing so. I am not a physicist though, so don't hold this to that standard! Feedback and/or help building this out is always welcome.

Alpha release 0.0.2! This is the prototype 3d version! In this version there are many improvements: window resizing and full-screen now supported, many performance tweaks that allow up to 150 blobs at 60/fps, new pallet of colors, "elapsed years" display, and of course, now in 3D! While it's fully 3D under the hood, the graphics are still 2D and the 3D effect is faked by adjusting blob size according to position on the z axis and a lighting effect on the blobs that point to the center blob.

#### Installation

Two ways, the easy way (Windows only) and the nerdy way . . .

###### The easy way (Windows only)

1. Download Windows executalbe here:
2. Save where you want to store it
3. Double click and enjoy (runs as is, no system installation)

###### The nerdy way

1. **Requrments:**
   1. git and github account
   2. python 3.11.5
      1. Pygame-CE 2.4.0
      2. Numpy 1.26.3
   3. ^ other versions may work, just not tested on any
2. **In terminal:**
   1. **cd** to desired working dir
   2. **git clone https://github.com/jmottster/newton.git**
      1. ^ or whatever method you use to pull a repository from github
   3. run **python main.py**

#### Instructions

This is a space-level gravity and collision simulator. At the center is a sun mass blob, and orbiting it are randomly created Earth to Moon mass blobs. This simulation uses real space level values for distance, mass, velocity, and acceleration. The size of the blobs are exaggerated, of course, and distance is scaled when rendered on the screen. :D Time is sped up to about 600 hours per second.

This is a prototype, a proof of concept. Thus, it's not very interactive yet, it's just showing what it can simulate. However, there are a few controls here while you watch it go.

* SPACEBAR - Puase/Unpause
* F - Toggle fullscreen/windowed mode
* D - Toggle stat displays
* A - Toggle Start pattern between square and circular (see below)
* W - Toggle start velocities between perfect orbit and random (it'll be within a range that works)
* S - Start over based on W and A options!

Some screen shots:

<img src="./resources/screen_shot004.png"/>


<img src="./resources/screen_shot005.png"/>


<img src="./resources/screen_shot006.png"/>


<img src="./resources/screen_shot007.png"/>


<img src="./resources/screen_shot008.png"/>


---

### Version 0.0.1 Alpha Prototype 2D

*A simulator of Newton's laws of physics, using space scale objects*

Alpha release 0.0.1! This is the prototype 2d version. It'll probably be the only 2d version, as the 3d version is well under way.

There isn't much to it, but it can be fun to just watch the blobs go . . .

<img src="resources/screen_shot001.png" />

## Instructions

This is a gravity and collision simulator. At the center is a sun sized blob, and orbiting it are randomly created Earth to Mercury sized blobs. This simulation uses real space level values for distance, mass, velocity, and acceleration. The size of the blobs are exaggerated, of course, and distance is scaled when rendered on the screen. :D Time is sped up to about 360 days per second.

There are a few controls here while you watch it go.

* SPACEBAR - Puase/Unpause
* D - Toggle stat displays
* A - Toggle Start pattern between square and circular (see below)
* W - Toggle start velocities between perfect orbit and random (it'll be within a range that works)
* S - Start over based on above options!

Here are Windows executable downloads if you're not inclined to fiddle around with Python code. The window is not resizable, so there is a 1000x1000 and a 768x768 version.

[Release 0.0.1 downloads](https://github.com/jmottster/newton/releases/tag/release%2F0.0.1)

Here are screen shots of the two optional starting patterns . . .

<img src="resources/screen_shot002.png"/>

<img src="resources/screen_shot003.png"/>
