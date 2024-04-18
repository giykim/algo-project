import warnings

import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import LogisticRegression

from feature_vector_creator import feature_vector
from dash_app import dash_app


def calc_price_change(df):
    target_df = pd.DataFrame()
    target_df["Date"] = df["Date"]
    target_df["Long"] = (df["High Price"] - df["Open Price"]) / df["Open Price"] > 0.03
    target_df["Short"] = (df["Low Price"] - df["Open Price"]) / df["Open Price"] < -0.03

    return target_df


def main():
    feature_df = feature_vector()
    print(feature_df.columns)
    feature_df = feature_df.dropna()
    target_df = calc_price_change(feature_df)
    print(feature_df)
    interval_length = 26
    feature_col = ["Open Price", "war", "conflict", "united states", "Count", "FEDFUNDS"]
    warnings.filterwarnings(
        "ignore",
        message="X does not have valid feature names, but LogisticRegression was fitted with feature names"
    )

    n_classes = 2
    conf_matrix = [[0] * n_classes for _ in range(n_classes)]
    n_correct = 0
    n_cases = 0

    orders = []

    for i in range(feature_df.shape[0]-interval_length-1):
        start = i
        end = i + interval_length + 1

        X_train = feature_df.iloc[start:end][feature_col]
        X_test = feature_df.iloc[end][feature_col].values.reshape(1, -1)
        y_train = target_df.iloc[start:end]["Long"]
        y_test = target_df.iloc[end]["Long"]

        # model = LinearRegression()
        model = LogisticRegression(random_state=42)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)[0]
        print(f"Predicted: {y_pred}, Actual: {y_test}")

        y_test = int(y_test)
        y_pred = int(y_pred)
        conf_matrix[y_test][y_pred] += 1
        n_correct += (y_test == y_pred)
        n_cases += 1

        if y_test == y_pred:
            orders.append(feature_df.iloc[start]["Date"])

    print(f"conf matrix:\t{conf_matrix[0]}")
    for i in range(1, n_classes):
        print(f"\t\t{conf_matrix[i]}")
    print(f"accuracy:\t{n_correct / n_cases}")

    # TODO: Visualization
    dash_app(feature_df)

    # TODO: Get rid of bad trades


if __name__ == "__main__":
    main()

