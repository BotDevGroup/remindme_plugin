REMINDER_SUCCESS = '🤖 I will be messaging you on <b>{}</b> ({}) to remind you.'

REMINDER_NO_FUTURE_DATE = '❌ You must specify a date in the future.'

REMINDER_INVALID_DATE = '❌ You must specify a valid date.'

REMINDER_TOO_SHORT = '❌ You must reply to a message with some text.'

REMINDER_NOT_REPLYING = '❌ You must use this command when replying.'

PRIVATE_REMINDER_MSG_TEMPLATE = """🤖 Hi {remind_first_name},
On *{remind_date}* you asked me to remind you of this message:

{message_text}
"""

CHAT_REMINDER_MSG_TEMPLATE = """🤖 Hi [{remind_first_name}](tg://user?id={remind_user_id}),
On *{remind_date}* you asked me to remind you of this message:

*{message_first_name}*: {message_text}

Sent at *{message_date}*
"""