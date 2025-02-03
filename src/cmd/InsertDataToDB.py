import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from src.common import util
from src.common import model
import config
from src.common import ccfsw_reader
from src.common import convert_data


def main():
    #データセット選択
    if (df := util.get_dataset()) is None:
        return 
    #開始地点選択
    start_point = util.get_start_point()

    #DB接続
    db = model.DB_Controller()

    index = start_point
    while True:
        try:
            identifier = df.at[index, "Identifier"]
        except KeyError:
            print("--- 処理終了 ---")
            break
        meta = (index, identifier)
        if index in config.SKIP_REPOS:
            print("[Info]スキップリポジトリです．")
            index += 1
            continue
        print("{:04}_{}".format(index, identifier.replace("/", "_")))
        #クローンセットディレクトリのファイル一覧を取得
        clone_set_dir = os.path.join(project_root, "dest", "sets", "{:04}_{}".format(index, identifier.replace("/", "_")))
        file_list = os.listdir(clone_set_dir)
        for ccfsw_file in file_list:
            #言語を取得
            lang = ccfsw_reader.get_lang(os.path.join(clone_set_dir, ccfsw_file))
            if lang is None:
                print("--- 言語が取得できませんでした ---")
                util.print_error_log(meta, ccfsw_file)
                continue

            #ファイル情報を取得
            result, file_list = ccfsw_reader.get_file_list(meta, os.path.join(clone_set_dir, ccfsw_file))
            if result is False:
                util.print_error_log(meta, ccfsw_file)
                continue
            #ファイル情報をDBに挿入
            db.insert_datas(convert_data.convert_file_list(meta, lang, file_list), "files")

            #コミット情報を取得
            commit_list = convert_data.get_commit_list(meta, file_list)

            #クローンセット情報を取得
            result, set_list = ccfsw_reader.get_set_list(meta, os.path.join(clone_set_dir, ccfsw_file), lang)
            if result is False:
                util.print_error_log(meta, ccfsw_file)
                continue
            #クローンセット情報をDBに挿入
            db.insert_datas(convert_data.convert_set_list(meta, lang, set_list, commit_list), "sets")

        #次のデータへ
        index += 1

        
if __name__ == "__main__":
    main()