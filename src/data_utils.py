import numpy as np
from typing import List

def load_vocabulary(path:str="data/bag+of+words/vocab.kos.txt") -> List[str]:
    vocabulary = []
    with open(path, "r") as f:
        for line in f:
            vocabulary.append(line.strip("\n"))

    return vocabulary


def load_docwords(path:str="data/bag+of+words/docword.kos.txt") -> np.ndarray:
    with open(path, "r") as f:
        n_docs = int(f.readline().strip())
        n_words = int(f.readline().strip())
        n_nonzero_counts = int(f.readline().strip())
        
        counts_matrix = np.zeros((n_docs, n_words))
        for line in f:
            split_line = line.strip().split(" ")
            counts_matrix[int(split_line[0])-1,
                          int(split_line[1])-1] = int(split_line[2])
    
    return counts_matrix