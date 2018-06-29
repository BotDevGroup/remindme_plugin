# -*- coding: utf-8 -*-
from marvinbot.plugins import Plugin
from marvinbot.handlers import CommandHandler
from marvinbot.core import get_adapter
from marvinbot.utils import trim_markdown
from remindme_plugin.templates import *
import logging
import arrow
import dateparser

log = logging.getLogger(__name__)


class RemindMePlugin(Plugin):
    def __init__(self):
        super(RemindMePlugin, self).__init__('remindme_plugin')
        self.config = None

    def get_default_config(self):
        return {
            'short_name': self.name,
            'enabled': True
        }

    def configure(self, config):
        self.config = config

    def setup_handlers(self, adapter):
        log.info("Setting up handlers for RemindMe plugin")
        self.add_handler(CommandHandler(
            'remindme', self.on_remindme_command,
            command_description='Reminds you of a message in the future.')
            .add_argument('when', nargs='*', help='Relative or absolute date')
        )

    def setup_schedules(self, adapter):
        pass

    def on_remindme_command(self, update, **kwargs):
        message = update.effective_message

        if message.reply_to_message is None:
            message.reply_text(text=REMINDER_NOT_REPLYING)
            return
        replied_message = message.reply_to_message

        if len(replied_message.text) == 0:
            message.reply_text(text=REMINDER_TOO_SHORT)
            return

        when_param = ' '.join([s.strip()
                               for s in kwargs.get('when') if len(s.strip())])

        tz = self.adapter.config.get('default_timezone')

        try:
            when = dateparser.parse(when_param, settings={'TIMEZONE': tz})
        except:
            message.reply_text(text=REMINDER_INVALID_DATE)
            return

        when_relative = arrow.get(when, tz)

        if when_relative < arrow.now(tz):
            message.reply_text(text=REMINDER_NO_FUTURE_DATE)
            return

        job_id = '{}/{}@{}/{}'.format(self.name, message.from_user.id,
                                      message.chat.id, message.message_id)

        name = '{}: reminder for {}@{} of msgid {}'.format(
            self.name,
            message.from_user.id,
            message.chat.id,
            message.message_id
        )
        kwargs = {
            'message_id': replied_message.message_id,
            'message_user_id': replied_message.from_user.id,
            'message_first_name': replied_message.from_user.first_name,
            'message_text': replied_message.text,
            'message_date': arrow.get(replied_message.date, tz),
            'remind_chat_id': message.chat.id,
            'remind_user_id': message.from_user.id,
            'remind_first_name': message.from_user.first_name,
            'remind_date': arrow.get(message.date, tz)
        }
        self.adapter.add_job(RemindMePlugin.on_job_run, 'date',
                             run_date=when,
                             id=job_id,
                             name=name,
                             kwargs=kwargs,
                             replace_existing=True)
        when_str = RemindMePlugin.format_date(when_relative)
        message.reply_text(
            text=REMINDER_SUCCESS.format(when_str, when_relative.humanize()),
            parse_mode='HTML'
        )

    @staticmethod
    def format_date(date):
        return '{} at {}'.format(
            date.format('dddd, MMMM Do, YYYY'),
            date.format('hh:mm a')
        )

    @staticmethod
    def on_job_run(**kwargs):
        adapter = get_adapter()

        message_id = kwargs.get('message_id')
        remind_chat_id = kwargs.get('remind_chat_id')
        remind_user_id = kwargs.get('remind_user_id')

        kwargs['remind_date'] = RemindMePlugin.format_date(
            kwargs['remind_date'])
        kwargs['message_date'] = RemindMePlugin.format_date(
            kwargs['message_date'])
        kwargs['remind_first_name'] = trim_markdown(
            kwargs['remind_first_name'])
        kwargs['message_first_name'] = trim_markdown(
            kwargs['message_first_name'])
        kwargs['message_text'] = trim_markdown(kwargs['message_text'])

        text = PRIVATE_REMINDER_MSG_TEMPLATE if remind_chat_id == remind_user_id else CHAT_REMINDER_MSG_TEMPLATE

        adapter.bot.send_message(
            chat_id=remind_chat_id,
            text=text.format(**kwargs),
            reply_to_message_id=message_id,
            parse_mode='Markdown'
        )
