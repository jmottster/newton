"""
Newton's Laws, a simulator of physics at the scale of space

An encapsulation of the fps clock

by Jason Mott, copyright 2024
"""

from typing import Self

from panda3d.core import ClockObject  # type: ignore
from newtons_blobs.globals import *


__author__ = "Jason Mott"
__copyright__ = "Copyright 2024"
__license__ = "GPL 3.0"
__version__ = VERSION
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


class FPS:
    """
    An encapsulation of the fps clock

    Attributes
    ----------

    clock: FPS.CLock
        The clock object keeps track of frame rates and delta times

    """

    paused: bool = False
    dt: float = 0.0

    def __init__(self: Self):
        class Clock:
            """
            The clock object keeps track of frame rates and delta times

            Methods
            -------

            tick(time: float) -> None
                A way to set the frame rate

            getAverageFrameRate() -> float
                Returns the average framerate for the running Ursina app, clocked every 4 ticks

            """

            def __init__(self: Self):
                self.frame_rate: float = float(FRAME_RATE)
                self.globalClock = ClockObject.getGlobalClock()
                self.globalClock.setMode(ClockObject.MLimited)
                self.globalClock.setFrameRate(self.frame_rate + 10)
                if CLOCK_FPS:
                    self.globalClock.setAverageFrameRateInterval(4)
                else:
                    self.globalClock.setAverageFrameRateInterval(0)
                self.dt: float = 1 / self.frame_rate  # self.globalClock.getDt()
                FPS.dt = self.dt

            def tick(self: Self, time: float) -> None:
                if time != self.frame_rate:
                    self.frame_rate = time
                    self.globalClock.setFrameRate(time)

                # self.dt = self.globalClock.getDt()
                # FPS.dt = self.dt

            def getAverageFrameRate(self: Self) -> float:
                return self.globalClock.getAverageFrameRate()

        self.clock: Clock = Clock()
