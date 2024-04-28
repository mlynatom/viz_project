import os
from typing import List, Literal, Union

import numpy as np
from sklearn.decomposition import NMF  # TODO write own
from sklearn.decomposition import PCA  # TODO write own
from sklearn.feature_extraction.text import TfidfTransformer

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
    
    def nmf(self, n_components:int = 10, num_topic_words: int = 5):
        nmf = NMF(n_components=n_components, random_state=SEED)
        W_matrix = nmf.fit_transform(self.tfidf_matrix) # document X topics matrix
        H_matrix = nmf.components_ # topics X words matrix

        topics_nmf = np.argmax(W_matrix, axis=1)
        topics_words = self._get_topics_words(H_matrix, num_topic_words)

        return topics_nmf, topics_words

    def _get_topics_words(self, topic_words_matrix, n:int = 5) -> List[List[str]]:
        topics_words = []

        for i in range(topic_words_matrix.shape[0]):
            ind =  np.argpartition(topic_words_matrix[i, :], -n)[-n:]

            words = [self.vocabulary[word_id] for word_id in ind]
            topics_words.append(words)

        return topics_words 