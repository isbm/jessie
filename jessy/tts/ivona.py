# -*- coding: utf-8-*-
"""
A Speaker handles audio output from Jasper to the user

Speaker methods:
    say - output 'phrase' as speech
    play - play the audio in 'filename'
    is_available - returns True if the platform supports this implementation
"""
import os
import tempfile
import yaml

try:
    import pyvona
    HAS_PYVONA = True
except ImportError:
    HAS_PYVONA = False

from jessy import diagnose
from jessy import jessypath
from jessy.utils import _module_getter
from jessy.tts import AbstractMp3TTSEngine


class IvonaTTS(AbstractMp3TTSEngine):
    """
    Uses the Ivona Speech Cloud Services.
    Ivona is a multilingual Text-to-Speech synthesis platform developed by
    Amazon.
    """

    SLUG = "ivona-tts"

    def __init__(self, access_key='', secret_key='', region=None,
                 voice=None, speech_rate=None, sentence_break=None):
        super(self.__class__, self).__init__()
        self._pyvonavoice = pyvona.Voice(access_key, secret_key)
        self._pyvonavoice.codec = "mp3"
        if region:
            self._pyvonavoice.region = region
        if voice:
            self._pyvonavoice.voice_name = voice
        if speech_rate:
            self._pyvonavoice.speech_rate = speech_rate
        if sentence_break:
            self._pyvonavoice.sentence_break = sentence_break

    @classmethod
    def get_config(cls, profile):
        config = {}
        if 'ivona-tts' in profile:
            if 'access_key' in profile['ivona-tts']:
                config['access_key'] = profile['ivona-tts']['access_key']
            if 'secret_key' in profile['ivona-tts']:
                config['secret_key'] = profile['ivona-tts']['secret_key']
            if 'region' in profile['ivona-tts']:
                config['region'] = profile['ivona-tts']['region']
            if 'voice' in profile['ivona-tts']:
                config['voice'] = profile['ivona-tts']['voice']
            if 'speech_rate' in profile['ivona-tts']:
                config['speech_rate'] = profile['ivona-tts']['speech_rate']
            if 'sentence_break' in profile['ivona-tts']:
                config['sentence_break'] = profile['ivona-tts']['sentence_break']

        return config

    @classmethod
    def is_available(cls):
        return (super(cls, cls).is_available() and
                diagnose.check_python_import('pyvona') and
                diagnose.check_network_connection())

    def say(self, phrase, *args):
        self._logger.debug("Saying '%s' with '%s'", phrase, self.SLUG)
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            tmpfile = f.name
        self._pyvonavoice.fetch_voice(phrase, tmpfile)
        self.play_mp3(tmpfile)
        os.remove(tmpfile)


def is_valid():
    '''
    Validator.
    '''
    return HAS_PYVONA


initiator = _module_getter(IvonaTTS)
