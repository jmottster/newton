"""
Newton's Laws, a simulator of physics at the scale of space

Lists of textures for blobs, large and small

by Jason Mott, copyright 2025
"""

from newtons_blobs.globals import *

__author__ = "Jason Mott"
__copyright__ = "Copyright 2025"
__license__ = "GPL 3.0"
__version__ = VERSION
__maintainer__ = "Jason Mott"
__email__ = "github@jasonmott.com"
__status__ = "In Progress"


BLOB_TEXTURES_GAS = [
    "gas_planets/gas_001.png",
    "gas_planets/gas_002.png",
    "gas_planets/gas_003.png",
    "gas_planets/gas_004.png",
    "gas_planets/gas_005.png",
    "gas_planets/gas_006.png",
    "gas_planets/gas_007.png",
    "gas_planets/gas_008.png",
    "gas_planets/gas_009.png",
    "gas_planets/gas_010.png",
    "gas_planets/gas_011.png",
    "gas_planets/gas_012.png",
    "gas_planets/gas_013.png",
    "gas_planets/gas_014.png",
    "gas_planets/gas_015.png",
    "gas_planets/gas_016.png",
    "gas_planets/gas_017.png",
    "gas_planets/gas_018.png",
    "gas_planets/gas_019.png",
    "gas_planets/gas_020.png",
    "gas_planets/gas_021.png",
    "gas_planets/gas_022.png",
    "gas_planets/gas_023.png",
    "gas_planets/gas_024.png",
    "gas_planets/gas_025.png",
    "gas_planets/gas_026.png",
    "gas_planets/gas_027.png",
    "gas_planets/gas_028.png",
    "gas_planets/gas_029.png",
    "gas_planets/gas_030.png",
    "gas_planets/gas_031.png",
    "gas_planets/gas_032.png",
    "gas_planets/gas_033.jpg",
    "gas_planets/gas_034.jpg",
    "gas_planets/jupiter.jpg",
    "gas_planets/8k_jupiter.jpg",
    "gas_planets/saturn.jpg",
    "gas_planets/8k_saturn.jpg",
    "gas_planets/neptune.jpg",
    "gas_planets/neptune_02.jpg",
    "gas_planets/2k_neptune.jpg",
    "gas_planets/uranus.jpg",
    "gas_planets/2k_uranus.jpg",
]

BLOB_TEXTURES_RINGS = [
    "planet_rings/ring_001.png",
    "planet_rings/ring_002.png",
    "planet_rings/ring_003.png",
    "planet_rings/ring_004.png",
    "planet_rings/ring_005.png",
    "planet_rings/ring_006.png",
    "planet_rings/ring_007.png",
    "planet_rings/ring_008.png",
    "planet_rings/ring_009.png",
    "planet_rings/ring_010.png",
    "planet_rings/ring_011.png",
    "planet_rings/ring_012.png",
    "planet_rings/ring_013.png",
    "planet_rings/ring_014.png",
    "planet_rings/ring_015.png",
    "planet_rings/ring_016.png",
    "planet_rings/ring_017.png",
    "planet_rings/ring_018.png",
    "planet_rings/ring_019.png",
    "planet_rings/ring_020.png",
    "planet_rings/ring_021.png",
    "planet_rings/ring_022.png",
    "planet_rings/ring_023.png",
    "planet_rings/ring_024.png",
    "planet_rings/ring_025.png",
    "planet_rings/ring_026.png",
    "planet_rings/ring_027.png",
    "planet_rings/ring_028.png",
    "planet_rings/ring_029.png",
    "planet_rings/ring_030.png",
    "planet_rings/ring_031.png",
    "planet_rings/ring_032.png",
    "planet_rings/ring_033.png",
    "planet_rings/ring_034.png",
    "planet_rings/jupiter.png",
    "planet_rings/jupiter.png",
    "planet_rings/saturn_02.png",
    "planet_rings/saturn_02.png",
    "planet_rings/neptune_01.png",
    "planet_rings/neptune_01.png",
    "planet_rings/neptune_01.png",
    "planet_rings/uranus_02.png",
    "planet_rings/uranus_02.png",
]


BLOB_TEXTURES_ROCKY = [
    "rocky_planets/8k_earth_daymap.jpg",
    "rocky_planets/8k_mercury.jpg",
    "rocky_planets/4k_venus_atmosphere.jpg",
    "rocky_planets/8k_mars.jpg",
    "rocky_planets/grassland_04.png",
    "rocky_planets/jungle_05.png",
    "rocky_planets/marshy_04.png",
    "rocky_planets/martian_01.png",
    "rocky_planets/sandy_03.png",
    "rocky_planets/snowy_01.png",
    "rocky_planets/tundra_02.png",
    "rocky_planets/alpine_20.png",
    "rocky_planets/fungal_13.png",
    "rocky_planets/ice_03.png",
    "rocky_planets/dry_mud_03.png",
    "rocky_planets/oasis_02.png",
    "rocky_planets/oceanic_19.png",
    "rocky_planets/primordial_14.png",
    "rocky_planets/savannah_09.png",
    "rocky_planets/tundral_14.png",
    "rocky_planets/epsilon_01.jpg",
    "rocky_planets/terrestrial_09.png",
    "rocky_planets/earth_02.jpg",
    "rocky_planets/terraformed_mars.jpg",
]

BLOB_TEXTURES_MOON = [
    "moons/8k_moon.jpg",
    "moons/4k_ceres_fictional.jpg",
    "moons/4k_eris_fictional.jpg",
    "moons/4k_haumea_fictional.jpg",
    "moons/4k_makemake_fictional.jpg",
    "moons/8k_venus_surface.jpg",
    "moons/arid_03.png",
    "moons/methane_01.png",
    "moons/barren_02.png",
    "moons/dusty_02.png",
    "moons/epsilon_02.jpg",
    "moons/epsilon_03.jpg",
    "moons/rock_17.png",
    "moons/pluto.jpg",
    "moons/moon_01.png",
    "moons/moon_02.jpg",
    "moons/moon_03.jpg",
    "moons/moon_04.jpg",
]

# orig: (25 / 255, 100 / 255, 150 / 255, 0.9)
BLOB_TRAIL_COLOR = [
    # Blue
    (0 / 255, 132 / 255, 184 / 255, 0.9),  # rgb(0, 132, 184)
    (5 / 255, 102 / 255, 141 / 255, 0.9),  # rgb(5, 102, 141)
    (57 / 255, 81 / 255, 91 / 255, 0.9),  # rgb(57, 81, 91)
    # Green
    (0 / 255, 175 / 255, 102 / 255, 0.9),  # rgb(0, 175, 102)
    (9 / 255, 129 / 255, 74 / 255, 0.9),  # rgb(9, 129, 74)
    (54 / 255, 84 / 255, 71 / 255, 0.9),  # rgb(54, 84, 71)
    # Yellow
    (207 / 255, 190 / 255, 0 / 255, 0.9),  # rgb(207, 190, 0)
    (170 / 255, 156 / 255, 1 / 255, 0.9),  # rgb(170, 156, 1)
    (108 / 255, 105 / 255, 65 / 255, 0.9),  # rgb(108, 105, 65)
    # Orange
    (207 / 255, 107 / 255, 0 / 255, 0.9),  # rgb(207, 107, 0)
    (171 / 255, 87 / 255, 0 / 255, 0.9),  # rgb(171, 87, 0)
    (108 / 255, 87 / 255, 65 / 255, 0.9),  # rgb(108, 87, 65)
    # Red
    (212 / 255, 14 / 255, 0 / 255, 0.9),  # rgb(212, 14, 0)
    (170 / 255, 20 / 255, 10 / 255, 0.9),  # rgb(170, 20, 10)
    (109 / 255, 72 / 255, 69 / 255, 0.9),  # rgb(109, 72, 69)
    # Purple
    (166 / 255, 0 / 255, 83 / 255, 0.9),  # rgb(166, 0, 83)
    (89 / 255, 41 / 255, 65 / 255, 0.9),  # rgb(89, 41, 65)
    (70 / 255, 58 / 255, 64 / 255, 0.9),  # rgb(70, 58, 64)
]

BLOB_BACKGROUND_LARGE = [
    "backgrounds/8k_stars_milky_way.jpeg",
    "backgrounds/starmap_2020_8k_gal.png",
    "backgrounds/multi_nebulae_2.png",
    "backgrounds/night_sky_02.jpg",
]

BLOB_BACKGROUND_SMALL = [
    "backgrounds/8k_stars_milky_way-small.jpeg",
    "backgrounds/starmap_2020_8k_gal-small.png",
    "backgrounds/multi_nebulae_2-small.png",
    "backgrounds/night_sky_02-small.jpg",
]

BLOB_BACKGROUND_ROTATION = [
    (0, 0, 40),
    (0, 0, 40),
    (0, 0, 90),
    (0, 0, 0),
]
