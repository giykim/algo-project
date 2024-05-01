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
                    use_bad_trades_model: bool = False
                    ):
    warnings.filterwarnings(
        "ignore",
        message="X does not have valid feature names, but LogisticRegression was fitted with feature names"
    )

    n_classes = 2
    conf_matrix_long = [[0] * n_classes for _ in range(n_classes)]
    conf_matrix_badTrade = [[0] * n_classes for _ in range(n_classes)]
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
        y_train_long = target_df.iloc[start:end]["Long"]
        y_test_long = target_df.iloc[end]["Long"]

        # Model for predicting 'long'
        model_long = LogisticRegression(random_state=42)
        model_long.fit(X_train, y_train_long)
        y_pred_long = (model_long.predict_proba(X_test)[:, 1] > 0.5)[0]

        final_pred = y_pred_long  # default to the prediction of the 'long' model

        if use_bad_trades_model and "badTrade" in target_df.columns:
            y_train_badTrade = target_df.iloc[start:end]["badTrade"]
            if y_train_badTrade.sum() > 0:  # Check if there are any bad trades in the training data
                # Model for predicting 'badTrade'
                model_badTrade = LogisticRegression(random_state=42)
                model_badTrade.fit(X_train, y_train_badTrade)
                y_pred_badTrade = (model_badTrade.predict_proba(X_test)[:, 1] > 0.5)[0]

                # Combine predictions: only count as '1' if long is '1' and badTrade is '0'
                final_pred = int(y_pred_long and not y_pred_badTrade)

        predictions[feature_df.iloc[end]['Date']] = (y_test_long, final_pred)

        # Update confusion matrix for 'long'
        y_test_long = int(y_test_long)
        conf_matrix_long[1-y_test_long][1-int(final_pred)] += 1
        n_cases += 1

    # Calculate and print metrics for 'long'
    def calculate_metrics(conf_matrix):
        TP = conf_matrix[0][0]
        TN = conf_matrix[1][1]
        FP = conf_matrix[1][0]
        FN = conf_matrix[0][1]
        accu = (TP + TN) / n_cases
        precision = TP / (TP + FP) if (TP + FP) > 0 else 0
        recall = TP / (TP + FN) if (TP + FN) > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        return {
            "accuracy": accu,
            "precision": precision,
            "recall": recall,
            "f1_score": f1_score,
            "confusion_matrix": conf_matrix
        }

    stats_long = calculate_metrics(conf_matrix_long)

    if print_metrics:
        print(f"Metrics for 'long':")
        print(f"Accuracy: {stats_long['accuracy']}")
        print(f"F1-Score: {stats_long['f1_score']}")
        print(f"Confusion Matrix: {stats_long['confusion_matrix']}")

    return predictions, stats_long
