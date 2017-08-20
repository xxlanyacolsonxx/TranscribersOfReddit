import logging

from praw.exceptions import ClientException as PRAWClientException

from tor.core.admin_commands import process_override
from tor.core.mentions import process_mention
from tor.core.reddit_ids import is_valid
from tor.core.user_interaction import process_coc
from tor.core.user_interaction import process_claim
from tor.core.user_interaction import process_done


class InboxChecker(object):
    '''
    Checks the inbox for messages to prompt further action
    '''

    known_bots = ['transcribot']

    def __init__(self, inbox, config, log=None):
        if not log:
            # this should always be passed, but just in case...
            log = logging.getLogger('tor')

        self.inbox = inbox
        self.log = log
        self.config = config

        self.mentions = []
        self.replies = []

    def call(self):
        for item in self.inbox.unread(limit=900):
            self.process_message(item)

    def process_message(self, message):
        if message.author.name in self.known_bots:
            self.ignore_message(message)
            return

        if message.subject == 'username mention':
            self.handle_mention(message)
            return

        if message.subject == 'comment reply':
            self.handle_reply(message)
            return

        for cmd in ['reload', 'update', 'ping']:
            if cmd in message.subject.lower():
                self.handle_admin_command(message)
                return

    def handle_mention(self, message):
        self.log.info('Received mention: (id is {})'.format(message))
        if not is_valid(message.parent_id, self.config):
            self.log.warning('ID already handled in DB: {}'.format(message.parent_id))
            message.mark_read()
            return

        try:
            process_mention(message, self.config)
            message.mark_read()
        except (AttributeError, PRAWClientException) as e:
            self.log.warning(e)

    def handle_admin_command(self, message):
        ''

    def handle_reply(self, message):
        self.log.info('Received comment reply: (id is {})'.format(message))

        try:
            if 'i accept' in message.body.lower():
                process_coc(message, self.config)
                message.mark_read()
                return

            elif 'claim' in message.body.lower():
                process_claim(message, self.config)
                message.mark_read()
                return

            elif 'done' in message.body.lower():
                process_done(message, self.config)
                message.mark_read()
                return

            elif '!override' in message.body.lower():
                process_override(message, self.config)
                message.mark_read()
                return

            else:
                self.log.warning('Unhandled message ("{}") found. Leaving it unread in inbox'.format(message))

        except (AttributeError, PRAWClientException) as e:
            self.log.warning(e)

    def ignore_message(self, message):
        message.mark_read()
