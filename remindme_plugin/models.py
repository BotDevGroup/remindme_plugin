import mongoengine
from marvinbot.utils import localized_date

class Reminder(mongoengine.Document):
    id = mongoengine.SequenceField(primary_key=True)

    chat_id = mongoengine.LongField(required=True)
    username = mongoengine.StringField()
    user_id = mongoengine.LongField(required=True)
    message_id = mongoengine.LongField(required=True)
    when = mongoengine.DateTimeField(required=True)
    date_added = mongoengine.DateTimeField(default=localized_date)
    date_modified = mongoengine.DateTimeField(default=localized_date)
    date_deleted = mongoengine.DateTimeField(required=False, null=True)

    @classmethod
    def by_id(cls, id):
        try:
            return cls.objects.get(id=id)
        except cls.DoesNotExist:
            return None

    @classmethod
    def by_chat_id(cls, chat_id):
        try:
            return cls.objects.get(chat_id=chat_id)
        except cls.DoesNotExist:
            return None

    @classmethod
    def all(cls):
        try:
            return cls.objects(date_deleted=None)
        except:
            return None
