# The code for determining whether encountering a streak of s consecutive lines
# with a certain property (such as the absence of resolutions in iambic
# trimeter) is probable in a text with n lines total of which k lines have the
# said property.

import numpy as np
import scipy.special


def get_p(k, n, s):
    """
    Get probability of there being a sequence of s consecutive lines without resolutions in a text
    of k lines total of which n lines have no resolution
    :param k: Total number of lines
    :param n: Number of lines without resolution
    :param s: Length of the sequence for which to calculate the probability
    :return:  Desired probability
    """
    counts = np.zeros(shape=(n + 1, s), dtype=object)
    # counts[n][s] is the number of arrangements of n lines without resolutions among k total
    # lines such that the last s lines in a sequence are without resolutions and no s lines without
    # resolutions occur consequently. Initially, k=1
    counts[1][1] = 1
    counts[0][0] = 1
    for _ in range(k - 1):
        old_counts = counts
        counts = np.zeros(shape=(n + 1, s), dtype=object)
        counts[:, 0] = np.sum(old_counts, axis=1)
        counts[1:n+1, 1:s] = old_counts[0:n, 0:s-1]
    return 1 - np.sum(counts[n, :]) / scipy.special.comb(k, n, exact=True)
