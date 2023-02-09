import hashlib
import time
import random
import string
import uuid

alphabets = "([A-Za-z])"
prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
suffixes = "(Inc|Ltd|Jr|Sr|Co)"
starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
websites = "[.](com|net|org|io|gov)"


def split_into_sentences(text):
    text = " " + text + "  "
    text = text.replace("\n", " ")
    text = text.replace("\r", "")
    # text = re.sub(prefixes,"\\1<prd>",text)
    # text = re.sub(websites,"<prd>\\1",text)
    # if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")
    # text = re.sub("\s" + alphabets + "[.] "," \\1<prd> ",text)
    # text = re.sub(acronyms+" "+starters,"\\1<stop> \\2",text)
    # text = re.sub(alphabets + "[.]" + alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
    # text = re.sub(alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>",text)
    # text = re.sub(" "+suffixes+"[.] "+starters," \\1<stop> \\2",text)
    # text = re.sub(" "+suffixes+"[.]"," \\1<prd>",text)
    # text = re.sub(" " + alphabets + "[.]"," \\1<prd>",text)
    # if "”" in text: text = text.replace(".”","”.")
    # if "\"" in text: text = text.replace(".\"","\".")
    # if "!" in text: text = text.replace("!\"","\"!")
    # if "?" in text: text = text.replace("?\"","\"?")
    text = text.replace(". ", ".<stop>")
    text = text.replace("? ", "?<stop>")
    text = text.replace("! ", "!<stop>")
    text = text.replace(": ", ":<stop>")
    text = text.replace("; ", ";<stop>")
    # text = text.replace("<prd>", ".")
    sentences = text.split("<stop>")
    # sentences = sentences[:-1]
    sentences = [s.strip() for s in sentences]
    return sentences


TRIM_LENGTH_FIRST = 350
TRIM_LENGTH = 225
# TRIM_NEW_LINE = True


def random_string():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))


def trim(text, trim_length):
    # if TRIM_NEW_LINE:
    #     text = text.replace('\\r\\n', '. ')
    #     text = text.replace('\\n', '. ')
    # if trim_length == -1:
    #     return text
    return (text[:trim_length] + '...') if len(text) > trim_length else text


def get_snippet(text):
    sentences = split_into_sentences(text)
    txt_print = sentences.pop(0)

    if len(txt_print) > TRIM_LENGTH_FIRST:
        txt_print = trim(txt_print, TRIM_LENGTH_FIRST)

    else:
        while len(sentences):
            txt_new = sentences.pop(0)
            if len(txt_print) + len(txt_new) > TRIM_LENGTH:
                break
            else:
                txt_print += ' ' + txt_new

    return txt_print


def generate_uuid() -> str:
    return f'{uuid.uuid4()}'


def generate_android_device_id() -> str:
    return "android-%s" % hashlib.sha256(str(time.time()).encode()).hexdigest()[:16]








if __name__ == '__main__':
    print(get_snippet("""Faux Mo House party edition was a vibe.

Made possible by excellence of all the artists: @ayebatonye__, Amy Russell and Co, @ambermccartneyy, @al3xarmani , @doompuff, @lovebettyapple , @emsanzaro, @matspiz, @nonchalantflowerboy, @gabecomerford , Grace Ovens, @hannahbronte, @qespeaks, @the.ana.thema, @jenlarge, Joe Weller, @kkatdaddi, @ihatekilimi, @kyall_shanks, @keia_mc , L$F, @ledlaser, @loren_rubicana + hosting, @mamadeleche, @fullyautom8edluxurycannibalism, @martyjaybird, @medhanitbarratt, @misty_delray, @mikaelelel, @whoneedsbuddy, @krazykosmickid,@nicfarrow, @nunami.xx, @pussaypoppins, @dancepointetas, @rosaxrita, @milquebarth, @samorasquid, Stevie Mcentee, Spike Mason, @tasdance, @twinsticks_ , @froggyantbear + TaikoOni drummers.

Design & architecture @champ.co Build by @soda_projects_tas

Produced by @dexter_rosengrave @fragilityzone
Production managed by @roise_poidd Staged managed by @casa_blanca1, @hera_fox_tas @notlikethecheeze Tech by @alive_entertainment
Digital by Exhibitionist
Costume by Tori Bell and UTAS Design and Architecture students


Curated and directed by @jrbrennanx and I.

Brought to you by the one and only @monafoma and @monamuseum . 📸 @jessehunniford Special mention @lianadelcray #fauxmo #monafoma #mona #disco
"""))