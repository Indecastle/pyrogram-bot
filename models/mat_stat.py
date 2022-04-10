from datetime import datetime

import pytz


class mat_stat:
    def __init__(self, row=None):
        if row is None:
            return
        self.chat_id = row['ChatId']
        self.user_id = row['UserId']
        self.username = row['UserName']
        self.firstname = row['FirstName']
        self.lastname = row['LastName']
        self.created_at_date = datetime.fromtimestamp(row['CreatedAtDate'], tz=pytz.utc) if 'CreatedAtDate' in row else None
        self.created_at_datetime = datetime.fromtimestamp(row['CreatedAtDateTime'], tz=pytz.utc) if 'CreatedAtDateTime' in row else None
        self.count = row['Count']

