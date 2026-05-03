from langchain.chroma import Chroma
from utils.config_handler import Chroma_conf
from model.factory import embed_model
from langchain_text_splitters import RecursiveCharacterTextSplitter



class VectorStoreService:
    def __init__(self):
        self.vector_store = Chroma(
            collection_name = Chroma_conf['collection_name'],
            embedding_function = embed_model,
            persist_directory = Chroma_conf['persist_directory'], 
            
        )
        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size = Chroma_conf['chunk_size'], 
            chunk_overlap = Chroma_conf['chunk_overlap'],
            separator = Chroma_conf['separator '],
            length_function = len,
        )

    def get_retriever(self):
        return self.vector_store.as_retriever(search_kwargs={"k": Chroma_conf['k']})

    def load_document(self):
        '''
        从数据文件中加载数据，转为向量，存入向量数据库
        计算文件的md5做去重
        : return: None
        '''
        
        def check_md5_hex(md5_for_check: str):
            if not os.path.exists(Chroma_conf['md5_path']):
                return False



