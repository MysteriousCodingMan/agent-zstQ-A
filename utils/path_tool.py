

import os


def get_project_root() -> str:
    '''
    获取项目根目录
    '''
    # 当前文件绝对路径
    current_filr = os.path.abspath(__file__)
    # 获取工程根目录,先获取文件所在的文件夹根目录
    current_dit = os.path.dirname(current_filr)
    # 获取工程根目录
    project_root = os.path.dirname(current_dit)
    
    return project_root
    
def get_abs_path(relative_path: str) -> str:
    '''
    传入相对路径，获取绝对路径
    '''
    project_root = get_project_root()
    return os.path.join(project_root, relative_path)
    