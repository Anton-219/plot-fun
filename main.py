# -*- coding: utf-8 -*-
"""
Created on Sat Aug  7 03:22:38 2021

@author: Offszanka

This module is solely to separate the command line parsing from the data plotting.

Ideas: Use a spinning symbol to indicate that the program is working.
"""

import os
import argparse
import warnings

import numpy as np

## Constants
DEFAULT_IMAGE_NAME = 'germany_energymix'
DEFAULT_VIDEO_NAME = 'germany_energymix'

DEFAULT_IMAGE_EXT = '.jpeg'
DEFAULT_VIDEO_EXT = '.mp4'

parse = argparse.ArgumentParser(description='Plot the data for the given years.'\
                                ' The default behaviour will save images and'\
                                ' an animation for the years 2002 to 2020.'\
                                'If an argument is given only this will be made.'\
                                'Needs more advanced packages like geopandas.',
                                formatter_class=argparse.RawTextHelpFormatter)
parse.add_argument('-i', '--image',
                   help='''Plots and saves the diagram image for the given year(s).
If no extension is given jpeg is used.
Usage: -i <name>''',
                   dest='image',
                   nargs=1)
parse.add_argument('-v', '-a', '--video', '--animation',
                   help='''Makes and saves an animation for the given years.
Only -gif and -mp4 extension is available.
If no extension is given mp4 is used.
Will make an animation from the earliest to the latest year.
Usage: -v <name of file> ''',
                   dest='video',
                   nargs=1)
parse.add_argument('-y', '--years',
                   help='''Set the years.
The image will be plotted and saved for each given year.
The animation will go from the min year to max year. Only one year is not
implemented.
Usage: <year1> <year2> <year3> ...
The default behaviour includes 2002 2020''',
                   dest='years',
                   type=int,
                   nargs='+')

## Parse arguments.
args = parse.parse_args()

image_name = args.image
video_name = args.video
years = args.years

image_ext = None
video_ext = None

if image_name is not None:
    t, ext = os.path.splitext(image_name[0])
    # Check if ext is empty or only contains a point.
    image_name = t
    if ext in '.':
        image_ext = DEFAULT_IMAGE_EXT
    else:
        image_ext = ext

if video_name is not None:
    t, ext = os.path.splitext(video_name[0])
    video_name = t
    if ext in ('.mp4', '.gif'):
        video_ext = ext
    else:
        video_ext = DEFAULT_VIDEO_EXT

# If both are not present then do default behaviour
if image_name is None and video_name is None:
    image_name = DEFAULT_IMAGE_NAME
    video_name = DEFAULT_VIDEO_NAME

    image_ext = DEFAULT_IMAGE_EXT
    video_ext = DEFAULT_VIDEO_EXT

if years is not None:
    # if len(years) == 2:
    #     years = np.arange(years[0], years[1])
    #     yz = np.hstack((years, years.max()+1))
    years = np.asarray(years)

    if years.min() < 2002 or years.max() > 2020:
        raise ValueError('There is no data before 2002 and after 2020.')
    if video_name is not None and len(years) == 1:
        warnings.warn('The animation needs a time period to work.')
        video_name = None
        video_ext = None
else:
    years = np.asarray([2002, 2020])

# Make a friendly welcome message.
# yz = np.hstack((years, years.max()+1))
yz = years
if image_name is not None:
    if len(years) > 1:
        image_text = f"images for the years {yz}"
    else:
        image_text = f"an image for the year {yz[0]}"
    isa = f"the images as {image_name}_[year]{image_ext}"
else:
    image_text = "no images"
    isa = ""


if video_name is not None:
    video_text = f"an animation for {yz.min()}-{yz.max()}"
    vsa = f"the animation as {video_name}{video_ext}"
else:
    video_text = "no animation"
    vsa = ""

and_text = " and " if video_name is not None and image_name is not None else ""
if video_name is None and image_name is None:
    and_text = "absolutely nothing"
welcome_text = f"""Hello :)
I will make {image_text} and {video_text}.
I will save {isa}{and_text}{vsa}."""
welcome_text += "" if video_name is None else "\nThis might take a while."

if __name__ == '__main__':
    print(welcome_text)

    # image_name = my_argparse.image_name
    # video_name = my_argparse.video_name
    # image_ext = my_argparse.image_ext
    # video_ext = my_argparse.video_ext
    # years = my_argparse.years

    from my_plot import animation_make, image_make

    if image_name is not None:
        for year in years:
            image_make(year, f"{image_name}_{year}{image_ext}")

    if video_name is not None:
        anim = animation_make(years, f"{video_name}{video_ext}")