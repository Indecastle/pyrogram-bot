import asyncio
import os
import sqlite3
from contextlib import closing
from typing import Union, Coroutine

from models.mat_stat import mat_stat

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

conn = sqlite3.connect(os.path.join(ROOT_DIR, "mydb.sqlite"), check_same_thread=False)  # isolation_level=None
conn.row_factory = sqlite3.Row


def fetchall_async(func):
    async def wrap_log(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: func(*args, **kwargs))
    return wrap_log


# def map_rows(rows, target_type):
#     keys = rows[0].keys()
#     mapped_list = []
#     for row in rows:
#         obj = target_type()
#         for key in keys:
#             setattr(obj, key, row[key])
#         mapped_list.append(obj)
#     return mapped_list


def map_rows(rows, target_type):
    return [target_type(row) for row in rows]


def ensure_database():
    with conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS settings (
            `Id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            `Key` VARCHAR(100) UNIQUE NOT NULL,
            `Value` VARCHAR(100) NOT NULL
        )""")

        conn.execute("""CREATE TABLE IF NOT EXISTS mat_stat (
                    `ChatId` INT NOT NULL,
                    `UserId` INT NOT NULL,
                    `UserName` NVARCHAR(1000) NULL,
                    `FirstName` NVARCHAR(1000) NULL,
                    `LastName` NVARCHAR(1000) NULL,
                    `CreatedAtDate` INT DEFAULT (strftime ('%s', date('now', 'localtime'))) NOT NULL,
                    `CreatedAtDateTime` INT DEFAULT (strftime ('%s', datetime('now', 'localtime'))) NOT NULL,
                    `Count` INT NOT NULL,
                    PRIMARY KEY ( `ChatId`, `UserId`, `CreatedAtDate`)
                )""")
        conn.execute("""CREATE TABLE IF NOT EXISTS mat_chat_variables (
                            `ChatId` INT NOT NULL,
                            `UserId` INT NOT NULL,
                            `Key` VARCHAR(100) UNIQUE NOT NULL,
                            `Value` VARCHAR(100) UNIQUE NOT NULL,
                            PRIMARY KEY ( `ChatId`, `UserId`, `Key`)
                        )""")


@fetchall_async
def mat_stat_init_if_not_exists(chat_id: int, user_id: int, username: str, firstname: str, lastname: str):
    with conn:
        conn.execute("""
        INSERT OR IGNORE INTO mat_stat (ChatId, UserId, UserName, FirstName, LastName, Count)
        VALUES (?, ?, ?, ?, ?, 0)
        """, [chat_id, user_id, username, firstname, lastname])


@fetchall_async
def mat_stat_increase_item(chat_id: int, user_id: int, unix_date: int, mat_count: int):
    with conn:
        conn.execute("""
        UPDATE mat_stat SET Count = Count + ?
        WHERE ChatId = ? AND UserId = ? AND CreatedAtDate = ?;
        """, [mat_count, chat_id, user_id, unix_date])


@fetchall_async
def mat_stat_reset_by_chat(chat_id: str):
    with conn:
        conn.execute("DELETE FROM mat_stat WHERE ChatId = ?;", [chat_id])


@fetchall_async
def mat_stat_reset():
    with conn:
        conn.execute("DELETE FROM mat_stat;")


@fetchall_async
def get_mat_stat_chats(unix_date):
    with conn:
        with closing(conn.cursor()) as cur:  # auto-closes
            cur.execute("SELECT ChatId FROM mat_stat WHERE CreatedAtDate >= ? GROUP BY ChatId;", [unix_date])
            result = [d['ChatId'] for d in cur.fetchall()]
            return result


@fetchall_async
def get_mat_stat_all(unix_date):
    with conn:
        with closing(conn.cursor()) as cur:  # auto-closes
            cur.execute("SELECT * FROM mat_stat WHERE CreatedAtDate >= ? ORDER BY Count DESC", [unix_date])
            sql_result = cur.fetchall()
            return map_rows(sql_result, mat_stat)


@fetchall_async
def get_mat_stat_by_chat_id_and_date(chat_id, unix_date):
    with conn:
        with closing(conn.cursor()) as cur:  # auto-closes
            cur.execute("""
                SELECT ChatId, UserId, UserName, FirstName, LastName, SUM(Count) as `Count` 
                FROM (
                    SELECT *
                    FROM mat_stat
                    ORDER BY CreatedAtDate DESC
                )
                WHERE ChatId = ? AND CreatedAtDate >= ? 
                GROUP BY ChatId, UserId
                ORDER BY Count DESC""", [chat_id, unix_date])
            sql_result = cur.fetchall()
            return map_rows(sql_result, mat_stat)


@fetchall_async
def set_setting_value(key: str, value: object):
    with conn.cursor():
        conn.execute("INSERT INTO settings(Key, Value) VALUES (?, ?)", [key, value])


@fetchall_async
def set_or_update_setting_value(key: str, value: object):
    with conn:
        conn.execute("INSERT OR IGNORE INTO settings(Key, Value) VALUES (:key, :value)", {"key": key, "value": value})
        conn.execute("UPDATE settings SET Value = ? WHERE Key=?", [value, key], )


@fetchall_async
def get_setting_value_async(key: str, type: object = str) -> Union[str, bool, int, float, None]:
    return get_setting_value(key, type)


def get_setting_value(key: str, type: object = str) -> Union[str, bool, int, float, None]:
    with conn:
        with closing(conn.cursor()) as cur:  # auto-closes
            cur.execute("SELECT * FROM settings WHERE Key = ?", [key])
            fetch_result = cur.fetchone()
            result = fetch_result['Value'] if fetch_result is not None else None
            if type is None:
                return None
            if type is str:
                return result
            if type is bool:
                return result == '1'
            if type is int:
                return int(result)
            if type is float:
                return float(result)


async def main():
    await set_or_update_setting_value("key4", True)
    value = await get_setting_value_async("key4", bool)
    print(value)
    chats = await get_mat_stat_chats()
    print(chats)
    return 'kek'


if __name__ == '__main__':
    ensure_database()

    res1 = asyncio.get_event_loop().run_until_complete(main())
    print(res1)
