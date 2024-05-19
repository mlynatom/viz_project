import os
from typing import List, Literal, Union

import numpy as np
from sklearn.decomposition import NMF
from sklearn.decomposition import PCA  # TODO write own
from sklearn.manifold import TSNE
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.decomposition import LatentDirichletAllocation
from umap import UMAP

SEED = 42

class DocumentData():
    """
    Class to load and process the data from the document files
    """
    def __init__(self, data_path:str, name:str) -> None:
        self.name = name
        self.vocab_path = os.path.join(data_path, f"vocab.{self.name}.txt")
        self.docword_path = os.path.join(data_path, f"docword.{self.name}.txt")
        self.vocabulary = self._load_vocabulary()
        self.doc_words_matrix = self._load_docwords()
        self.total_term_counts = self._total_term_counts(self.doc_words_matrix)
        self.sum_word_counts = np.sum(self.total_term_counts)
        #self.document_words_sum = self._number_of_words_per_doc(self.doc_words_matrix)
        self.tfidf_matrix = TfidfTransformer().fit_transform(self.doc_words_matrix)
        self.selected_documents = []

    def fit_transform(self, solver: Union[Literal["pca"], Literal["umap"], Literal["tsne"]]):
        """
        Fit and transform the data using the specified solver
        """
        if solver == "pca":
            try:
                pca_res = np.load(f"./precomputed/{self.name}_pca.npy")
            except:
                pca_res = self._pca()
                #np.save(f"./precomputed/{self.name}_pca.npy", pca_res) #we do not need to precompute PCA

            return pca_res
        elif solver == "tsne":
            try:
                tsne_res = np.load(f"./precomputed/{self.name}_tsne.npy")
            except:
                tsne_res = TSNE(n_components=2, init="random", random_state=SEED).fit_transform(self.tfidf_matrix)
                np.save(f"./precomputed/{self.name}_tsne.npy", tsne_res)

            return tsne_res
        elif solver == "umap":
            try:
                umap_res = np.load(f"./precomputed/{self.name}_umap.npy")
            except:
                umap_res = UMAP(n_components=2).fit_transform(self.tfidf_matrix)
                np.save(f"./precomputed/{self.name}_umap.npy", umap_res)

            return umap_res
        else:
            raise ValueError("Invalid solver")
        
    def fit_topics(self, solver: Union[Literal["nmf"], Literal["lda"]], n_components:int = 10):
        """
        Fit the topics using the specified solver
        """
        if solver == "nmf":
            try:
                doc_topics = np.load(f"./precomputed/{self.name}_nmf_{n_components}_doc_topics.npy")
                topics = np.load(f"./precomputed/{self.name}_nmf_{n_components}_topics.npy")
            except:
                doc_topics, topics = self._nmf(n_components=n_components)
            return doc_topics, topics
        elif solver == "lda":
            try:
                doc_topics = np.load(f"./precomputed/{self.name}_lda_{n_components}_doc_topics.npy")
                topics = np.load(f"./precomputed/{self.name}_lda_{n_components}_topics.npy")
            except:
                doc_topics, topics = self._lda(n_components=n_components)
                np.save(f"./precomputed/{self.name}_lda_{n_components}_doc_topics.npy", doc_topics)
                np.save(f"./precomputed/{self.name}_lda_{n_components}_topics.npy", topics)


            return doc_topics, topics
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
        #TODO write own
        pca = PCA(n_components=2, svd_solver="arpack")
        return pca.fit_transform(self.tfidf_matrix)
    
    def _nmf(self, n_components:int = 10):
        nmf = NMF(n_components=n_components, random_state=SEED)
        W_matrix = nmf.fit_transform(self.tfidf_matrix) # document X topics matrix
        H_matrix = nmf.components_ # topics X words matrix

        topics = np.argmax(W_matrix, axis=1)

        return topics, H_matrix
    
    def _lda(self, n_components:int = 10):
        lda = LatentDirichletAllocation(n_components=n_components, random_state=SEED)
        X_new = lda.fit_transform(self.doc_words_matrix)
        topics = np.argmax(X_new, axis=1)

        return topics, lda.components_

    def get_topics_words(self, topic_words_matrix, n:int = 5) -> List[List[str]]:
        """
        Get the top n words for each topic which are the most representative
        """
        topics_words = []

        for i in range(topic_words_matrix.shape[0]):
            ind =  np.argpartition(topic_words_matrix[i, :], -n)[-n:]

            words = [self.vocabulary[word_id] for word_id in ind]
            topics_words.append(words)

        return topics_words

    def get_words_best_topic(self, words_idx, topic_words_matrix) -> int:
        return np.argmax(topic_words_matrix[:, words_idx])

    def _total_term_counts(self, doc_words):
        return np.sum(doc_words, axis=0)

    def _number_of_words_per_doc(self, doc_words):
        return np.sum(doc_words, axis=1)

    def compute_g2(self, selected_documents = None):
        """
        https://dl.acm.org/doi/pdf/10.3115/1117729.1117730
        We use it not to compare two documents, but selected documents to unselected documents.
        Used smoothing (added one everywhere), to prevent division by zero
        #todo vectorize
        """

        if selected_documents is None:
            selected_documents = self.selected_documents

        unselected_documents_mask = np.ones(self.doc_words_matrix.shape[0], dtype=bool)
        unselected_documents_mask[selected_documents] = False



        term_counts_selected = self._total_term_counts(self.doc_words_matrix[selected_documents])
        term_counts_unselected = self._total_term_counts(self.doc_words_matrix[unselected_documents_mask])
        total_words_selected = np.sum(term_counts_selected)
        total_words_unselected = np.sum(term_counts_unselected)

        log_likelihoods = np.empty((self.doc_words_matrix.shape[1]))
        for word in range(self.doc_words_matrix.shape[1]):
            expected_value_selected = (self.total_term_counts[word] * total_words_selected +1)/self.sum_word_counts
            expected_value_unselected = (self.total_term_counts[word] * total_words_unselected +1)/self.sum_word_counts
            log_likelihoods[word] = 2* (term_counts_selected[word] * np.log((term_counts_selected[word]+1)/expected_value_selected) +
                                term_counts_unselected[word] * np.log((term_counts_unselected[word]+1) / expected_value_unselected))

        return log_likelihoods
