import pandas as pd
import refinitiv.data as rd
import refinitiv.dataplatform as rdp


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
            'SDate': '1D'
        }
    )

    return df


def main():
    session = connect_refinitiv()

    refinitiv_df = refinitiv_data()
    print(refinitiv_df)

    session.close()


if __name__ == "__main__":
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    main()

