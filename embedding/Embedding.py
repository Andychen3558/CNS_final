
# coding: utf-8

# In[1]:


import gensim
import random
import json
from .request_img import get_img


# In[2]:


class Embedding():
    def __init__(self, wordfile, cache_url=None):
        self.model = gensim.models.KeyedVectors.load_word2vec_format(wordfile)
        if cache_url:
            with open(cache_url, 'r') as f:
                self.cache_url = json.load(f)
        else:
            self.cache_url = {}
        self.postopn = 50 # choise topn of positive words
        self.posrann = 1 # sample n from above
        self.posmask = 10 # avoid topn
        self.negtopn = 0 # choise topn of negative words
        self.negrann = 0 # sample n from above


    def invocab(self, word):
        return word in self.model.vocab
    
    def get_options(self, word, opt_num=9, get_url=False): # default opt_num = 9
        # check word exists in vocab
        if not self.invocab(word):
            return None
        
        # select positive keys
        high = self.model.most_similar(positive=[word], topn=self.postopn)
        highkeys = [high[i][0] for i in range(self.posmask, self.postopn)]
        choice = random.sample(highkeys, self.posrann)

        # # select negative keys
        # neg = self.model.most_similar(negative=[word], topn=self.negtopn)
        # negkeys = [neg[i][0] for i in range(self.negtopn)]
        # choice.extend(random.sample(negkeys, self.negrann))
        
        # random select keys
        keys = self.model.vocab.keys()
        otherkeys = random.sample(keys, opt_num-self.posrann-self.negrann)
        choice.extend(otherkeys)

        # high = self.model.most_similar(positive=[word], topn=self.postopn2)
        # highkeys = [high[i][0] for i in range(self.posmask, self.postopn2)]
        # choice = random.sample(highkeys, self.posrann2)
        
        #shuffel keys
        random.shuffle(choice)
        
        choice_dic = {}
        
        for i in choice:

            url = ''
            if get_url:
                url = self.cache_url[i] if i in self.cache_url else get_img(i)

            choice_dic[i] = {
                "url": url,
                "score": self.model.similarity(word, i),
                "name": i
            }
            
        return choice_dic
    
    def get_options_by_size(self, word, opt_num, subw_num, get_url=False):
        choice = self.get_options(word, opt_num, get_url=get_url)
        keys = self.model.vocab.keys()
        otherkeys = random.sample(keys, opt_num*(subw_num-1))
        index = 0
        choice_list = []

        for i in choice:
            subw_list = [choice[i]]
            for j in range(subw_num-1):

                url = ''
                if get_url:
                    url = self.cache_url[i] if i in self.cache_url else get_img(i)
                
                subw_list.append({
                    "url": url,
                    "score": self.similarity(word, otherkeys[index]),
                    'name': otherkeys[index]
                })

                index += 1
            random.shuffle(subw_list)
            choice_list.append(subw_list)
        
        return choice_list

    def similarity(self, w1, w2):
        if not self.invocab(w1) or not self.invocab(w2):
            return None
        return self.model.similarity(w1, w2)
# gensim example:          
# sim = m.model.most_similar(positive=['貴族', '女人'], negative=['男人'], topn=1000)
# sim = [(i,m.model.vocab[i[0]].count) for i in sim]

# m.model.similarity('大量', '分類')

# m.model.doesnt_match('歌手')


# In[3]:


# m = Embedding('wiki.en.vec.small')


# In[4]:


# print(m.get_options('bird'))


# In[11]:


# m.model.vocab['bird'].count


# In[5]:


# m.similarity('bird', 'tree')

