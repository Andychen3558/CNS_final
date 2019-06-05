### to use the embedding model:

from embedding import Embedding
vecfile = 'embedding/wiki.zh.vec.small'
model = Embedding.Embedding(vecfile)

### model.invocab(word)
* check if a word exists in vocabulary
* if exists, return True; else, False

### model.get_options(word)
* if word not in vocabulary, return None
* else return a dictionary contain 9 choices
* every choices is also a dictionary structure
* structure:
	[word]: {
		"url": [URL],
		"name": [word],
		"score": [similarity]
	}