import sys
sys.path.append('./')  # 将项目根目录添加到sys.path中，以便导入模块

from langchain_chroma import Chroma
from utils.config_handler import chroma_conf
from model.factory import embed_model
from langchain_text_splitters import RecursiveCharacterTextSplitter
from utils.path_tool import get_abs_path
from utils.file_handler import PyPDFLoader, TextLoader, listdir_with_allowed_type, get_file_md5_hex
from utils.logger_handler import logger
from langchain_core.documents import Document
import os


class VectorStoreService:
    def __init__(self):
        self.vector_store = Chroma(
            collection_name = chroma_conf['collection_name'],
            embedding_function = embed_model,
            persist_directory = chroma_conf['persist_directory'], 
            
        )
        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size = chroma_conf['chunk_size'], 
            chunk_overlap = chroma_conf['chunk_overlap'],
            separators = chroma_conf['separators'],
            length_function = len,
        )

    def get_retriever(self):
        return self.vector_store.as_retriever(search_kwargs={"k": chroma_conf['k']})

    def load_document(self):
        '''
        从数据文件中加载数据，转为向量，存入向量数据库
        计算文件的md5做去重
        : return: None
        '''
        
        def check_md5_hex(md5_for_check: str):
            if not os.path.exists(get_abs_path(chroma_conf['md5_hex_store'])):
                # 创建文件
                open(get_abs_path(chroma_conf['md5_hex_store']), 'w', encoding='utf-8').close()  # 创建md5文件
                return False   # md5没处理过

            with open(get_abs_path(chroma_conf['md5_hex_store']), 'r', encoding='utf-8') as f:
                for line in f.readlines():
                    line = line.strip()
                    if line == md5_for_check:
                        return True    # md5处理过了
                    
                return False   # md5没处理过
            
        def save_md5_hex(md5_for_check: str):
            with open(get_abs_path(chroma_conf['md5_hex_store']), 'a', encoding='utf-8') as f:
                f.write(md5_for_check + '\n')

        def get_file_documents(read_path: str):
            if read_path.endswith('.txt'):
                try:
                    return TextLoader(read_path, encoding="utf-8").load()
                except:
                    return TextLoader(read_path, encoding="gbk").load()
            
            if read_path.endswith('.pdf'):
                return PyPDFLoader(read_path).load()
            
            return []
        
        allowed_files_path: list[str] = listdir_with_allowed_type(
            get_abs_path(chroma_conf['data_path']),
            tuple(chroma_conf['allowed_knowledge_file_types']),
            )
        
        for path in allowed_files_path:
            # 计算文件md5
            md5_hex = get_file_md5_hex(path)
            
            if check_md5_hex(md5_hex):
                logger.info(f'[加载知识库]{path}已处理过，跳过')
                continue
            
            # 加载文件，转为向量，存入向量数据库
            try:
                documents:list[Document] = get_file_documents(path)
                
                if not documents:
                    logger.warning(f'[加载知识库]文件{path}没有加载到文档，跳过')
                    continue
                
                split_documents: list[Document] = self.spliter.split_documents(documents)
                
                if not split_documents:
                    logger.warning(f'[加载知识库]文件{path}分片后没有分割出文档，跳过')
                    continue
                
                # 存入向量数据库
                self.vector_store.add_documents(split_documents)
                
                # 保存md5
                save_md5_hex(md5_hex)
                
                logger.info(f'[加载知识库]文件{path}加载成功，分割成{len(split_documents)}个文档，已存入向量数据库')

            except Exception as e:
                # exc_info为True时会输出完整的异常堆栈信息, 为False时只输出异常信息
                logger.error(f'[加载知识库]文件{path}加载失败，错误信息：{e}', exc_info=True)
                continue


if __name__ == '__main__':
    vector_store_service = VectorStoreService()
    vector_store_service.load_document()
    
    retriver = vector_store_service.get_retriever()
    docs = retriver.invoke('什么是RAG？')
    
    for doc in docs:
        print(doc.page_content)
        print('---')



