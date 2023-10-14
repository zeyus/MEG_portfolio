from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

def axis_seconds(ax):
    """
    Changes the x axis to seconds
    """
    ax.set_xticks(np.arange(0, 301, step=50), [-0.2, 0. , 0.2, 0.4, 0.6, 0.8, 1. ])

def plot_decoding_accuracy(acc, title, legend_title, savepath = None):
    fig, ax = plt.subplots(1, 1, figsize = (12, 8), dpi = 300)

    for subject in range(acc.shape[0]):
        ax.plot(acc[subject], linewidth = 1, alpha = 0.6, label = f"Subject {subject + 1}")

    # plot the average
    average = np.average(acc, axis = 0)
    ax.plot(average, linewidth = 2, color = "k")

    ax.set_title(title)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Accuracy")

    axis_seconds(ax)

    # vertical line at 0
    ax.axvline(x = 0+0.2*250, color = "k", linestyle = "--", linewidth = 1)

    # horizontal line at 0.5
    ax.axhline(y = 0.5, color = "k", linestyle = "--", linewidth = 1)

    # legend
    ax.legend(title = legend_title, loc = "upper right")

    # x limits
    ax.set_xlim(0, 300)

    if savepath:
        plt.savefig(savepath)
    plt.close()



if __name__ in "__main__":
    path = Path(__file__).parent
    results_path = Path("/work/807746/study_group_8") / "results" 
    outpath = Path("/work/807746/study_group_8") / "fig"
    
    trig_pairs = [(11, 12), (21, 22), (11, 21), (12, 22)]
    labels = [
        # 'bankssts',
        # 'caudalanteriorcingulate',
        # 'caudalmiddlefrontal',
        # 'cuneus',
        # 'entorhinal',
        # 'frontalpole',
        # 'fusiform',
        # 'inferiorparietal',
        # 'inferiortemporal',
        # 'insula',
        # 'isthmuscingulate',
        # 'lateraloccipital',
        # 'lateralorbitofrontal',
        # 'lingual',
        # 'medialorbitofrontal',

        # # ...
        # 'superiorfrontal-lh_superiorfrontal',
        # 'middletemporal',
        # 'paracentral',
        # 'parahippocampal',
        'parsopercularis',
        'parsorbitalis',
        'parstriangularis',
        'pericalcarine',
        'postcentral',
        'posteriorcingulate',
        'precentral',
        'precuneus',
        'rostralanteriorcingulate',
        'rostralmiddlefrontal',
        'superiorfrontal',
        'superiorparietal',
        'superiortemporal',
        'supramarginal',
        'temporalpole',
        'transversetemporal',
    ]
    #     "IMG/PS": 11,
    # "IMG/PO": 21,
    # "IMG/NS": 12,
    # "IMG/NO": 22,
    # "IMG/BI": 23,
    # "button_press": 202
    trig_names = {
        11: "Positive (self-selected)",
        21: "Positive (other-selected)",
        12: "Negative (self-selected)",
        22: "Negative (other-selected)",
        23: "Neutral (Button press)",
        202: "Button press event"
    }
    label_suffixes = ['-lh', '-rh']
    
    for lbl in labels:
        for lbl_suff in label_suffixes:
            if lbl == "superiorfrontal-lh_superiorfrontal" and lbl_suff == "-lh":
                continue
            label = lbl + lbl_suff
            for trig_1, trig_2 in trig_pairs:
                trig_1 = [trig_1]
                trig_2 = [trig_2]

                trig_1_str = '-'.join([str(elem) for elem in trig_1])
                trig_2_str = '-'.join([str(elem) for elem in trig_2])


                # create output directory if it doesn't exist
                if not outpath.exists():
                    outpath.mkdir()

                acc = np.load(results_path / f"across_subjects_{trig_1_str}_{trig_2_str}_{label}.npy")

                plot_decoding_accuracy(
                    acc, 
                    title = f"Decoding accuracy for {trig_names[trig_1[0]]} vs {trig_names[trig_2[0]]} (across subject)", 
                    legend_title = "Test subject",
                    savepath = outpath / f"across_subjects_{trig_1_str}_{trig_2_str}_{label}.png"
                    )


                within_subject = []
                for i in range(1, 9):
                    within_subject.append(np.load(results_path / f"within_subject_{i}_{trig_1_str}_{trig_2_str}_{label}.npy"))

                within_subject = np.mean(np.array(within_subject), axis = 2)
                
                plot_decoding_accuracy(
                    within_subject,
                    legend_title = "Subject",
                    title = f"Decoding accuracy for {trig_names[trig_1[0]]} vs {trig_names[trig_2[0]]} (within subject)", 
                    savepath = outpath / f"within_subjects_{trig_1_str}_{trig_2_str}_{label}.png"
                    )

    
