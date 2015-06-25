# OSMNotesBot

Bot for [telegram](https://telegram.org/) to post
[notes](http://wiki.openstreetmap.org/wiki/Notes) to Openstreetmap. Send your
location to the bot, then reply with text of the note.

[@OSMNotesBot](https://telegram.me/OSMNotesBot) in telegram.

## Install

This bot uses [Google App Engine](https://cloud.google.com/appengine/).
To deploy or test locally, install
[GAE SDK](https://cloud.google.com/appengine/downloads).

Copy ``settings.py.example`` to ``settings.py`` and configure with your bot's
API key and URIs.

After starting, open ``https://your-app-domain/run/your-secret/`` in browser to
request sending all messages to application's webhook.

It's currently stateless and not using any data storage.
