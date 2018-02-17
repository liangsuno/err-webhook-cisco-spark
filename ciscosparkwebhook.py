from errbot import BotPlugin, webhook
from ciscosparkapi import CiscoSparkAPI, Webhook
spark_api = CiscoSparkAPI()

class CiscoSparkWebhook(BotPlugin):

    @webhook('/errbot/spark', raw=True)
    def errbot_spark(self, raw):

        signature = hmac.new(self._bot.webhook_secret.encode('utf-8'), raw.body.read(), hashlib.sha1).hexdigest()

        if signature != raw.get_header('X-Spark-Signature'):
            self.log.debug("X-Spark-Signature failed. Webhook will NOT be processed")

        else:
            webhook_event = Webhook(raw.json)

            bot_name = self._bot.bot_name

            if webhook_event.actorId == self._bot.bot_identifier.id:
                self.log.debug("Message created by bot...ignoring")

            else:

                # Need to load complete message from Spark as the webhook message only includes IDs
                # Can only retrieve messages targeted to the bot. User must type @<botname> <message>.
                message = spark_api.messages.get(webhook_event.data.id)   # Get the message details

                #spark_api.messages.create(webhook_event.data.roomId, text="Welcome to the room!")

                room = spark_api.rooms.get(webhook_event.data.roomId)     # Get the room details
                person = spark_api.people.get(message.personId)           # Get the sender's details
                occupant = self._bot.get_occupant_using_id(person=person, room=room)

                # Strip the bot name from the message in order for errbot to process commands properly
                message_without_botname = message.text.replace(bot_name,"",1).lstrip()
                msg = self._bot.create_message(body=message_without_botname, frm=occupant, to=room, extras={'roomType': webhook_event.data.roomType})

                # Force the bot to process the message and our job is done!
                self._bot.process_message(msg)

        return "OK"

