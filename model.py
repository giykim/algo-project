import warnings

import pandas
import pandas as pd
from sklearn.linear_model import LogisticRegression


def get_predictions(feature_df: pandas.DataFrame,
                    target_df: pandas.DataFrame,
                    feature_col: list[str],
                    interval_length: int,
                    print_metrics: bool = True,
                    ) -> dict:
    warnings.filterwarnings(
        "ignore",
        message="X does not have valid feature names, but LogisticRegression was fitted with feature names"
    )

    n_classes = 2
    conf_matrix = [[0] * n_classes for _ in range(n_classes)]
    n_correct = 0
    n_cases = 0

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
        y_pred = model.predict(X_test)
        predictions[feature_df.iloc[end]['Date']] = (y_pred)

        y_test = int(y_test)
        y_pred = int(y_pred)
        conf_matrix[y_test][y_pred] += 1
        n_correct += (y_test == y_pred)
        n_cases += 1

    if print_metrics:
        print(f"conf matrix:\t{conf_matrix[0]}")
        for i in range(1, n_classes):
            print(f"\t\t{conf_matrix[i]}")
        print(f"accuracy:\t{n_correct / n_cases}")

    return predictions
