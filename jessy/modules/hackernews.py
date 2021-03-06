# -*- coding: utf-8-*-
import urllib2
import random
from bs4 import BeautifulSoup
from semantic.numbers import NumberService
from jessy import app_utils
from jessy.modules import JessyModule


URL = 'http://news.ycombinator.com'


class HNStory(object):

    def __init__(self, title, URL):
        self.title = title
        self.URL = URL


def get_top_stories(max_results=None):
    """
        Returns the top headlines from Hacker News.

        Arguments:
        maxResults -- if provided, returns a random sample of size maxResults
    """
    hdr = {'User-Agent': 'Mozilla/5.0'}
    req = urllib2.Request(URL, headers=hdr)
    page = urllib2.urlopen(req).read()
    soup = BeautifulSoup(page)
    matches = soup.findAll('td', class_="title")
    matches = [m.a for m in matches if m.a and m.text != u'More']
    matches = [HNStory(m.text, m['href']) for m in matches]

    if max_results:
        num_stories = min(max_results, len(matches))
        return random.sample(matches, num_stories)

    return matches


def _handle(mic, profile):
    """
        Responds to user-input, typically speech text, with a sample of
        Hacker News's top headlines, sending them to the user over email
        if desired.

        Arguments:
        text -- user-input, typically transcribed speech
        mic -- used to interact with the user (for both input and output)
        profile -- contains information related to the user (e.g., phone
                   number)
    """
    mic.say("Pulling up some stories.")
    stories = get_top_stories(max_results=3)
    all_titles = '... '.join(str(idx + 1) + ") " +
                             story.title for idx, story in enumerate(stories))

    def handle_response(text):

        def extract_ordinals(text):
            output = []
            service = NumberService()
            for w in text.split():
                if w in service.__ordinals__:
                    output.append(service.__ordinals__[w])
            return [service.parse(w) for w in output]

        chosen_articles = extract_ordinals(text)
        send_all = not chosen_articles and app_utils.is_positive(text)

        if send_all or chosen_articles:
            mic.say("Sure, just give me a moment")

            if profile['prefers_email']:
                body = "<ul>"

            def format_article(article):
                tiny_url = app_utils.generate_tiny_url(article.URL)

                if profile['prefers_email']:
                    return "<li><a href=\'%s\'>%s</a></li>" % (tiny_url,
                                                               article.title)
                else:
                    return article.title + " -- " + tiny_url

            for idx, article in enumerate(stories):
                if send_all or (idx + 1) in chosen_articles:
                    article_link = format_article(article)

                    if profile['prefers_email']:
                        body += article_link
                    else:
                        if not app_utils.email_user(profile, SUBJECT="",
                                                    BODY=article_link):
                            mic.say("I'm having trouble sending you these " +
                                    "articles. Please make sure that your " +
                                    "phone number and carrier are correct " +
                                    "on the dashboard.")
                            return

            # if prefers email, we send once, at the end
            if profile['prefers_email']:
                body += "</ul>"
                if not app_utils.email_user(profile,
                                            SUBJECT="From the Front Page of " +
                                                   "Hacker News",
                                            BODY=body):
                    mic.say("I'm having trouble sending you these articles. " +
                            "Please make sure that your phone number and " +
                            "carrier are correct on the dashboard.")
                    return

            mic.say("All done.")

        else:
            mic.say("OK I will not send any articles")

    if not profile['prefers_email'] and profile['phone_number']:
        mic.say("Here are some front-page articles. " +
                all_titles + ". Would you like me to send you these? " +
                "If so, which?")
        handle_response(mic.active_listen())

    else:
        mic.say("Here are some front-page articles. {0}".format(all_titles.encode('utf-8')))


class HackerNews(JessyModule):
    '''
    Handle GMail
    '''
    PRIORITY = 4
    NAME = 'Hacker news'
    DESCR = 'Can tell the latest hacker news'
    IS_SKILL = True

    def __init__(self, *args, **kwargs):
        JessyModule.__init__(self, *args, **kwargs)

    def handle(self, transcription, context=None):
        if self.matches(transcription):
            _handle(self._mic, self._config)
            return True

    @classmethod
    def keywords(cls):
        return ['hacker', 'news']


plugin = HackerNews
