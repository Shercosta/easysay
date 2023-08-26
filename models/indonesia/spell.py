import json
import pandas as pd

with open('slang.dic') as f:
    slang = json.load(f)

kamus_slang = pd.read_json('slang.dic',typ = 'series')
pd.DataFrame(kamus_slang.items(), columns = ['contraction', 'original']).head()
contractions_list = list(kamus_slang.keys())

def spell_check(text):
    words = []
    for word in text.split():
        if word in contractions_list:
            words = words + kamus_slang[word].split()
        else:
            words = words + word.split()
    
    text_converted = " ".join(words)
    return text_converted