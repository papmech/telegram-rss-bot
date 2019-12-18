# Telegram RSS Bot

A barebones RSS bot that scrapes a list of RSS feeds and sends them via a Telegram Bot to a channel or chat.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

- A bot which is has permissions for the desired channel/group/chat.
- The ID of the channel/group/chat. To figure this out, [see here](https://stackoverflow.com/questions/36099709/how-get-right-telegram-channel-id/45577616).
- Python 3

### Installing

Clone the git repo. Install the python dependencies.

```
pip3 install -r requirements.txt
```

Run the bot (assumes that ```python3``` is the binary to run Python 3).

```
python3 .\news-scraper-bot-v2.py "<YOUR_BOT_TOKEN>" --interval 60
```

## Authors

* papmech - *Initial work* 

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## Acknowledgments

* [Python Telegram Bot](https://github.com/python-telegram-bot/python-telegram-bot)
* [README Template](https://gist.github.com/PurpleBooth/109311bb0361f32d87a2)
