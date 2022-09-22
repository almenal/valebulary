#!/usr/bin/env python
# coding: utf-8

import PyPDF2, re, pickle
import pandas as pd
from pathlib import Path
from wordentry import WordEntry, Session

here = Path(__file__).parent

def main():
    magoosh_reader, magoosh_pages, magoosh_wrap = retrieve_pages()
    sections = fetch_sections(magoosh_pages)
    vocab_draft, wrong_words = build_vocabulary_draft(sections, 
                                                      magoosh_reader,
                                                      magoosh_pages)
    vocab_corr = address_incorrect_words(vocab_draft, wrong_words)
    vocab_corr_2 = post_hoc_additions(vocab_corr)
    vocab_corr_3 = post_hoc_corrections(vocab_corr_2)
    export(vocab_corr_3)
    magoosh_wrap.close()


def retrieve_pages():
    magoosh_fn = here.parent / 'data' / 'magoosh-gre-1000-words_oct01.pdf' 
    magoosh_wrap = open(magoosh_fn, 'rb') 
    magoosh_reader = PyPDF2.PdfFileReader(magoosh_wrap)
    magoosh_pages = [magoosh_reader.getPage(i).extractText() 
                    for i in range(magoosh_reader.numPages)]
    return magoosh_reader, magoosh_pages, magoosh_wrap

def fetch_sections(pages):
    # Importing Magoosh vocabulary
    sections = []
    for index in range(len(pages)):
        match = re.search(r'.+?\s+?Word', pages[index])
        if match:
            sections.append(index)
    return sections

def build_vocabulary_draft(sections, magoosh_reader, magoosh_pages):
    page_ranges = [
       (sections[0], sections[1]),
       (sections[1], sections[2]),
       (sections[2], magoosh_reader.numPages),
    ]
    difficulties = ["Common", "Basic", "Advanced"]
    vocabulary = {}
    exceptions = []
    for (start,stop), difficulty in zip(page_ranges, difficulties):
        vocab, excpt = scrape_vocabulary(start, stop, magoosh_pages, difficulty)
        vocabulary.update(vocab)
        exceptions.extend(excpt)
    return vocabulary, exceptions

def scrape_vocabulary(start, stop, pages, difficulty="Common"):
    # First let's assume that the structure of each page is similar 
    # and we can divide blocks regularly
    vocabulary = {}
    exceptions = []
    for p in range(start, stop):
        text = pages[p].split('\n \n \n')
        for line in text:
            blocks = line.split('\n \n')
            try:
                word = blocks[0].strip().replace('\n', '')
                category_meaning = blocks[1].split('\n):')
                category = category_meaning[0][1:].strip().replace('\n', '')
                meaning = category_meaning[1].strip().replace('\n', '')
                example = blocks[2].replace('\n', '')
                Word = WordEntry(
                    word=word, 
                    category=category,
                    meaning=meaning, 
                    example=example, 
                    difficulty=difficulty
                )
                # vocabulary =  vocabulary.append( pd.Series({word:Word}) )
                vocabulary[word] = Word
            except:
                exceptions.append(line)
    return vocabulary, exceptions

def address_incorrect_words(vocab_draft, incorrect_words):
    vocab_corr = vocab_draft.copy()
    # Let's deal with the incorrect ones and detect patterns
    newlength = 1
    oldlength = len(incorrect_words)
    # Since remove only removes the first occurrence of an item, we iterate until 
    # all occurrences of each items have been removed
    while newlength != oldlength:
        oldlength = len(incorrect_words)
        for item in incorrect_words:
            if item in ['gre.magoosh.com/flashcards', '', ' ']:
                incorrect_words.remove(item)
        newlength = len(incorrect_words)

    newlength = 1
    oldlength = len(incorrect_words)
    while newlength != oldlength:
        oldlength = len(incorrect_words)
        for line in incorrect_words:
            try:
                for word in vocab_corr.keys():
                    if word in line:
                        vocab_corr[word].example = line.replace('\n', '')
                        incorrect_words.remove(line)
                        break
            except:
                pass
        newlength = len(incorrect_words)
    return

def post_hoc_additions(vocabulary):
    # Post-hoc manual additions
    vocabulary.update( {'malapropism': 
        WordEntry(
            word='malapropism', category='noun', difficulty='Advanced', is_known=False,
            meaning='the confusion of a word with another word that sounds similar',
            example='Whenever I looked glum, my mother would offer to share "an amusing antidote" with me--an endearing malapropism of "anecdote" that never failed to cheer me up'
        )}
    )
    vocabulary.update( {'aboveboard': 
        WordEntry(
            word='aboveboard', category='adjective', difficulty='Basic', is_known=False,
            meaning='open and honest',
            example='The mayor, despite his avuncular face plastered about the city, was hardly aboveboard -- some concluded that it was his ingratiating smile that allowed him to engage in corrupt behavior and get away with it'
        )}
    )
    vocabulary.update( {'innocuous': 
        WordEntry(
            word='innocuous', category='adjective', difficulty='Basic', is_known=False,
            meaning='harmless and doesn"t produce any ill effects',
            example='Everyone found Nancys banter innocuous--except for Mike, who felt like she was intentionally picking on him'
        )}
    )
    vocabulary.update( {'contemptuous': 
        WordEntry(
            word='contemptuous', category='adjective', difficulty='Basic', is_known=False,
            meaning='scornful, looking down at\n others with a sneering attitude',
            example='Always on the forefront of fashion, Vanessa looked contemptuously at anyone wearing dated clothing.'
        )}
    )
    vocabulary.update( {'profusion': 
        WordEntry(
            word='profusion', category='noun', difficulty='Basic', is_known=False,
            meaning='the property of being extremely abundant',
            example='When Maria reported that she had been visited by Jesus Christ and had proof, a profusion of reporter and journalists descended on the town'
        )}
    )
    vocabulary.update( {'profusion': 
        WordEntry(
            word='profusion', category='noun', difficulty='Basic', is_known=False,
            meaning='the property of being extremely abundant',
            example='When Maria reported that she had been visited by Jesus Christ and had proof, a profusion of reporter and journalists descended on the town'
        )}
    )
    vocabulary.update( {'whimsical': 
        WordEntry(
            word='whimsical', category='adjective', difficulty='Advanced', is_known=False,
            meaning='determined by impulse or whim rather than by necessity or reason',
            example='Adults look to kids and envy their whimsical nature at times, wishing that they could act without reason and play without limitation'
        )}
    )
    return vocabulary
    
def post_hoc_corrections(vocabulary):
    # Corrections
    vocabulary['ascribe'].example='History ascribes The Odyssey and The Illiad to Homer, but scholars now debate whether he was a historical figure or a fictitious name'
    vocabulary['incorrigible'].example='Tom Sawyer seems like an incorrigible youth until Huck Finn enters the novel; even Sawyer can\'t match his fierce individual spirit'
    vocabulary['subsume'].iloc[1].meaning='consider (an instance of something) as part of a general rule or principle'
    vocabulary['subsume'].iloc[1].example='Don Quixote of La Mancha subsumes all other modern novels, demonstrating modern literary devices and predating even the idea of a postmodern, metanarrative'
    vocabulary['serendipity'].example+='idea was looking for a strong adhesive; the weak adhesive he came up with was perfect for holding a piece of paper in place but made it very easy for so'  
    vocabulary['catholic'].example +='he enjoyed music from countries as far-flung as Mali and Mongolia'
    vocabulary['denote'].example = "Even if the text is not visible, the red octagon denotes \"stop\" to all motorists in America."
    return vocabulary

def export(vocabulary):
    # ## Finally, export vocabulary object as a pickle
    with open(here.parent / 'assets' / 'vocabulary.obj', 'wb') as f:
        pickle.dump(vocabulary, f)
    
    with open(here.parent / 'assets' / 'master_session.obj', 'wb') as f:
        pickle.dump(Session(vocabulary), f)

if __name__ == "__main__":
    main()
