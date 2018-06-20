# -*- coding: utf-8 -*-
from marvinbot.plugins import Plugin
from marvinbot.handlers import CommandHandler
from marvinbot.core import get_adapter
from remindme_plugin.models import Reminder
import logging
import arrow
import dateparser

log = logging.getLogger(__name__)


class RemindMePlugin(Plugin):
    def __init__(self):
        super(RemindMePlugin, self).__init__('remindme_plugin')
        self.config = None
        self.job = None

    def get_default_config(self):
        return {
            'short_name': self.name,
            'enabled': True,
        }

    def configure(self, config):
        self.config = config

    def setup_handlers(self, adapter):
        log.info("Setting up handlers for RemindMe plugin")
        self.add_handler(CommandHandler('remindme', self.on_remindme_command,
                                        command_description='Reminds you of a message in the future.')
                         .add_argument('when', nargs='*', help='Relative or absolute date'))

    def setup_schedules(self, adapter):
        self.job = self.adapter.add_job(RemindMePlugin.on_timer, 'interval',
                                        minutes=1,
                                        id='{}-timer'.format(self.name),
                                        name='{} minutely timer'.format(
                                            self.name),
                                        replace_existing=True)

    def on_remindme_command(self, update, **kwargs):
        message = update.effective_message
        if message.reply_to_message is None:
          message.reply_text(text='❌ You must use this command when replying.')
          return
        log.info(str(kwargs))
        log.info(str(message))
        when_str = ' '.join([s.strip() for s in kwargs.get('when') if len(s.strip()) > 0])
        when = dateparser.parse(when_str)
        when_relative = arrow.get(when)
        if when_relative < arrow.now():
          message.reply_text(text='❌ You must specify a date in the future.')
          return
        log.info(when_str)
        log.info(when_relative)
        message.reply_text(text='🤖 I will be messaging you on <b>{}</b> ({}) to remind you of <b>{}</b>'.format(
            when, when_relative.humanize(), 'link to msg'), parse_mode='HTML')

    @classmethod
    def add_reminder(cls, **kwargs):
        try:
            reminder = Reminder(**kwargs)
            reminder.save()
            return True
        except Exception as err:
            log.info(err)
            return False

    @staticmethod
    def get_reminders():
        return Reminder.all()

    @staticmethod
    def on_timer():
        log.info('on timer... 👀')
        reminders = RemindMePlugin.get_reminders()
        adapter = get_adapter()
        for reminder in reminders:
            adapter.bot.send_message(chat_id='7175022', text=str(reminder))
