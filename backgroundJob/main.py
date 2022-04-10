import asyncio

import pyrogram
import aioschedule
import time
import functools
import random

from pyrogram import Client

import common
from backgroundJob.post_commets.main import post_comments_main


# декоратор для ловли исключений
from services.mats_service import mat_stat_notify, mat_stat_show_all
from settings_provider import ensure_database, mat_stat_reset, get_setting_value_async


def catch_exceptions(cancel_on_failure=False):
    def catch_exceptions_decorator(job_func):
        @functools.wraps(job_func)
        def wrapper(*args, **kwargs):
            try:
                return job_func(*args, **kwargs)
            except:
                import traceback
                print(traceback.format_exc())
                if cancel_on_failure:
                    return aioschedule.CancelJob

        return wrapper

    return catch_exceptions_decorator



#
#
# @catch_exceptions(cancel_on_failure=True)
# def job(app):
#     app.send_message("me", "Hi!")
#
#
# def run_threaded(job_func):
#     job_thread = threading.Thread(target=job_func)
#     job_thread.start()


# async def backgroundJobMain(app):
#     schedule.every(2).seconds.do(run_threaded, job, app=app)
#
#     async with app:
#         # await app.send_message("me", "Hi!")
#         while 1:
#             schedule.run_pending()
#             await asyncio.sleep(1)

i = 0


# @catch_exceptions(cancel_on_failure=True)
async def work(app) -> None:
    # await app.send_message("me", "ХуЙ")
    global i
    i += 1
    print(f"hi {i}")
    # raise Exception("my exception")
    kek = 1 / 0


async def simple():
    ...


async def update_live_client(app: Client) -> None:
    try:
        x = await app.get_me()
    except:
        print("update_live_client error")


async def morning(app: Client, id) -> None:
    try:
        await asyncio.sleep(random.randint(10, 3600))
        msg = await app.send_message(id, "Доброе утро!")
        await asyncio.sleep(3600)
        await msg.delete()
    except:
        print("morning error")


async def show_mat_stat(app: Client) -> None:
    try:
        is_enable = get_setting_value_async("is_enable_schedule_show_mat_stat", bool)
        if not is_enable:
            return

        await mat_stat_show_all(app)
    except:
        print("show_mat_stat error")



async def reset_mat_stat(app: Client) -> None:
    try:
        await mat_stat_reset()
    except:
        print("reset_mat_stat error")


async def notify_mat_stat(app: Client):
    try:
        await mat_stat_notify(app)
    except Exception as e:
        print("notify_mat_stat error: " + str(e))


def define_schedule(app: Client):
    aioschedule.every().day.at('07:00').do(morning, app=app, id=712315499)  # Мама
    aioschedule.every().day.at('07:00').do(morning, app=app, id=886661129)  # Розинский

    aioschedule.every(20).minutes.do(update_live_client, app=app)

    # aioschedule.every().day.at('22:00').do(show_mat_stat, app=app)
    # aioschedule.every().hour.do(notify_mat_stat, app=app)
    # aioschedule.every().day.at('00:00').do(reset_mat_stat, app=app)
    # aioschedule.every(4).seconds.do(work, app=app)


async def multiple_tasks(app):
    input_coroutines = [
        aioschedule.run_pending(),

        # post_comments_main(app),
        simple(),
    ]
    res = await asyncio.gather(*input_coroutines, return_exceptions=True)
    return res


def main():
    ensure_database()

    app = pyrogram.Client("my_account_2")


    # unix_time = calendar.timegm(datetime.today().date().timetuple())
    # print(unix_time)
    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)
    with app:
        common.init_common(app)
        define_schedule(app)

        while True:
            res1, res2 = asyncio.get_event_loop().run_until_complete(multiple_tasks(app))
            time.sleep(0.2)


# def backgroundJobMain(app):
#     my_thread = threading.Thread(target=main, args=(app,))
#     my_thread.start()


if __name__ == '__main__':
    main()

# https://pypi.org/project/aioschedule/
# https://docs.pyrogram.org/faq#can-i-use-multiple-clients-at-once-on-the-same-account

#  https://github.com/gawel/aiocron
#  https://question-it.com/questions/1952345/python-39-planirovanie-periodicheskih-vyzovov-asinhronnoj-funktsii-s-raznymi-parametrami
