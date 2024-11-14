import os

def list_files_in_directory(directory_path):
    # 列出指定目录中的所有文件和子目录
    files = os.listdir(directory_path)
    # 只保留文件（排除子目录）
    files = [f for f in files if os.path.isfile(os.path.join(directory_path, f))]
    return files

def list_file_paths_in_directory(directory_path):
    # 获取指定目录中所有文件的完整路径
    file_paths = [os.path.join(directory_path, f) for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]
    return file_paths
