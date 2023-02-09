import datetime as dt
from enum import Enum

# The time to wait from one audio to the next
DEFAULT_GAP = dt.timedelta(seconds=1)
DEFAULT_VOICE_PITCH = -20

class Voice(Enum):
    NATASHA = 1
    JENNY_WHISPER = 2
    JENNY_UNFRIENDLY = 3

class IntermissionType(Enum):
    STATIC_AUDIO = 1
    PLAY_INSTAGRAM_HANDLE = 2
    REPEAT_LAST = 3
    PAUSE = 4
    BACKGROUND_AUDIO = 5

class Effect:
    def __init__(self, timestamp: dt.timedelta = None, voice: Voice = Voice.NATASHA, rate: int = 0,
                 pitch: int = DEFAULT_VOICE_PITCH, gap: dt.timedelta = DEFAULT_GAP, volume: float = 1):
        self.timestamp = timestamp
        self.voice = voice
        self.rate = rate
        self.pitch = pitch
        self.gap = gap
        self.volume = volume

class Intermission:
    def __init__(self, timestamp: dt.timedelta, type: IntermissionType, audio_file: str = '', duration: dt.timedelta = dt.timedelta(seconds=1), effect: Effect = Effect()):
        self.timestamp = timestamp
        self.type = type
        self.audio_file = audio_file
        self.duration = duration
        self.effect = effect

# Intermissions should be in order of playback.
# Each intermission will be played back NO EARLIER THAN the timestamp.
def get_intermissions():
    return [
        Intermission(dt.timedelta(seconds=0),                IntermissionType.BACKGROUND_AUDIO,        '/static/audio_samples/Scrape290722_Underscore.mp3'),
        Intermission(dt.timedelta(seconds=0),                IntermissionType.PAUSE,                   duration=dt.timedelta(minutes=0, seconds=57)),
        Intermission(dt.timedelta(minutes=1, seconds=35),    IntermissionType.STATIC_AUDIO,            '/static/audio_samples/Scrape290722_Audio1_Hmm.mp3',             duration=dt.timedelta(seconds=1)),
        Intermission(dt.timedelta(minutes=3, seconds=42),    IntermissionType.STATIC_AUDIO,            '/static/audio_samples/Scrape290722_Audio2_Grave.mp3',           duration=dt.timedelta(seconds=9)),
        Intermission(dt.timedelta(minutes=4, seconds=46),    IntermissionType.STATIC_AUDIO,            '/static/audio_samples/Scrape290722_Audio3_End.mp3',             duration=dt.timedelta(seconds=32)),
    ]

def get_effects():
    return [
        Effect(dt.timedelta(seconds=0),                     Voice.JENNY_WHISPER,        rate=-5,    pitch=-20,    volume=0.75,    gap=dt.timedelta(seconds=2)),
        Effect(dt.timedelta(minutes=2, seconds=35),         Voice.JENNY_WHISPER,        rate=0,     pitch=-20,    volume=0.75,    gap=dt.timedelta(seconds=1.5)),
        Effect(dt.timedelta(minutes=2, seconds=53),         Voice.JENNY_WHISPER,        rate=10,    pitch=-20,    volume=0.75,    gap=dt.timedelta(seconds=0.8)),
        Effect(dt.timedelta(minutes=3, seconds=24),         Voice.JENNY_UNFRIENDLY,     rate=0,     pitch=-20,    volume=1,       gap=dt.timedelta(seconds=0.8)),
        Effect(dt.timedelta(minutes=3, seconds=53),         Voice.JENNY_WHISPER,        rate=10,    pitch=-20,    volume=1,       gap=dt.timedelta(seconds=1)),
    ]


def get_fake_posts():
    return [
        'So excited to finally be here after 2 years away, it’s giving me life! PS what am I even doing in this photo?!',
        'Cocktails with my besties after what’s been a pretty scary time. I wont go into it too much here but will download with you all IRL soon. 🍸💖',
        'Ready for an adventure. Reading some classics. Writing some poems. Looking for hotties. ✈🚆 #Europe #travel #instatravel #picoftheday #travelphotography #travelgram #girlsontour',
        'Last night was so crazy omg. Someone please remind me that tables are not podiums 🙈',
        'Can’t believe it’s my last day here! Congratulations to everyone on graduating and here’s to changing the world! Let’s break apart this capitalist machine together. But after my holiday please. Love every single one of you, thank you for being part of my journey and thanks for letting me be part of yours. ❤ See you crazy kids later woohoo #graduation #byronbaes #wasted #beachlyfe #qualified',
        'We are giving strong Romeo and Juliet vibes here. 🍆🍑',
        'So devastated. Have. No. Words. I’ll miss you forever. 💔💔💔',
        'Little thirst trap for your Monday morning 💦',
        'Please donate. Link in bio. PS. I had the incredible honour of meeting this community in person and they are so, so, so amazing.',
        'You are being very wtf and I need you to be lol.',
        'I’m having a mini-socials break. DM me if you want to catch up.',
        '😘🍹❤💃',
        'I did it, i\'m chasing waterfalls #travel #waterfalls #TLC',
        'the goodest boy, the bestest puperoonie 🥰🥰',
        'THEY ASKED AND I SAID YES!! Cant wait to spend forever with my best friend! Heres to the next chapter of our lives!! 💍❤',
        'Up the bombers!!!! Yehooo #mcg #footy',
        'Happy mothers day to the woman who made me. The creator of the worlds best mac and cheese, my first ever uber driver, my shoulder to cry on, my rock and my greatest supporter. I love you mum, thank you for everything you\'ve done for me. Can\'t wait to spoil you today ❤',
        'Living my best life 🌴🍹 #travel #islandlife #fiji #beach #cocktail'
    ]
