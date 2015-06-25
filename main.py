#!/usr/bin/env python
import json
import re
import urllib
import logging
import webapp2
import urllib2

import settings

class TelegramAPIError(Exception):
    pass


class OSMAPIError(Exception):
    pass


def create_osm_note(lat, lon, text):
    url = "{}/notes?{}".format(settings.osm_api_prefix,
                               urllib.urlencode(dict(lat=lat.encode("utf-8"),
                                                     lon=lon.encode("utf-8"),
                                                     text=text.encode("utf-8"))))
    # logging.info(url)
    resp = urllib2.urlopen(url, data="")
    if resp.getcode() != 200:
        raise OSMAPIError(resp.read())
    # logging.info(resp.read())
    m = re.match(r".*/notes/(\d+)/.*", resp.read(), re.DOTALL)  # Sorry for parsing XML with regexps :3
    if m:
        return int(m.group(1))


def telegram(method, **params):
    def convert(value):
        if isinstance(value, dict):
            return json.dumps(value)
        elif isinstance(value, unicode):
            return value.encode('utf-8')
        else:
            return value

    processed_params = {k: convert(v) for k, v in params.iteritems()}
    resp = urllib2.urlopen("https://api.telegram.org/bot{}/{}".format(settings.apikey, method),
                           urllib.urlencode(processed_params))
    if resp.getcode() != 200:
        raise TelegramAPIError("Non 200 return code")
    data = json.load(resp)
    if not data['ok']:
        raise TelegramAPIError(data['description'])
    return data

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello world!')

class StartHandler(webapp2.RequestHandler):
    def get(self):
        r = telegram("setWebhook", url=settings.webhook.format(settings.secret))
        json.dump(r, self.response)

class MessageHandler(webapp2.RequestHandler):
    def post(self):
        update = json.loads(self.request.body)
        # logging.info(self.request.body)
        message = update['message']

        if message.get('location'):
            self._location_received(message)
        elif (message.get('reply_to_message') and
              message['reply_to_message']['from']['id'] == settings.bot_user_id and
              message.get('text')):
            self._description_received(message)

    def _location_received(self, message):
        text = "Okay, reply with description text for note at [{}, {}]".format(
            message['location']['latitude'], message['location']['longitude'])
        telegram("sendMessage", chat_id=message['chat']['id'], text=text, reply_markup={'force_reply': True})

    def _description_received(self, message):
        # logging.info("description received")
        orig_text = message['reply_to_message']['text']
        m = re.match(r".*\s+\[([0-9.]+), ([0-9.]+)\]\s*$", orig_text)
        if m:
            lat = m.group(1)
            lon = m.group(2)
            note_id = create_osm_note(lat, lon, message['text'] + u"\n\n(sent with @OSMNotesBot (telegram))")
            text = u"\U0001f4dd Thanks, added note {}".format(settings.osm_note_url.format(note_id))
            logging.info("Created note {}, message: {}".format(note_id, message))
            telegram("sendMessage", chat_id=message['chat']['id'], text=text, disable_web_page_preview=True)

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/start/{}/'.format(settings.secret), StartHandler),
    ('/incoming/{}/'.format(settings.secret), MessageHandler)
], debug=True)
