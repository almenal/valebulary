#!/usr/bin/env python
# coding: utf-8

# In[1]:


import PyPDF2, re, pickle
import pandas as pd
from wordentry import WordEntry, Session

# In[2]:


magoosh_fn = 'magoosh-gre-1000-words_oct01.pdf' 
prepscholar_fn = 'PrepScholar-GRE-vocab-parts-of-speech.pdf'

magoosh_wrap = open(magoosh_fn, 'rb') 
#prepscho_wrap = open(prepscholar_fn, 'rb') 


# In[3]:


magoosh_reader = PyPDF2.PdfFileReader(magoosh_wrap)
magoosh_pages = [magoosh_reader.getPage(i).extractText() for i in range(magoosh_reader.numPages)]

#prepscho_reader = PyPDF2.PdfFileReader(prepscho_wrap)
#prepscho_pages = [prepscho_reader.getPage(i).extractText() for i in range(prepscho_reader.numPages)]


# # Importing Magoosh vocabulary

# In[4]:


sections = []
for index in range(len(magoosh_pages)):
    match = re.search(r'.+?\s+?Word', magoosh_pages[index])
    if match:
        sections.append(index)
sections


# ## First let's assume that the structure of each page is similar and we can divide blocks regularly

# In[5]:


vocabulary = pd.Series()
exceptions = []
# Section 1 - Common
for p in range(sections[0], sections[1]):
    text = magoosh_pages[p].split('\n \n \n')
    for line in text:
        blocks = line.split('\n \n')
        try:
            word = blocks[0].strip().replace('\n', '')
            category_meaning = blocks[1].split('\n):')
            category = category_meaning[0][1:].strip().replace('\n', '')
            meaning = category_meaning[1].strip().replace('\n', '')
            example = blocks[2].replace('\n', '')
            Word = WordEntry(word=word, category=category,
                            meaning=meaning, example=example, difficulty="Common")
            vocabulary = vocabulary.append( pd.Series({word:Word}) )
        except:
            exceptions.append(line)
            
# Section 2 - Basic
for p in range(sections[1], sections[2]):
    text = magoosh_pages[p].split('\n \n \n')
    for line in text:
        blocks = line.split('\n \n')
        try:
            word = blocks[0].strip().replace('\n', '')
            category_meaning = blocks[1].split('\n):')
            category = category_meaning[0][1:].strip().replace('\n', '')
            meaning = category_meaning[1].strip().replace('\n', '')
            example = blocks[2].replace('\n', '')
            Word = WordEntry(word=word, category=category,
                            meaning=meaning, example=example, difficulty="Basic")
            vocabulary = vocabulary.append( pd.Series({word:Word}) )
        except:
            exceptions.append(line)

# Section 3 - Advanced
for p in range(sections[2], magoosh_reader.numPages):
    text = magoosh_pages[p].split('\n \n \n')
    for line in text:
        blocks = line.split('\n \n')
        try:
            word = blocks[0].strip().replace('\n', '')
            category_meaning = blocks[1].split('\n):')
            category = category_meaning[0][1:].strip().replace('\n', '')
            meaning = category_meaning[1].strip().replace('\n', '')
            example = blocks[2].replace('\n', '')
            Word = WordEntry(word=word, category=category,
                            meaning=meaning, example=example, difficulty="Advanced")
            vocabulary = vocabulary.append( pd.Series({word:Word}) )
        except:
            exceptions.append(line)
    
# ## Let's deal with the incorrect ones and detect patterns

# In[6]:


newlength = 1
oldlength = len(exceptions)
# Since remove only removes the first occurrence of an item, we iterate until 
# all occurrences of each items have been removed
while newlength != oldlength:
    oldlength = len(exceptions)
    for item in exceptions:
        if item in ['gre.magoosh.com/flashcards', '', ' ']:
            exceptions.remove(item)
    newlength = len(exceptions)


# In[7]:


newlength = 1
oldlength = len(exceptions)
while newlength != oldlength:
    oldlength = len(exceptions)
    for line in exceptions:
        try:
            for word in vocabulary.keys():
                if word in line:
                    vocabulary[word].example = line.replace('\n', '')
                    exceptions.remove(line)
                    break
        except:
            pass
    newlength = len(exceptions)

# In[8]:


# Additions

vocabulary = vocabulary.append( pd.Series( {'malapropism': 
    WordEntry(word='malapropism', category='noun', difficulty='Advanced', is_known=False,
            meaning='the confusion of a word with another word that sounds similar',
            example='Whenever I looked glum, my mother would offer to share "an amusing antidote" with me--an endearing malapropism of "anecdote" that never failed to cheer me up')})
)

vocabulary = vocabulary.append( pd.Series( {'aboveboard': 
    WordEntry(word='aboveboard', category='adjective', difficulty='Basic', is_known=False,
        meaning='open and honest',
        example='The mayor, despite his avuncular face plastered about the city, was hardly aboveboard -- some concluded that it was his ingratiating smile that allowed him to engage in corrupt behavior and get away with it')})
)

vocabulary = vocabulary.append( pd.Series( {'innocuous': 
    WordEntry(word='innocuous', category='adjective', difficulty='Basic', is_known=False,
             meaning='harmless and doesn"t produce any ill effects',
             example='Everyone found Nancys banter innocuous--except for Mike, who felt like she was intentionally picking on him')
                                         })
)

vocabulary = vocabulary.append( pd.Series( {'contemptuous': 
    WordEntry(word='contemptuous', category='adjective', difficulty='Basic', is_known=False,
             meaning='scornful, looking down at\n others with a sneering attitude',
             example='Always on the forefront of fashion, Vanessa looked contemptuously at anyone wearing dated clothing.')
                                          })
)

vocabulary = vocabulary.append( pd.Series( {'profusion': 
    WordEntry(word='profusion', category='noun', difficulty='Basic', is_known=False,
             meaning='the property of being extremely abundant',
             example='When Maria reported that she had been visited by Jesus Christ and had proof, a profusion of reporter and journalists descended on the town')
                                         })
)

vocabulary = vocabulary.append( pd.Series( {'profusion': 
    WordEntry(word='profusion', category='noun', difficulty='Basic', is_known=False,
             meaning='the property of being extremely abundant',
             example='When Maria reported that she had been visited by Jesus Christ and had proof, a profusion of reporter and journalists descended on the town')
                                          })
)

vocabulary = vocabulary.append( pd.Series( {'whimsical': 
    WordEntry(word='whimsical', category='adjective', difficulty='Advanced', is_known=False,
            meaning='determined by impulse or whim rather than by necessity or reason',
            example='Adults look to kids and envy their whimsical nature at times, wishing that they could act without reason and play without limitation')
                                         })
)


# Corrections
vocabulary['ascribe'].example='History ascribes The Odyssey and The Illiad to Homer, but scholars now debate whether he was a historical figure or a fictitious name'
vocabulary['incorrigible'].example='Tom Sawyer seems like an incorrigible youth until Huck Finn enters the novel; even Sawyer can\'t match his fierce individual spirit'
vocabulary['subsume'].iloc[1].meaning='consider (an instance of something) as part of a general rule or principle'
vocabulary['subsume'].iloc[1].example='Don Quixote of La Mancha subsumes all other modern novels, demonstrating modern literary devices and predating even the idea of a postmodern, metanarrative'
vocabulary['serendipity'].example+='idea was looking for a strong adhesive; the weak adhesive he came up with was perfect for holding a piece of paper in place but made it very easy for so'  
vocabulary['catholic'].example +='he enjoyed music from countries as far-flung as Mali and Mongolia'
vocabulary['denote'].example = "Even if the text is not visible, the red octagon denotes \"stop\" to all motorists in America."


# ## Finally, export vocabulary object as a csv
pickle.dump(vocabulary, open('vocabulary.obj', 'wb'))
pickle.dump(Session(vocabulary), open('master_session.obj', 'wb'))

