__author__ = 'eczech'

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import matplotlib


def get_histograms(data, target, sentinels=None, bins=5):
    cols = [col for col in data if col != target]

    if sentinels is None:
        sentinels = {}

    placeholders = sentinels.values() + ['nan']

    def is_numeric(x):
        return x not in placeholders and np.isfinite(x)

    data = data.applymap(lambda x: 'nan' if np.isnan(x) else sentinels.get(x, x))

    def cut(x):
        x = x.order()
        x_mask = x.apply(is_numeric)
        q = pd.cut(x.loc[x_mask], bins, retbins=True, include_lowest=True, right=True)
        x_cut = pd.cut(x, q[1], labels=[i for i in range(bins)], include_lowest=True, right=True)
        x_cut = x.where(~x_mask, x_cut)
        return {'values': x_cut, 'levels': q[0]}

    res = {}
    target_bins = cut(data[target])
    for col in cols:
        col_bins = cut(data[col])
        r = pd.DataFrame({col: col_bins['values'], target: target_bins['values']},  index=np.arange(0, len(data[col])))
        unique_col = r[col].unique()
        unique_tgt = r[target].unique()

        r = r.groupby([target, col]).size().unstack()
        bin_set = np.array(range(bins), dtype=np.float)

        for i in np.setdiff1d(bin_set, unique_tgt):
            r.loc[i, :] = np.nan
        for i in np.setdiff1d(bin_set, unique_col):
            r.loc[:, i] = np.nan
        for i in [0, 1]:
            r.sort_index(axis=i, inplace=True)

        cols = [col_bins['levels'].levels[int(x)] if x in bin_set else x for x in r.columns]
        r.columns = pd.Index(cols, name=r.columns.name)
        rows = [target_bins['levels'].levels[int(x)] if x in bin_set else x for x in r.index]
        r.index = pd.Index(rows, name=r.index.name)

        res[col] = r
    return res


def plot_histograms(hists, cnorm=None, cmap=matplotlib.cm.GnBu_r, transform=None):
    """ Plots histogram results returned from self.get_histograms method
    :param hists: Dictionary returned from self.get_histograms
    :param cnorm: Color scale; commonly one of matplotlib.colors.{LogNorm, SymLogNorm}
    :param cmap: Colormap used in heatmap color scheme
    :param transform: Transformation to be applied to each histogram count value
    :return: List of tuples containing matplotlib objects for each heatmap plot;
            each tuple has the form: (figure, plotaxis, coloraxis)
    """
    res = []
    for col in hists:
        d = hists[col]

        if transform is not None:
            d = transform(d)

        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_title(d.columns.name+' vs '+d.index.name)

        cax = ax.matshow(d, interpolation='nearest', norm=cnorm, cmap=cmap)
        fig.colorbar(cax, shrink=.7)

        ax.set_xticks(np.arange(len(d.columns)))
        ax.set_xticklabels(map(str, d.columns), rotation=16, rotation_mode="anchor")
        ax.set_xlabel(d.columns.name)

        ax.set_yticklabels(map(str, d.index))
        ax.set_yticks(np.arange(len(d.index)))
        ax.set_ylabel(d.index.name)

        fig.set_size_inches((10, 10))

        res.append((fig, ax, cax))
    return res