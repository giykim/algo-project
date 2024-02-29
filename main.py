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
    pass


def main():
    session = connect_refinitiv()

    # refinitiv_df = refinitiv_data()

    session.close()


if __name__ == "__main__":
    main()

