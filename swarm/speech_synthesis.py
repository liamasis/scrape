import datetime
import logging

import azure.cognitiveservices.speech as speechsdk
from django.conf import settings
import uuid
from swarm.audio_journey import *

# Please load secrets from .env
speech_config = speechsdk.SpeechConfig(subscription=settings.AZURE_SPEECH_KEY, region=settings.AZURE_SPEECH_REGION)

speech_config.set_speech_synthesis_output_format(speechsdk.SpeechSynthesisOutputFormat.Audio24Khz160KBitRateMonoMp3)
speech_config.speech_synthesis_voice_name='en-AU-NatashaNeural' # Not needed if using SSML

logger = logging.getLogger(__name__)

# xml.sax.saxutils.escape doesn't escape " and ' so...
def escape(s: str):
    s = s.replace("&", "&amp;")
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    s = s.replace("\"", "&quot;")
    s = s.replace("'", "&apos;")
    return s


def synthesise(text: str, file_name: str, effect: Effect) -> datetime.timedelta:
    """
    Synth audio and save it to a file
    :param text:
    :param file_name:
    :return: Audio duration if synthesised; None otherwise
    """

    # Escape the text for use with SSML
    text = escape(text)

    # Configure file path
    audio_config = speechsdk.audio.AudioOutputConfig(filename=str(settings.BASE_DIR / 'swarm' / 'static' / 'audio' / file_name))
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

    voice_tag_open = ''
    voice_tag_close = ''

    if effect.voice == Voice.NATASHA:
        voice_tag_open = '<voice name="en-AU-NatashaNeural">'
        voice_tag_close = '</voice>'

    elif effect.voice == Voice.JENNY_WHISPER:
        voice_tag_open = '<voice name="en-US-JennyNeural"><mstts:express-as style="whispering">'
        voice_tag_close = '</mstts:express-as></voice>'

    elif effect.voice == Voice.JENNY_UNFRIENDLY:
        voice_tag_open = '<voice name="en-US-JennyNeural"><mstts:express-as style="unfriendly">'
        voice_tag_close = '</mstts:express-as></voice>'

    # Generate SSML
    ssml = f"""
    <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="http://www.w3.org/2001/mstts" xml:lang="en-US">
        {voice_tag_open}
            <prosody rate="{effect.rate}%" pitch="{effect.pitch}%">{text}</prosody>
        {voice_tag_close}
    </speak>
    """

    # Ask friendly Satya Nadella
    # speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()
    speech_synthesis_result = speech_synthesizer.speak_ssml_async(ssml).get()

    if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        logger.debug("Speech synthesized for text [{}]".format(text))
        return speech_synthesis_result.audio_duration

    elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_synthesis_result.cancellation_details
        logger.warning("Speech synthesis canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            if cancellation_details.error_details:
                logger.warning("Error details: {}".format(cancellation_details.error_details))
                logger.warning("Did you set the speech resource key and region values?")

    else:
        logger.warning("ERROR: Unknown error occurred with speech synthesis")

    return None


def main():
    print(settings.BASE_DIR)
    file_name = f'{uuid.uuid4().hex}.mp3'
    res = synthesise("Faux Mo House party edition was a vibe. Made possible by excellence of all the artists.", file_name, Effect(rate=30, pitch=-40, voice=Voice.NATASHA))
    print(file_name, res)
    # synthesise("There's just NO WAY that \"BOBO\" could do such a thing <_> !!! Me & doggo will show him!", uuid.uuid4().hex + '.mp3') # Testing escape strings

if __name__ == "__main__":
    main()