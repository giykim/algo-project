import warnings

import pandas as pd
from sklearn.linear_model import LinearRegression

from feature_vector_creator import feature_vector


def calc_price_change(df):
    target_df = pd.DataFrame()
    target_df["Date"] = df["Date"]
    target_df["Pos"] = (df["High Price"] - df["Open Price"]) / df["Open Price"] * 100
    target_df["Neg"] = (df["Low Price"] - df["Open Price"]) / df["Open Price"] * 100

    return target_df


def main():
    feature_df = feature_vector()
    target_df = calc_price_change(feature_df)

    interval_length = 26
    feature_col = ["Open Price", "war", "conflict", "united states"]
    warnings.filterwarnings("ignore",
                            message="X does not have valid feature names, but LinearRegression was fitted with feature names")
    for i in range(feature_df.shape[0]-interval_length-1):
        start = i
        end = i + interval_length + 1

        X_train = feature_df.iloc[start:end][feature_col]
        X_test = feature_df.iloc[end][feature_col].values.reshape(1, -1)
        y_train = target_df.iloc[start:end]["Pos"]
        y_test = target_df.iloc[end]["Pos"]

        model = LinearRegression()
        model.fit(X_train, y_train)
        print(f"Predicted: {model.predict(X_test)[0]}, Actual: {y_test}")


if __name__ == "__main__":
    main()

