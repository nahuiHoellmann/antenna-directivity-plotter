import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from math import log10
from math import pi


def convert_dB(val):

    """
    Convert val do dezibel
    -------
    float
        20 * log10(val)
    """
    return 20 * log10(val)


def lock_phi(df, deg):

    """
    Get the subslice of a DataFrame for a specific phi

    Parameters
    ----------
    deg : int
        The degree at which phi is to be locked
    df : DataFrame
        The simulation data of the Antenna
    Returns
    -------
    DataFrame
        Sorted rows where phi == deg
    """

    return df.iloc[range(deg, 65341 + deg, 361)]


def lock_theta(df, deg):

    """
    Get the subslice of a DataFrame for a specific theta

    Parameters
    ----------
    deg : int
        The degree at which theta is to be locked
    df : DataFrame
        The simulation data of the Antenna
    Returns
    -------
    DataFrame
        Sorted rows where theta == deg
    """

    return df[deg*360 + deg: (deg + 1) * 360 + deg + 1]


def data_points(io, *, lock, polarization=['E-Theta', 'E-Phi'], freq=None):

    """
    The absolute values for one or both polarizations when phi or theta are locked at a specific angle

    Parameters
    ----------
    io : DataFrame or file_like or str(filename)
        Where to read data from
    lock : ({'Phi','Theta'}, int)
        keyword only!
        Which variable to lock and which degree to lock it at
    polarization: array of {'E-Theta', 'E-Phi'} default: ['E-Theta', 'E-Phi']
        Which Values to return
    freq:
        The frequency to plot for
        When using an exel as io this is also the sheet name
        When usinh an df as io this is only needed to label the plot
    Returns
    -------
    (datavalues, degrees): tuple of np.array
        The Values for one polarization at a specific degree
    (data_pol_1, data_pol_1, degrees): tuple of np.array
        The Values for both polarizations in the order specified by polarization
    """

    if isinstance(io, pd.DataFrame):
        dff = io
    else:
        dff = pd.read_excel(io, sheet_name=freq)

    lock_var, deg = lock
    lock_function, plot_var = {
        'Phi': (lock_phi, 'Theta'),
        'Theta': (lock_theta, 'Phi')
    }[lock_var]

    df = lock_function(dff, deg)

    abs_values = []

    for pol in polarization:
        pol_specific_values = [np.absolute(re + im*1j) for re, im in zip(df[f'{pol} Re'], df[f'{pol} Im'])]
        print(type(pol_specific_values))
        abs_values.append(pol_specific_values)

    abs_values.append(df[plot_var].to_numpy())

    return tuple(abs_values)


class Plotter:

    @staticmethod
    def io_plot(io, *, lock, polarization=['E-Theta', 'E-Phi'], freq=None, db=True, ax=None):

        """
        Plot antenna data which is extracted of an excel or DataFrame first
            see Plotter.plot()
            and data_points()
            for more details

        Parameters
        ----------
            io : DataFrame or file_like or str(filename)
        Where to read data from
        lock : ({'Phi','Theta'}, int)
            keyword only!
            Which variable to lock and which degree to lock it at
        polarization: array of {'E-Theta', 'E-Phi'} default: ['E-Theta', 'E-Phi']
            Which Values to return
        freq:
            The frequency to plot for
        db: bool
            Wether the values should be converted to dB first, default is True
        ax: matplotlib.axes.Axes, optional
            The ax to draw to, if one is specified the caller is responsible to call ax.show() or the equivalent after
            the funtion call is complete
        Returns
        -------
        matplotlib.axes.Axes
            The ax where the plot was drawn to
        """

        lock_var, lock_deg = lock
        plot_var = 'Phi' if lock_var == 'Theta' else 'Theta'

        title = f'{plot_var}(deg)'

        if not freq:
            freq = '?'

        def lable(pol):
            return f'{lock_var} = {lock_deg} deg | Polarisation = {pol} | Frequency = {freq}'

        if len(polarization) == 1:

            var1, deg = data_points(io, lock=lock, polarization=polarization, freq=freq)
            Plotter.plot(
                [(var1, deg)],
                title,
                label=[
                       lable(polarization[0])
                      ],
                db=db,
                ax=ax
            )

        else:

            var1, var2, deg = data_points(io, lock=lock, polarization=polarization, freq=freq)
            Plotter.plot(
                [(var1, deg), (var2, deg)],
                title,
                label=[
                       lable(polarization[0]),
                       lable(polarization[1])
                      ],
                db=db,
                ax=ax
            )

    @staticmethod
    def plot(data, title=None, label=["", ""], db=True, ax=None):

        """
        A wraper around matplotlib.pyplot to reduce overhead when plotting polar graphs of antenna directivity

        Parameters
        ----------
        data : array of tuple(np.array, np.array)
            The Datapoints to plot where the the first value is val(deg) and the second value is deg
        title: str, optional
            The title for the graph
        label: array(str), optional
            The lable for the data were lable[x] is the lable for data[x]
            To omit the lable, put in an empty string
        db: bool
            Wether the values should be converted to db first, default is True
        ax: matplotlib.axes.Axes, optional
            The ax to draw to, if one is specified the caller is responsible
            to make the canvas redraw after the function call ended
        Returns
        -------
        matplotlib.axes.Axes
            The ax where the plot was drawn to
        """

        if not ax:
            ax = ax = plt.subplot(111, projection='polar')
        else:
            ax.clear()

        for d, l in zip(data, label):
            var, deg = d
            rad = [d * pi / 180 for d in deg]
            if db:
                var = list(map(convert_dB, var))
            if label:
                ax.plot(rad, var, label=l)
            else:
                ax.plot(rad, var)

        ax.set_rlabel_position(22.5)  # get radial labels away from plotted line
        ax.grid(True)
        ax.legend(loc='lower left', bbox_to_anchor=(-0.2, -0.15, 1, 1), ncol=2)

        if title:
            ax.set_title(title)
