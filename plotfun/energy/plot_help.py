# -*- coding: utf-8 -*-
"""
Created on Wed Aug  4 01:41:31 2021

@author: Offszanka

Implements grid_plot which helps to create a GridLayout in pyplot.

TODO: Add start_delay and end_delay
"""
import os
import warnings
from collections.abc import Iterable

import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import matplotlib.animation as animation

import numpy as np

def _detect_rect(table):
    """
    Detects the rectangle which is indicated by true values.
    The area has to be convex.
    If the are true values outside of the rectangle or the rectangle is not
    convex then False is returned.

    If the rectangle is valid then the coordinates of the upper left and
    bottom right points of the rectangle is returned.

    Parameters
    ----------
    table : 2 -dim np.ndarray filled with bool values
        The table which contains a rectangle described of true values.

    Returns
    -------
    upper_left : point, ndarray with 2 elements
        DESCRIPTION.
    bottom_right : point, ndarray with 2 elements
        DESCRIPTION.

    """

    trues = np.vstack(np.where(table))
    upper_left = trues[:,np.linalg.norm(trues, axis=0).argmin()]
    bottom_right = trues[:,np.linalg.norm(trues, axis=0).argmax()]

    ## Check if the rectangle is valid.
    # Check if all true values are in the rectangle.
    for i in (0,1):
        min_, max_ = upper_left[i], bottom_right[i]
        if not np.all((min_ <= trues[i,:]) & (trues[i,:] <= max_)):
            return False

    # Check if in the rectangle are only true values.
    # That is, in the rectangle we have so much cells as in the calculation below.
    # trues.shape[1] indicate how much true values are found.
    if not trues.shape[1] == (upper_left[0]-(bottom_right[0]+1)) * \
                            (upper_left[1]-(bottom_right[1]+1)):
        return False

    return upper_left, bottom_right

def grid_plot(table, fig, name_book = None, **kwargs):
    """
    Helps to make a pyplot-plot with GridSpec.
    Adds subplots according to the structure of table.
    The table has to be a 2-dim np.ndarray with dtype int
    divided into convex rectangle consisting
    of the same numbers.

    Returns a dictionary with the axes as values

    Parameters
    ----------
    table : 2-dimensional np.ndarray with dtype=np.int
        The table which specifies the grid layout.
    fig : pyplot figure
        The figure which will contain the axes of the GridLayout.
    name_book : dictionary, optional
        If given the keys of the returned dictionary are renamed according
        to the numbers. Note that all numbers have to exist in the dictionary.
        The default is None.

    **kwargs : TYPE
        Additional parameters passed to the GridSpec constructor.

    Raises
    ------
    ValueError
        If a rectangle is not valid.

    Returns
    -------
    ax_d : dictionary
        The dictionary filled with the axes. The keys are build as ax{k} or
        according to name_book.

    Examples
    --------
    >>> table = np.asarray([1,1,2,1,1,2,1,1,3]).reshape(3,3)

    >>> table
    array([[1, 1, 2],
           [1, 1, 2],
           [1, 1, 3]])

    >>> fig = plt.figure()

    >>> grid_plot(table, fig)
    {'ax_1': <AxesSubplot:>, 'ax_2': <AxesSubplot:>, 'ax_3': <AxesSubplot:>}

    >>> grid_plot(table, fig, names={1 : 'left', 2 : 'right_upper', 3 : 'right_bottom'})
    {'left': <AxesSubplot:>,
     'right_upper': <AxesSubplot:>,
     'right_bottom': <AxesSubplot:>}
    """

    gs = GridSpec(*table.shape, figure=fig, **kwargs)

    ax_d = dict()

    numbers = np.unique(table)
    # Check if the custom dictionary contains all keys.
    # If not a KeyError will be returned.
    if name_book is not None:
        # Convert the book to have integers as keys.
        # This will raise an error if not possible.
        name_book = {int(key) : name_book[key] for key in name_book}

        # Check whether all numbers of the table are keys of name_book.
        if len(set(numbers) - name_book.keys()) > 0:
            raise ValueError(f'None of {set(numbers) - name_book.keys()} are in name_book.')

        # [name_book[num] for num in numbers]

    for j in numbers:
        points = _detect_rect(table == j)
        if points is None:
            raise ValueError(f'No proper rectangle for j={j} found.')

        ul, br = points
        ul0, ul1 = ul
        br0, br1 = br

        # plus one is needed because the points include the last element
        # but the last element of slice is ignored.
        axes = fig.add_subplot(gs[slice(ul0, br0+1), slice(ul1, br1+1)])
        if name_book is not None:
            ax_d[name_book[j]] = axes
        else:
            ax_d[f'{j}'] = axes

    return ax_d

class GridPlot:
    """A wrapper to help to plot frames and animations. For an example
    see my_plot.py."""

    def __init__(self, table, plot_functions, name_book = None,*,
                 fig_kwargs = None, grid_kwargs = None):
        """
        A wrapper to help to plot frames and animations.

        Parameters
        ----------
        table : np.ndarray, 2-dimensional. A list with 2-dim arrays is possible.
            The table specifying the grid layout.
            If table is a li st then grid_kwargs has to be has to be a list
            with dictionaries as entries.
            Note that the numbers of the whole array have to still be unique
            and each number needs to have a corresponding plot_function.

            The dimension is handled like this:
            (x-dimension, y-dimension).
        plot_functions : dictionary like object with callables as values.
            This functions are called when plot_frame or plot_animation are
            called. They must have the signature:
                func(ax, val, **kwargs)
                where ax  is the corresponding axes and val the value to
                customize the data. ... are
        name_book : dictionary like, optional
            Connects the numbers to the functions. Use this to stay safe where
            the plot_functions will be used. The default behaviour is to connect
            them by the order plot_functions.keys() gives.
            keys have to be the numbers and values have to be identical the
            keys of plot_functions.
        fig_kwargs : TYPE, optional
            Arguments passed to plt.figure. The default is empty set.
        grid_kwargs : dictionary or list with dictionaries as entries, optional.
            Arguments passed to the constructor of GridSpec.
            If table is a list then it has to be a list which specifies
            the arguments for each table. It has to be explicitly given then.
            The default is an empty set.

        Returns
        -------
        None.

        """
        if name_book is not None and 'fig' in name_book.values():
            raise ValueError('Do not use "fig" as a value in name_book.')

        calls_f = {f for f in plot_functions if not callable(plot_functions[f])}
        if len(calls_f) > 0:
            raise ValueError(f'The objects specified by {calls_f} are not callable.')

        self.plot_functions = plot_functions

        if fig_kwargs is None:
            fig_kwargs = {}

        fig = plt.figure(**fig_kwargs)

        numbers = np.unique(table)
        if name_book is None:
            name_book = {j : key for j,key in zip(numbers, plot_functions)}
        else:
            # Check if the values of name_book are identical to the keys of plot_functions
            s1 = set(name_book.values())
            s2 = set(plot_functions.keys())
            if len(s1 - s2) > 0:
                raise ValueError(f'{s1-s2} is not represented correctly.')

        if type(table) == list:
            self.grid = dict()
            if grid_kwargs is None:
                grid_kwargs = [{}]*len(table)
            for tab, gkw in zip(table, grid_kwargs):
                self.grid.update(grid_plot(tab, fig, name_book, **gkw))
        else:
            if grid_kwargs is None:
                grid_kwargs = {}
            self.grid = grid_plot(table, fig, name_book, **grid_kwargs)
        self.grid['fig'] = fig

    def __getitem__(self, key):
        return self.grid[key]

    def plot_frame(self, val, func_args = None, to_save=False,
                   save_path='image.png'):
        """
        Plots a frame by calling all saved functions.

        Parameters
        ----------
        val :
            The value which is passed to all functions.
        func_args : dictionary like object, optional
            Additional parameters passed to the functions.
            The key corresponds to the function. The default is None.

        Returns
        -------
        The returns of the functions if at least one is returning something.

        """
        if func_args is None:
            func_args = {}

        return_dict = {}

        for kf in self.plot_functions:
            return_dict[kf] = self.plot_functions[kf](self.grid[kf], val,
                                                  **func_args.get(kf, {}))

        if to_save:
            plt.savefig(save_path)

        # Check if something was returned (i.e. not None)
        # If so then return only the not None returns.
        # Maybe return everything?
        if len([v for v in return_dict.values() if v is not None]) > 0:
            return {k : return_dict[k] for k in return_dict
                    if return_dict[k] is not None}

    def _anim_update(self, val, fargs):
        """Simple animation update which only calls all saved functions."""

        if fargs is None:
            fargs = {}
        for kf in self.plot_functions:
            self.plot_functions[kf](self.grid[kf], val, **fargs.get(kf, {}))

    def plot_animation(self, frames, *,
                       anim_update = None, interval = 100,
                       init_func = None,
                       to_save = False, save_path = 'video.mp4',
                       writer_args = None, fargs = None):
        """
        Plots the animation based on the saved functions.

        Parameters
        ----------
        frames : iterator like object
            Iterator which has to return the arguments which are passed to
            the saved functions (val).
        anim_update : TYPE, optional
            Updater function. Needs to have the signature:
                func(val, obj, fargs)
                where val is the iterated value, obj will be self and fargs
                are the arguments passed to the functions.
                The default is None.
        interval : int, optional
            interval at which the images are plotted. Passed to constructor of
            FuncAnimation. The default is 100.
        init_func : callable, optional
            init_func passed to FuncAnimation
        to_save : bool, optional
            Should the animation be saved? The default is False.
        save_path : string, optional
            path at which the file is saved. Ignored if save_path = False.
            The default is 'video.mp4'.
        writer_args : dictionary, optional
            Arguments passed to the writer object. The default is None.
        fargs : dictionary, optional
            Arguments passed to the saved functions. Has to be a dictionary where
            the keys are the names of the functions.
            The default is None.

        Returns
        -------
        anim : TYPE
            DESCRIPTION.

        """
        # ??? Is there a way to get the current style?
        # and how to apply style only in one animation
        if anim_update is None:
            anim_update = self._anim_update
            args_ = fargs
        elif fargs is None:
            args_ = (self,None)
        else: 
            args_ = (self, *fargs)

        anim = animation.FuncAnimation(self.grid['fig'], anim_update,
                                       frames = frames,
                                       repeat=False, interval=interval, blit=False,
                                       init_func=init_func,
                                       fargs = args_)

        if to_save:
            t,ext = os.path.splitext(save_path)
            if not ext in ('.mp4', '.gif'):
                warnings.warn('Other extenctions than .mp4 or .gif are not available'\
                              ' yet. .mp4 is added.')
                save_path = save_path + '.mp4'

            if ext == '.mp4':
                Anim_Writer = animation.writers['ffmpeg']
            elif ext == '.gif':
                Anim_Writer = animation.PillowWriter()
                anim.save(save_path, writer=Anim_Writer)
                return anim

            if writer_args is None:
                writer_args = {}

            # writer_ffmpeg = Anim_Writer(fps=12, metadata=dict(artist='Me'), bitrate=1800)
            writer_ffmpeg = Anim_Writer(**writer_args)

            anim.save(save_path, writer=writer_ffmpeg)
        return anim


def make_annotations(wedges, ax, names,*,
                     divisor = 2, horizontalalignment = None,
                     calc_xy = None, c_style = None,
                     annotation_args = None):
    """Create annotations to pie chart wedges
    From: https://matplotlib.org/stable/gallery/pie_and_polar_charts/pie_and_donut_labels.html#sphx-glr-gallery-pie-and-polar-charts-pie-and-donut-labels-py


    Parameters
    ----------
    wedges : list-type or iterable in other ways.
        List of wedges of a pie chart.
    ax : TYPE
        Axes of a figure. Here, the annotation box is plotted
    names : iterable of strings(-like)
        This will be in the annotation boxes.
    divisor : TYPE, optional
        DESCRIPTION. The default is 2.
    horizontalalignment : TYPE, optional
        DESCRIPTION. The default is None.
    calc_xy : TYPE, optional
        DESCRIPTION. The default is None.
    c_style : TYPE, optional
        DESCRIPTION. The default is None.
    annotation_args : dictionary, optional
        Arguments passed to annotation. Note that if given all arguments
        have to be passed. connectionstyle will always be updated depending on
        c_style.
        The default is None.
    Returns
    -------
    None.

    """

    if not isinstance(wedges, Iterable):
        wedges = [wedges]

    if annotation_args is None:
        facecolor = plt.rcParams['figure.facecolor']
        edgecolor = plt.rcParams['text.color']
        bbox_props = dict(boxstyle="square,pad=0.3",
                          fc=facecolor,
                          ec=edgecolor,
                          lw=0.72)
        annotation_args = dict(arrowprops=dict(arrowstyle="-"),
                  bbox=bbox_props, zorder=0, va="center")

    for i, (wedge, cnt_name) in enumerate(zip(wedges, names)):
        ang = (wedge.theta2 - wedge.theta1)/divisor + wedge.theta1
        y = np.sin(np.deg2rad(ang))
        x = np.cos(np.deg2rad(ang))

        if horizontalalignment is None:
            horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]

        if c_style is None:
            connectionstyle = "angle,angleA=0,angleB={}".format(ang)
        else:
            connectionstyle = c_style(wedge)
        # connectionstyle = "arc3,rad=0." # Schau hier: https://matplotlib.org/stable/gallery/userdemo/connectionstyle_demo.html
        annotation_args["arrowprops"].update({"connectionstyle": connectionstyle})

        if not callable(calc_xy):
            x_loc, y_loc = (1.35*np.sign(x), 1.4*y)
        else:
            x_loc, y_loc = calc_xy(x,y)
        ax.annotate(cnt_name, xy=(x, y), xytext=(x_loc, y_loc),
                    horizontalalignment=horizontalalignment, **annotation_args)

