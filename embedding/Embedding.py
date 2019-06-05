
# coding: utf-8

# In[15]:


import gensim
import random
from .request_img import get_img


# In[16]:


class Embedding():
    def __init__(self, wordfile):
        self.model = gensim.models.KeyedVectors.load_word2vec_format(wordfile)
        self.postopn = 50 # choise topn of positive words
        self.posrann = 2 # sample n from above
        self.posmask = 5 # avoid topn
        self.negtopn = 100 # choise topn of negative words
        self.negrann = 4 # sample n from above
        self.optionn = 9 # total choice num
        
    def invocab(self, word):
        return word in self.model.vocab
    
    def get_options(self, word):
        
        # check word exists in vocab
        if not self.invocab(word):
            return None
        
        # select positive keys
        high = self.model.most_similar(positive=[word], topn=self.postopn)
        highkeys = [high[i][0] for i in range(self.posmask, self.postopn)]
        choice = random.sample(highkeys, self.posrann)

        # select negative keys
        neg = self.model.most_similar(negative=[word], topn=self.negtopn)
        negkeys = [neg[i][0] for i in range(self.negtopn)]
        choice.extend(random.sample(negkeys, self.negrann))
        
        # random select keys
        keys = self.model.vocab.keys()
        otherkeys = random.sample(keys, self.optionn-self.posrann-self.negrann)
        choice.extend(otherkeys)
        
        #shuffel keys
        random.shuffle(choice)
        
        choice_dic = {}
        for i in choice:
            choice_dic[i] = {
                "url": get_img(i),
                "score": self.model.similarity(word, i),
                "name": i
            }
            
        return choice_dic
    
# gensim example:          
# sim = m.model.most_similar(positive=['貴族', '女人'], negative=['男人'], topn=1000)
# sim = [(i,m.model.vocab[i[0]].count) for i in sim]

# m.model.similarity('大量', '分類')

# m.model.doesnt_match('歌手')


# In[17]:


# m = Embedding('wiki.zh.vec.small')


# In[18]:


# print(m.get_options('音樂'))

