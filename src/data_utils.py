import os
from typing import List, Literal, Union

import numpy as np
from sklearn.decomposition import NMF  # TODO write own
from sklearn.decomposition import PCA  # TODO write own
from sklearn.manifold import TSNE
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.decomposition import LatentDirichletAllocation

SEED = 42

class DocumentData():
    def __init__(self, data_path:str, name:str) -> None:
        self.vocab_path = os.path.join(data_path, f"vocab.{name}.txt")
        self.docword_path = os.path.join(data_path, f"docword.{name}.txt")
        self.vocabulary = self._load_vocabulary()
        self.doc_words_matrix = self._load_docwords()
        self.tfidf_matrix = TfidfTransformer().fit_transform(self.doc_words_matrix)
        
    def fit_transform(self, solver: Union[Literal["pca"], Literal["umap"], Literal["tsne"]]):
        if solver == "pca":
            return self._pca()
        elif solver == "tsne":
            return TSNE(n_components=2, init="random", random_state=SEED).fit_transform(self.tfidf_matrix)
        elif solver == "umap":
            #TODO
            raise NotImplementedError("UMAP not implemented yet")
        else:
            raise ValueError("Invalid solver")
        
    def fit_topics(self, solver: Union[Literal["nmf"], Literal["lda"]], n_components:int = 10, num_topic_words: int = 5):
        if solver == "nmf":
            return self._nmf(n_components=n_components, num_topic_words=num_topic_words)
        elif solver == "lda":
            return self._lda(n_components=n_components, num_topic_words=num_topic_words)
        else:
            raise ValueError("Invalid solver")


    def _load_vocabulary(self) -> List[str]:
        vocabulary = []
        with open(self.vocab_path, "r") as f:
            for line in f:
                vocabulary.append(line.strip("\n"))

        return vocabulary
    

    def _load_docwords(self) -> np.ndarray:
        with open(self.docword_path, "r") as f:
            self.n_docs = int(f.readline().strip())
            self.n_words = int(f.readline().strip())
            self.n_nonzero_counts = int(f.readline().strip())

            counts_matrix = np.zeros((self.n_docs, self.n_words))
            for line in f:
                split_line = line.strip().split(" ")
                counts_matrix[int(split_line[0])-1,
                              int(split_line[1])-1] = int(split_line[2])

        return counts_matrix
    
    def _pca(self):
        pca = PCA(n_components=2, svd_solver="arpack")
        return pca.fit_transform(self.tfidf_matrix)
    
    def _nmf(self, n_components:int = 10, num_topic_words: int = 5):
        nmf = NMF(n_components=n_components, random_state=SEED)
        W_matrix = nmf.fit_transform(self.tfidf_matrix) # document X topics matrix
        H_matrix = nmf.components_ # topics X words matrix

        topics = np.argmax(W_matrix, axis=1)

        return topics, H_matrix
    
    def _lda(self, n_components:int = 10, num_topic_words: int = 5):
        lda = LatentDirichletAllocation(n_components=n_components, random_state=SEED)
        X_new = lda.fit_transform(self.doc_words_matrix)
        topics = np.argmax(X_new, axis=1)

        return topics, lda.components_

    def get_topics_words(self, topic_words_matrix, n:int = 5) -> List[List[str]]:
        topics_words = []

        for i in range(topic_words_matrix.shape[0]):
            ind =  np.argpartition(topic_words_matrix[i, :], -n)[-n:]

            words = [self.vocabulary[word_id] for word_id in ind]
            topics_words.append(words)

        return topics_words 