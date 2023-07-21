from sklearn.metrics import accuracy_score, mean_absolute_error, mean_squared_error

from fairlearn.metrics import (
    MetricFrame,
    selection_rate,
    equalized_odds_difference,
    equalized_odds_ratio,
    demographic_parity_difference,
    demographic_parity_ratio,
    false_positive_rate,
    false_negative_rate,
    count,
    accuracy_score_ratio,
)
from fairlearn.reductions import (
    BoundedGroupLoss,
    ZeroOneLoss,
    DemographicParity,
    ErrorRate,
    GridSearch,
)

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib.cm as cm
from matplotlib.colors import Normalize
import matplotlib.patches as mpatches
import warnings


def score(
    _is_classification,
    y_true,
    y_pred,
):
    if _is_classification:
        return accuracy_score(y_true, y_pred)
    else:
        return mean_absolute_error(y_true, y_pred)


def calculate_metrics(
    is_classification,
    data,
    y_true,
    y_pred,
    group_test,
    sensitive_feature,
    fairness_metrics,
    visualize,
):
    if not is_classification:
        return show_regression_score(
            data,
            y_true,
            y_pred,
            group_test,
            sensitive_feature,
            fairness_metrics,
            visualize,
        )
    else:
        return show_classification_score(
            data,
            y_true,
            y_pred,
            group_test,
            sensitive_feature,
            fairness_metrics,
            visualize,
        )


def show_classification_score(
    data, y_true, y_pred, group_test, sensitive_feature, fairness_metrics, visualize
):
    metrics = {
        "accuracy": accuracy_score,
        "false positive rate": false_positive_rate,
        "false negative rate": false_negative_rate,
        "selection rate": selection_rate,
        "count": count,
    }

    fairness_dict = {
        "equalized_odds_difference": equalized_odds_difference,
        "demographic_parity_difference": demographic_parity_difference,
        "equalized_odds_ratio": equalized_odds_ratio,
        "demographic_parity_ratio": demographic_parity_ratio,
    }

    if fairness_metrics is None:
        fairness_metrics = fairness_dict.keys()

    mf = MetricFrame(
        metrics=metrics, y_true=y_true, y_pred=y_pred, sensitive_features=group_test
    )
    res = mf.by_group

    _encoder = data._encoder_mapping[sensitive_feature]

    ix = np.asarray(res.index.astype(int).tolist())
    res.index = _encoder.inverse_transform(ix.reshape(-1, 1))

    if visualize:
        plot_accuracy_metrics(res)

    results = (res,)

    if visualize:
        fig = plt.figure(figsize=(12, 9))

    res_summary = {}
    for num, fm in enumerate(fairness_metrics):
        is_diff = False
        _metrics = fairness_dict[fm]

        if "diff" in fm:
            is_diff = True
            thre = 0.25
        else:
            thre = 0.8

        val = _metrics(y_true, y_pred, sensitive_features=group_test)
        val = round(val, 2)
        sum_text = get_text(fm, val, thre, is_diff)

        if visualize:
            try:
                ax = fig.add_subplot(2, 2, num + 1)
                ax.set_title(fm)

                plot_diff(fig, ax, val, thre, fm, sum_text, is_diff)
                fig.tight_layout(pad=4)
            except Exception as ex:
                warnings.warn(f"Visualization cannot be completed. {ex}")

        text_summary = " ".join(sum_text)
        res_summary[fm] = (val, text_summary)

    results = results + (res_summary,)

    return results


def show_regression_score(
    _data,
    y_true,
    y_pred,
    group_test,
    sensitive_feature,
    fairness_metrics,
    visualize=False,
):
    if fairness_metrics is None:
        fairness_metrics = "mean_absolute_error"

    mae_frame = MetricFrame(
        metrics=mean_absolute_error,
        y_true=y_true,
        y_pred=y_pred,
        sensitive_features=group_test,
    )

    if visualize:
        _encoder = _data._encoder_mapping[sensitive_feature]

        res_idx = mae_frame.by_group.index
        ix = np.asarray(res_idx.astype(int).tolist()).reshape(-1, 1)
        labels = np.unique(_encoder.inverse_transform(ix)).tolist()

        plot_regression_metrics(
            mae_frame.by_group, labels, fairness_metrics, sensitive_feature
        )

    return mae_frame.by_group


def plot_regression_metrics(res, xlabels, metric_name, _sensitive_feature):
    fig, ax = plt.subplots()

    ax.bar(res.index, res.values, align="center", tick_label=xlabels)

    ax.set_facecolor("blanchedalmond")
    ax.set_alpha(0.7)
    plt.xticks(rotation=45)

    ax.set_xlabel(_sensitive_feature)
    ax.set_ylabel(metric_name)

    plt.show()


def plot_accuracy_metrics(res):
    _sum = res["count"].sum()

    res["count"] = res["count"].apply(lambda x: x / _sum)
    ax = res.plot(kind="bar", figsize=(6.4, 3.5))
    ax.axhspan(0, 1, facecolor="blanchedalmond", alpha=0.15)

    plt.legend(bbox_to_anchor=(1.05, 1.0), loc="upper left")
    plt.tight_layout()
    plt.show()


def get_text(fm, val, thre, is_diff):
    texts = [f"The value of {fm} is {val}"]
    if val > thre:
        texts.append(f"which is more than minimum threshold {thre}.")
    else:
        texts.append(f"which is less than minimum threshold {thre}.")

    if is_diff:
        texts.append("The ideal value of this metric is 0.")
        texts.append(f"Fairness for this metric is between 0 and {thre}.")
    else:
        texts.append("The ideal value of this metric is 1.")
        texts.append(f"Fairness for this metric is between {thre} and 1.")
    return texts


def plot_diff(fig, ax, val, thre, label, summary, is_diff):
    text_summary = "\n".join(summary)

    ax.axhspan(-1, 1, facecolor="blanchedalmond", alpha=0.15)

    red_patch = mpatches.Patch(color="darksalmon", label="Biased")
    green_patch = mpatches.Patch(color="paleturquoise", label="Fair")

    if is_diff:
        ax.set_ylim(-1, 1)

        thre = 0.25
        if val > thre:
            ax.bar(
                [1, 2],
                [0, val],
                width=0.35,
                tick_label=["", label],
                color=("darksalmon"),
            )
        else:
            ax.bar(
                [1, 2],
                [0, val],
                width=0.35,
                tick_label=["", label],
                color=("paleturquoise"),
            )

        plt.axhline(y=0, color="grey", linestyle="-")
        plt.axhline(y=thre, color="grey", linestyle="--")
        plt.axhline(y=-thre, color="grey", linestyle="--")

        plt.text(2.72, 0, "Fair", fontsize=10)
        plt.text(2.72, thre, "Bias", fontsize=10)
        plt.text(2.72, -thre, "Bias", fontsize=10)

        ax.annotate(
            "",
            xy=(1.15, 0.30),
            xycoords="axes fraction",
            xytext=(1.15, 0.70),
            arrowprops=dict(arrowstyle="<->", color="black"),
        )

        text_widget = ax.text(
            1, -1.6, text_summary, fontsize=12, color="black", ha="left", va="bottom"
        )
        text_widget.set_fontstyle("italic")

        plt.legend(handles=[red_patch, green_patch], loc="upper left")

    else:
        ax.set_ylim(0, 1)

        thre = 0.8

        if val < thre:
            ax.bar(
                [1, 2],
                [0, val],
                width=0.35,
                tick_label=["", label],
                color=("darksalmon"),
            )
        else:
            ax.bar(
                [1, 2],
                [0, val],
                width=0.35,
                tick_label=["", label],
                color=("paleturquoise"),
            )

        plt.axhline(y=0, color="grey", linestyle="-")
        plt.axhline(y=thre, color="grey", linestyle="--")

        plt.text(2.72, 0, "Bias", fontsize=10)
        plt.text(2.72, thre, "Fair", fontsize=10)

        ax.annotate(
            "",
            xy=(1.15, 0.30),
            xycoords="axes fraction",
            xytext=(1.15, 0.70),
            arrowprops=dict(arrowstyle="<-", color="black"),
        )

        text_widget = ax.text(
            1, -0.4, text_summary, fontsize=12, color="black", ha="left", va="bottom"
        )
        text_widget.set_fontstyle("italic")

        plt.legend(handles=[red_patch, green_patch], loc="lower left")

    ax.set_xlim(1, 2.7)
    ax.set_xticks([])
