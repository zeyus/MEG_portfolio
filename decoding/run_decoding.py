"""
X shape = (n_epochs, n_times, n_sources)
"""

from pathlib import Path
import numpy as np
from sklearn import svm
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

def read_data(data_path, subject, x_file="X.npy", y_file="y.npy"):
    """Read in data for a given subject.

    Parameters
    ----------
    data_path : str
        Path to the data directory.
    subject : str
        Subject ID.

    Returns
    -------
    X : array
        Data array.
    y : array
        Label array.
    """

    X = np.load(data_path / subject / x_file)
    y = np.load(data_path / subject / y_file)

    return X, y
    
def balance_class_weights(X, y):
    """
    Balances the class weight by removing trials so each class has the same number of trials as the class with the least trials.

    Parameters
    ----------
    X : array
        Data array with shape (n_trials, x, x)
    y : array
        Array with shape (n_trials, ) containing several classes

    Returns
    -------
    X_equal : array
        Data array with shape (n_trials, x, x) with equal number of trials for each class
    y_equal : array
        Array with shape (n_trials, ) containing classes with equal number of trials for each class

    """
    keys, counts = np.unique(y, return_counts = True)

    keep_inds = []

    for key in keys:
        index = np.where(np.array(y) == key)
        random_choices = np.random.choice(index[0], size = counts.min(), replace=False)
        keep_inds.extend(random_choices)
    
    X_equal = X[keep_inds, :, :]
    y_equal = y[keep_inds]

    return X_equal, y_equal


def across_subject(decoder, Xs, ys):
    """
    Run decoding across subjects.

    Parameters
    ----------
    decoder : sklearn estimator
        Decoder to use.
    Xs : array
        Data array.
    ys : array
        Label array.
    """
    N, T, S = Xs[0].shape
    results = np.array((len(Xs), T)) # number of subjects, number of time points

    for i in range(len(Xs)):
        X_tmp = Xs.copy()
        X_test = X_tmp.pop(i)

        y_tmp = ys.copy()
        y_test = y_tmp.pop(i)

        X_train = np.concatenate(X_tmp, axis=0)
        y_train = np.concatenate(y_tmp, axis=0)
        print(X_train.shape)

        # balance class weights
        X_train, y_train = balance_class_weights(X_train, y_train)

        for t in range(T):
            decoder.fit(X_train[:, t, :], y_train)
            results[i, t] = decoder.score(X_test[:, t, :], y_test)
    
    return results

def convert_y_triggers(y, zero = [], one = []):
    """
    Converts triggers to 0 and 1.

    Parameters
    ----------
    zero : list
        List of triggers to convert to 0.
    one : list
        List of triggers to convert to 1.
    
    Returns
    -------
    y : array
        Array with shape (n_trials, ) containing 0 and 1.
    """
    y_new = np.zeros(len(y))

    for i in range(len(y)):
        if y[i] in zero:
            y_new[i] = 0
        elif y[i] in one:
            y_new[i] = 1
        else:
            y_new[i] = np.nan
    
    return y_new



if __name__ in "__main__":

    path = Path(__file__).parent

    data_path = path.parent / "data"
    outpath = path / "results"

    # create output directory if it doesn't exist
    if not outpath.exists():
        outpath.mkdir()
    
    subjects = ["0108", "0109", "0110", "0111", "0112", "0113", "0114", "0115"]
    label = 'parsopercularis-lh'    

    # read in data for all subjects
    Xs = []
    ys = []

    for subject in subjects:
        X, y = read_data(data_path, subject, x_file=f"X_{label}.npy", y_file=f"y_{label}.npy")

        # only keep certain triggers
        triggerlist = np.array([11, 12])
        trigger_idx = np.where(np.isin(y, triggerlist))

        X = X[trigger_idx[0], :, :]
        y = y[trigger_idx[0]]

        # convert triggers to 0 and 1
        y = convert_y_triggers(y, zero = [11], one = [12])


        Xs.append(X)
        ys.append(y)

    # run decoding
    decoder = make_pipeline(StandardScaler(), svm.SVC(C=1, kernel='linear', gamma='auto'))
    results = across_subject(decoder, Xs, ys)

    # save results
    np.save(outpath / "across_subjects.npy", results)


    