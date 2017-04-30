import logging

from tor.helpers.flair import flair
from tor.helpers.flair import flair_post
from tor.setup import __version__
from tor.strings.responses import bot_footer


def set_meta_flair_on_other_posts(r, tor, context):
    """
    Loops through the 10 newest posts on ToR and sets the flair to
    'Meta' for any post that is not authored by the bot or any of
    the moderators.

    :param transcribersofreddit: The Subreddit object for ToR.
    :param Context: the active context object.
    :return: None.
    """
    for post in tor.new(limit=10):

        if (
            post.author != r.redditor('transcribersofreddit') and
            post.author not in context.tor_mods and
            post.link_flair_text != flair.meta
        ):
            logging.info(
                'Flairing post {} by author {} with Meta.'.format(
                    post.fullname, post.author
                )
            )
            flair_post(post, flair.meta)


def _(message):
    """
    Message formatter. Returns the message and the disclaimer for the
    footer.

    :param message: string. The message to be displayed.
    :return: string. The original message plus the footer.
    """
    return bot_footer.format(message, version=__version__)


def log_header(message):
    logging.info('*' * 50)
    logging.info(message)
    logging.info('*' * 50)