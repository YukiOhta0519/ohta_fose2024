import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from src.common import util
from src.common import model
from src.common import ccfsw_reader
import config

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
            print("{:04}_{}".format(index, identifier.replace("/", "_")))
        except KeyError:
            print("--- 処理終了 ---")
            break
        if index in config.SKIP_REPOS:
            print("[Info]スキップリポジトリです．")
            index += 1
            continue
        meta = (index, identifier)
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
            print("[Info]言語: {}".format(lang))
            #ファイル情報を取得
            file_path_dict = db.get_file_path_dict(meta, lang)
            #クローンセット情報を取得
            clone_set_list = db.get_clone_set_list(meta, lang)
            #フィルタリング
            test_clone_set_list = []
            product_clone_set_list = []
            for clone_set in clone_set_list:
                product_fragments = []
                test_fragments = []
                for fragment in clone_set["fragments"]:
                    file_path: str = file_path_dict[fragment["file_number"]]
                    if "test" in file_path.lower():
                        test_fragments.append(fragment)
                    else:
                        product_fragments.append(fragment)
                if len(test_fragments) > 1:
                    test_clone_set_list.append({
                        "index": meta[0],
                        "identifier": meta[1],
                        "lang": lang,
                        "clone_id": clone_set["clone_id"],
                        "fragments": test_fragments
                    })
                if len(product_fragments) > 1:
                    product_clone_set_list.append({
                        "index": meta[0],
                        "identifier": meta[1],
                        "lang": lang,
                        "clone_id": clone_set["clone_id"],
                        "fragments": product_fragments
                    })
            #フィルタリング後のクローンセット情報をDBに挿入
            if len(product_clone_set_list) > 0:
                db.insert_datas(product_clone_set_list, "product_sets")
            else:
                print("[Info]プロダクトセットがありません．")
            if len(test_clone_set_list) > 0:
                db.insert_datas(test_clone_set_list, "test_sets")
            else:
                print("[Info]テストセットがありません．")

        #次のデータへ
        index += 1


if __name__ == "__main__":
    main()