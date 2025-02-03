import os
import sys

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from src.common import util
from src.common import model
from src.common import ccfsw_reader
import config


def output_boxplot(result_dict: dict, output_file_path: str):
    languages = [convert_to_output_str(lang) for lang in result_dict.keys()]
    values = result_dict.values()

    #中央値を計算
    medians = [np.median(v) for v in values]

    # # #ソート（中央値でソート）
    # sorted_data = sorted(zip(languages, values, medians), key=lambda x: x[2], reverse=False)
    # sorted_languages, sorted_values, sorted_medians = zip(*sorted_data)

    for lang, median in zip(languages, medians):
        print("{}-median: {}".format(lang, median))

    # プロットの設定
    fig, ax = plt.subplots(figsize=(12, 15))

    # 箱ヒゲ図を作成
    box = ax.boxplot(values, tick_labels=languages, patch_artist=True, vert=False, widths=0.4)

    # 白黒の設定
    for element in ['boxes', 'whiskers', 'medians', 'caps']:
        plt.setp(box[element], color='black')

    for patch in box['boxes']:
        patch.set(facecolor='white')

    # 値の範囲を設定
    ax.set_xlim(0, 1)

    # グリッドを追加
    ax.grid(True, axis='x')

    # グラフを表示
    plt.savefig(output_file_path)
    

def convert_to_output_str(s: str) -> str:
    match s:
        case "java":
            return "Java"
        case "python3":
            return "Python"
        case "csharp":
            return "C#"
        case "javascript":
            return "JavaScript"
        case "typescript":
            return "TypeScript"
        case "golang":
            return "Go"
        case "php":
            return "PHP"
        case "ruby":
            return "Ruby"
        case "rust":
            return "Rust"
        case "scala":
            return "Scala"
        case "c":
            return "C"
        case "cpp":
            return "C++"
        case _:
            return s


def get_clone_ratio(df, type: str):
    db = model.DB_Controller()
    result_dict = {}

    index = 0
    while True:
        try:
            identifier = df.at[index, "Identifier"]
        except:
            break
        if index in config.SKIP_REPOS:
            index += 1
            continue
        meta = (index, identifier)

        #クローンセットディレクトリのファイル一覧を取得
        clone_set_dir = os.path.join(project_root, "dest", "sets", "{:04}_{}".format(index, identifier.replace("/", "_")))
        ccfsw_file_list = os.listdir(clone_set_dir)
        for ccfsw_file in ccfsw_file_list:
            #言語を取得
            lang = ccfsw_reader.get_lang(os.path.join(clone_set_dir, ccfsw_file))
            if lang is None:
                print("--- 言語が取得できませんでした ---")
                util.print_error_log(meta, ccfsw_file)
                continue

            #ファイル情報を取得
            file_list = db.get_file_list(meta, lang, "files")

            dup_file_dict = {}
            for file in file_list:
                match type:
                    case "product":
                        if "test" not in file["path"].lower():     
                            dup_file_dict[file["id"]] = [False] * (int(file["LOC"]) + 1)
                    case "test":
                        if "test" in file["path"].lower():
                            dup_file_dict[file["id"]] = [False] * (int(file["LOC"]) + 1)
                    case "all":
                        dup_file_dict[file["id"]] = [False] * (int(file["LOC"]) + 1)
            
            match type:
                case "product":
                    clone_set_list = db.get_product_clone_set_list(meta, lang)
                case "test":
                    clone_set_list = db.get_test_clone_set_list(meta, lang)
                case "all":
                    clone_set_list = db.get_clone_set_list(meta, lang)

            count = 0
            for clone_set in clone_set_list:
                count += 1
                for fragment in clone_set["fragments"]:
                    for line in range(fragment["begin"]-1, fragment["end"]):
                        try:
                            dup_file_dict[fragment["file_number"]][line] = True
                        except:
                            print("{}-{}: {} ({})".format(fragment["begin"], fragment["end"], line, len(dup_file_dict[fragment["file_number"]])))
            
            if count == 0:
                continue

            duplicated_line_count = 0
            line_count = 0
            for file_number in dup_file_dict.keys():
                duplicated_list = dup_file_dict[file_number]
                duplicated_line_count += duplicated_list.count(True)
                line_count += len(duplicated_list)

            if lang not in result_dict.keys():
                result_dict[lang] = []

            if line_count > 0:
                result_dict[lang].append(duplicated_line_count / line_count)

        index += 1

    return result_dict


def get_co_modification_ratio(df, type: str):
    db = model.DB_Controller()
    result_dict = {}

    index = 0
    while True:
        try:
            identifier = df.at[index, "Identifier"]
        except:
            break
        meta = (index, identifier)
        if index in config.SKIP_REPOS:
            index += 1
            continue
        
        #クローンセットディレクトリのファイル一覧を取得
        clone_set_dir = os.path.join(project_root, "dest", "sets", "{:04}_{}".format(index, identifier.replace("/", "_")))
        ccfsw_file_list = os.listdir(clone_set_dir)
        for ccfsw_file in ccfsw_file_list:
            #言語を取得
            lang = ccfsw_reader.get_lang(os.path.join(clone_set_dir, ccfsw_file))
            if lang is None:
                print("--- 言語が取得できませんでした ---")
                util.print_error_log(meta, ccfsw_file)
                continue

            #クローンセットを取得
            match type:
                case "product":
                    clone_set_list = db.get_product_clone_set_list(meta, lang)
                case "test":
                    clone_set_list = db.get_test_clone_set_list(meta, lang)
                case "all":
                    clone_set_list = db.get_clone_set_list(meta, lang)
            
            co_modified_count = 0
            count = 0
            for clone_set in clone_set_list:
                count += 1
                commits = set()
                co_modified = False
                for fragment in clone_set["fragments"]:
                    fragment_commits = fragment["commit_list"]
                    for commit in fragment_commits:
                        if commit.startswith("^"):
                            continue
                        if commit in commits:
                            co_modified = True
                            break
                        commits.add(commit)
                    if co_modified:
                        co_modified_count += 1
                        break
                        
            if lang not in result_dict.keys():
                result_dict[lang] = []
            if count > 0:
                result_dict[lang].append(co_modified_count / count)

        index += 1

    return result_dict


def generate_rq1(df):
    print("### RQ1 ###")
    rq1_result_dict = get_clone_ratio(df, "all")
    for lang in rq1_result_dict.keys():
        print("{}-count: {}".format(lang, len(rq1_result_dict[lang])))
        print("{}-min: {}".format(lang, min(rq1_result_dict[lang])))
        print("{}-max: {}".format(lang, max(rq1_result_dict[lang])))
        print("{}-median: {}".format(lang, np.median(rq1_result_dict[lang])))
    boxplot_file_path = os.path.join(project_root, "dest", "results", "RQ1.pdf")
    output_boxplot(rq1_result_dict, boxplot_file_path)


def generate_rq2(df):
    print("### RQ2 ###")
    product_result_dict = get_clone_ratio(df, "product")
    test_result_dict = get_clone_ratio(df, "test")

    result_dict = {}
    languages = product_result_dict.keys()
    sorted_languages = sorted(languages, reverse=True)

    for lang in sorted_languages:
        print("{}: {}".format(lang, stats.mannwhitneyu(product_result_dict[lang], test_result_dict[lang], alternative='two-sided')))
        print("")

    for lang in sorted_languages:
        key = convert_to_output_str(lang) + "(product)"
        result_dict[key] = product_result_dict[lang]
        print("{}-count: {}".format(key, len(product_result_dict[lang])))
        print("{}-min: {}".format(key, min(product_result_dict[lang])))
        print("{}-max: {}".format(key, max(product_result_dict[lang])))
        print("{}-median: {}".format(key, np.median(product_result_dict[lang])))
        key = convert_to_output_str(lang) + "(test)"
        result_dict[key] = test_result_dict[lang]
        print("{}-count: {}".format(key, len(test_result_dict[lang])))
        print("{}-min: {}".format(key, min(test_result_dict[lang])))
        print("{}-max: {}".format(key, max(test_result_dict[lang])))
        print("{}-median: {}".format(key, np.median(test_result_dict[lang])))
    boxplot_file_path = os.path.join(project_root, "dest", "results", "RQ2.pdf")
    output_boxplot(result_dict, boxplot_file_path)
    

def generate_rq3(df):
    print("### RQ3 ###")
    product_result_dict = get_co_modification_ratio(df, "product")
    test_result_dict = get_co_modification_ratio(df, "test")

    result_dict = {}
    languages = product_result_dict.keys()
    sorted_languages = sorted(languages, reverse=True)
    for lang in sorted_languages:
        print("{}: {}".format(lang, stats.mannwhitneyu(product_result_dict[lang], test_result_dict[lang], alternative='two-sided')))
        print("")

    for lang in sorted_languages:
        key = convert_to_output_str(lang) + "(product)"
        result_dict[key] = product_result_dict[lang]
        print("{}-count: {}".format(key, len(product_result_dict[lang])))
        print("{}-min: {}".format(key, min(product_result_dict[lang])))
        print("{}-max: {}".format(key, max(product_result_dict[lang])))
        print("{}-median: {}".format(key, np.median(product_result_dict[lang])))
        key = convert_to_output_str(lang) + "(test)"
        result_dict[key] = test_result_dict[lang]
        print("{}-count: {}".format(key, len(test_result_dict[lang])))
        print("{}-min: {}".format(key, min(test_result_dict[lang])))
        print("{}-max: {}".format(key, max(test_result_dict[lang])))
        print("{}-median: {}".format(key, np.median(test_result_dict[lang])))
    boxplot_file_path = os.path.join(project_root, "dest", "results", "RQ3.pdf")
    output_boxplot(result_dict, boxplot_file_path)
        

def main():
    #データセット選択
    if (df := util.get_dataset()) is None:
        return
    os.makedirs(os.path.join(project_root, "dest", "results"), exist_ok=True)
    
    generate_rq1(df)
    generate_rq2(df)
    generate_rq3(df)


if __name__ == "__main__":
    main()