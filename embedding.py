import torch.cuda
import torch.backends
import logging
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
import os

LOG_FORMAT = "%(levelname) -5s %(asctime)s" "-1d: %(message)s"
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(format=LOG_FORMAT)

embedding_model_path = os.environ.get("EMBEDDING_MODEL_PATH", "/home/ubuntu/data/model_data/m3e-base")

# Embedding model name
EMBEDDING_MODEL = "m3e-base"

# Embedding running device
EMBEDDING_DEVICE = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"

# patch HuggingFaceEmbeddings to make it hashable
def _embeddings_hash(self):
    return hash(self.model_name)


embeddings = HuggingFaceEmbeddings(model_name=embedding_model_path,
                                                model_kwargs={'device': EMBEDDING_DEVICE})






