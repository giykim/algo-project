import warnings

import pandas
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler


def get_predictions(feature_df: pandas.DataFrame,
                    target_df: pandas.DataFrame,
                    feature_col: list[str],
                    interval_length: int,
                    print_metrics: bool = False,
                    ):
    warnings.filterwarnings(
        "ignore",
        message="X does not have valid feature names, but LogisticRegression was fitted with feature names"
    )

    n_classes = 2
    conf_matrix = [[0] * n_classes for _ in range(n_classes)]
    n_cases = 0

    columns_to_exclude = ["Date"]
    columns_to_scale = feature_df.columns.difference(columns_to_exclude)

    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(feature_df[columns_to_scale])

    scaled_df = pd.DataFrame(scaled_features, columns=columns_to_scale, index=feature_df.index)
    feature_df = pd.concat([feature_df[columns_to_exclude], scaled_df], axis=1)

    predictions = {}
    for i in range(feature_df.shape[0] - interval_length - 1):
        start = i
        end = i + interval_length + 1

        X_train = feature_df.iloc[start:end][feature_col]
        X_test = feature_df.iloc[end][feature_col].values.reshape(1, -1)
        y_train = target_df.iloc[start:end]["Long"]
        y_test = target_df.iloc[end]["Long"]

        model = LogisticRegression(random_state=42)
        model.fit(X_train, y_train)
        y_prob = model.predict_proba(X_test)[:, 1]

        threshold = 0.5
        y_pred = (y_prob > threshold)[0]

        predictions[feature_df.iloc[end]['Date']] = (y_test, y_pred)

        y_test = int(y_test)
        y_pred = int(y_pred)
        conf_matrix[1-y_test][1-y_pred] += 1
        n_cases += 1

    TP = conf_matrix[0][0]
    TN = conf_matrix[1][1]
    FP = conf_matrix[1][0]
    FN = conf_matrix[0][1]

    accu = (TP + TN) / n_cases
    precision = TP / (TP + FP) if (TP + FP) > 0 else 0
    recall = TP / (TP + FN) if (TP + FN) > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    if print_metrics:
        print(f"Confusion Matrix:\t{conf_matrix[0]}")
        for i in range(1, n_classes):
            print(f"\t\t\t{conf_matrix[i]}")
        print(f"Accuracy:\t{accu}")
        print(f"F1-Score:\t{f1_score}")

    stats = {}
    stats["accu"] = accu
    stats["precision"] = precision
    stats["recall"] = recall
    stats["f1_score"] = f1_score
    stats["confusion_matrix"] = conf_matrix

    return predictions, stats
