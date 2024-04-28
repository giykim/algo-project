import pandas as pd
import refinitiv.data as rd


def connect_refinitiv():
    exec(open("credentials.py").read(), globals())

    session = rd.session.platform.Definition(
        app_key=APP_KEY,
        grant=rd.session.platform.GrantPassword(
            username=RDP_LOGIN,
            password=RDP_PASSWORD
        ),
        signon_control=True
    ).get_session()
    session.open()
    rd.session.set_default(session)

    exec("del APP_KEY; del RDP_LOGIN; del RDP_PASSWORD", globals())

    return session


def refinitiv_data():
    df = rd.get_data(
        universe=["PLTR.K"],
        fields=[
            "TR.OPENPRICE",
            "TR.HIGHPRICE",
            "TR.LOWPRICE",
            "TR.CLOSEPRICE",
            "TR.PriceMoVolatilityDly",
            "TR.CLOSEPRICE.Date"
        ],
        parameters={
            'Curn': 'USD',
            'SDate': '2021-03-29',
            'EDate': '2024-03-28',
            'Frq': 'D'
        }
    )

    return df


def process_data(df):
    # Convert the 'TR.CLOSEPRICE.Date' column to datetime format
    df['Date'] = pd.to_datetime(df['Date'])

    # Set the date column as the index
    df.set_index('Date', inplace=True)

    # Resample the DataFrame to 2-week periods and calculate OHLC
    ohlc_df = df.resample('2W').agg({
        'Open Price': 'first',
        'High Price': 'max',
        'Low Price': 'min',
        'Close Price': 'last',
    }).dropna()

    ohlc_df.index = ohlc_df.index - pd.Timedelta(days=13)

    ohlc_df.reset_index(inplace=True)

    ohlc_df.to_csv("data/refinitiv_palantir_biweekly.csv", index=False)


session = connect_refinitiv()
refinitiv_df = refinitiv_data()
session.close()

# Process the DataFrame to get OHLC data for 2-week increments
process_data(refinitiv_df)