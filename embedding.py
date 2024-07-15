import torch.cuda
import torch.backends
import os
import logging
import uuid
from langchain.embeddings.huggingface import HuggingFaceEmbeddings


LOG_FORMAT = "%(levelname) -5s %(asctime)s" "-1d: %(message)s"
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(format=LOG_FORMAT)

embedding_model_dict = {
    "ernie-tiny": "nghuyong/ernie-3.0-nano-zh",
    "ernie-base": "nghuyong/ernie-3.0-base-zh",
    "text2vec-base": "/home/ubuntu/data/model_data/text2vec-large-chinese",
    "text2vec": "GanymedeNil/text2vec-large-chinese",
}

# Embedding model name
EMBEDDING_MODEL = "text2vec"

# Embedding running device
EMBEDDING_DEVICE = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"

# patch HuggingFaceEmbeddings to make it hashable
def _embeddings_hash(self):
    return hash(self.model_name)


embeddings = HuggingFaceEmbeddings(model_name=embedding_model_dict[EMBEDDING_MODEL],
                                                model_kwargs={'device': EMBEDDING_DEVICE})






