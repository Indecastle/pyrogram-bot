import pyrogram

from controller import controllers, init_functions
import common
from settings_provider import conn, ensure_database

# from backgroundJob import backgroundJobMain

app = pyrogram.Client("my_account")


def main():
    ensure_database()

    with app:
        common.init_common(app)

        for init_func in init_functions:
            init_func(app)

    for controller in controllers:
        controller(app)

    app.run()


if __name__ == '__main__':
    # backgroundJobMain(app)
    main()
