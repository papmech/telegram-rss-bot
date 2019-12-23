#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Bot that scrapes RSS feeds.

Usage:
Run python3 bot.py --help for help.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import feedparser
import tzlocal
import pytz
import argparse
import datetime as dt
import yaml
from sqlitedict import SqliteDict
from telegram.ext import Updater, CommandHandler
from time import mktime

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

SGT = pytz.timezone('Asia/Singapore')
RSS_FROM_THIS_TIMESTAMP = dt.datetime.strptime('20 Mar 2019 2:30PM', '%d %b %Y %I:%M%p').astimezone(SGT)

# def update_feeds(bot, job):
def update_feeds(context):
    job = context.job
    bot = context.bot
    chat_name, chat_id, seen_urls_dict, feeds = job.context
    logger.debug("update_feeds called! chat_name = '%s' | chat_id = '%s'" % (chat_name, chat_id))

    for feed in feeds: # feeds is a list of dicts with keys {name, url, disabled}
        feed_name = feed['name']

        if "disabled" in feed and feed['disabled']:
            logger.debug("skipping '%s' since 'disabled' detected" % feed_name)
            continue

        # HTTP access on feed['url'] and grab the entries
        try:
            NewsFeed = feedparser.parse(feed['url'])
        except:
            logger.error("Exception when attempting to read and/or parse '%s' at URL %s", feed_name, feed['url'])
            continue

        for entry in NewsFeed.entries:
            # Ignore if the link has already been seen before
            if entry.link in seen_urls_dict:
                break

            # Ignore if any of the ignored_categories are found in the entry.category
            if 'ignored_categories' in feed:
                ignored = False
                for c in feed['ignored_categories']:
                    if c in entry.category:
                        logger.info("Ignored because category = '%s': %s | %s | %s", entry.category, feed_name, entry.published, entry.link) 
                        ignored = True
                        # Mark as seen
                        seen_urls_dict[entry.link] = True
                        break
                if ignored: continue

            # Ignore if the published datetime is before RSS_FROM_THIS_TIMESTAMP
            published_datetime = dt.datetime.fromtimestamp(mktime(entry.published_parsed)).replace(tzinfo=pytz.utc).astimezone(SGT)
            if published_datetime < RSS_FROM_THIS_TIMESTAMP:
                break

            try:
                bot.send_message(chat_id, text="%s (%s)\n%s\n[%s]" % (entry.title, published_datetime.strftime("%Y-%m-%d %H:%M"), entry.link, feed_name))
                logger.info("Sent to chat '%s': %s | %s | %s", chat_name, feed_name, entry.published, entry.link)
                
                # If this line is reached, then the message has been successfully sent
                seen_urls_dict[entry.link] = True
            except telegram.error.TimedOut as exc:
                logger.error("Timeout when attempting to send to chat '%s': %s | %s | %s", chat_name, feed_name, entry.published, entry.link)
            except:
                logger.error("Exception when attempting to send to chat '%s': %s | %s | %s", chat_name, feed_name, entry.published, entry.link)

def error(bot, update, telegram_error):
    logger.warning('Update "%s" caused error "%s"', update, telegram_error)

def main():
    # Command line parameters
    parser = argparse.ArgumentParser(description='RSS Scraping Telegram Bot')
    parser.add_argument('bot_token', action='store', default=None, help="Your bot's token")
    # parser.add_argument('chat_id', action='store', default=None, help="The destination channel or chat in the format @channelname")
    parser.add_argument('--interval', dest='interval', action='store', type=int, default=60, help="Interval in seconds to refresh the RSS feeds")
    parser.add_argument('--feeds', dest='feeds', action='store', type=str, default='feeds.yaml', help="YAML file containing chats and feeds")
    parser.add_argument('--seendb', dest='seendb', action='store', type=str, default='seen_urls.sqlite', help="SQLite db for storing seen URLs")
    parser.add_argument('--runonce', action='store_true', default=False, help="Scrape once and quit")
    args = parser.parse_args()

    # Open the "feeds.yaml" config file and read the feeds
    with open(args.feeds, 'r') as stream:
        try:
            feeds_config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print("Error while loading %s" % args.feeds)
            raise exc

    logger.info("RSS Scraping Telegram Bot starting up...")
    updater = Updater(args.bot_token, use_context=True)

    for chat in feeds_config['chats']:
        seen_urls_dict = SqliteDict(args.seendb, autocommit=True, tablename=chat['chat_name'])
        if args.runonce:
            updater.job_queue.run_once(update_feeds, 0, context=(chat['chat_name'], chat['chat_id'], seen_urls_dict, chat['feeds']))
        else:
            updater.job_queue.run_repeating(update_feeds, args.interval, context=(chat['chat_name'], chat['chat_id'], seen_urls_dict, chat['feeds']))

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()