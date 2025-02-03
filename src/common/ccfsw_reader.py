import os
import re

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def get_file_list(meta: tuple, file_path: str) -> tuple:
    if not os.path.isfile(file_path):
        return False, None
    files = {}
    with open(file_path, 'r') as file:
        # ファイル情報までスキップ
        while True:
            line = file.readline()
            if "#source_files" in line:
                break
        # ファイル情報を抽出
        while True:
            line = file.readline()
            if "#clone_sets" in line:
                break
            args = line.split("\t")
            path = str(args[3]).replace("\n", "")
            files[int(args[0])] = {"LOC":int(args[1]), "path":path}
    if len(files.keys()) == 0:
        print("--- ファイル情報がありません ---")
        return False, None
    else:
        return True, files
    

def get_set_list(meta: tuple, file_path: str, lang: int) -> tuple:
    if not os.path.isfile(file_path):
        return False, None
    set_list = []
    with open(file_path, 'r') as file:
        # セット情報までスキップ
        while True:
            line = file.readline()
            if "#clone_sets" in line:
                break
        # セット情報を抽出
        clone_id = -1
        fragments = []
        while True:
            line = file.readline()
            # 終了検知
            if not line:
                if clone_id != -1:
                    set_list.append({"clone_id":clone_id, "fragments": fragments})
                break
            # セットごとに分割
            # クローンIDを取得
            if "cloneID" in line:
                if clone_id != -1:
                    set_list.append({"clone_id":clone_id, "fragments": fragments})
                    fragments = []
                clone_id = int(line.replace('\n', '').split(':')[1])
                continue
            # フラグメントを取得
            args = re.split("[:, -]+", line)
            fragments.append({"file_number":int(args[0].replace('\t', '')), "begin":int(args[1]), "end":int(args[3])})
    if len(set_list) == 0:
        return False, None
    else:
        return True, set_list
    

def get_lang(file_path: str) -> str:
    with open(file_path, 'r') as file:
        while True:
            line = file.readline()
            if "#rule_constructor" in line:
                break
        line = file.readline()
        return line.replace("{\n", "")
    return None