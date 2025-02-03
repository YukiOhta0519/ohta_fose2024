import subprocess
import os
import sys
import json

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from src.common import util
import config

def clone_set_detect(meta: tuple):
    index, identifier = meta
    target = project_root + "/dest/subjects/{:0=4}_{}".format(index, identifier.replace("/", "_"))
    dest_path = project_root + "/dest/sets/{:0=4}_{}/".format(index, identifier.replace("/", "_"))
    err_path = project_root + "/dest/error.log"
    os.makedirs(dest_path, exist_ok=True)
    # 検出言語を設定

    # クローンを言語ごとに検出
    print("{:04}_{}".format(index, identifier))
    lang_ccfinder = config.FOCUS_LANG_CCFINDER
    cmd = [
        "java",
        "-jar",
        "-Xms16g",
        "-Xmx16g",
        "-Xss128m",
        project_root + "/" + config.CCFINDER_PATH,
        'D',
        '-d',
        target,
        '-l',
        lang_ccfinder,
        '-o',
        dest_path + lang_ccfinder,
        '-w',
        '2',
        '-ccfsw',
        'set',
    ]            
    result = subprocess.run(cmd)
    if result.returncode != 0:
        with open(err_path, "a") as f:
            f.write("Error: {:0=4}_{}: {}\n".format(index, identifier, config.FOCUS_LANG))


def is_focus_lang(meta: tuple) -> bool:
    index, identifier = meta
    target = project_root + "/dest/subjects/{:0=4}_{}/".format(index, identifier.replace("/", "_"))
    cmd = ["github-linguist", target ,"--json", "--breakdown"]
    output = str(subprocess.run(cmd, capture_output=True, text=True).stdout).replace("\\n", "")
    output_json = json.loads(output)
    for lang in output_json.keys():
        if lang == config.FOCUS_LANG:
            return True
    return False


def main():
    #データセット選択
    if (df := util.get_dataset()) is None:
        return 
    #開始地点選択
    start_point = util.get_start_point()

    #出力先作成
    os.makedirs(project_root + "/dest/sets/", exist_ok=True)

    #リポジトリごとに処理
    index = start_point
    while True:
        try:
            identifier = df.at[index, "Identifier"]
        except KeyError:
            print("--- 処理終了 ---")
            break
        print("")
        print("---")
        print("{0}: {1}".format(index, identifier))
        print("---")
        meta = (index, identifier)
        if index in config.SKIP_REPOS:
            print("[Info]スキップリポジトリです．")
            index += 1
            continue
        if is_focus_lang(meta):
            clone_set_detect(meta)
        index += 1

if __name__ == "__main__":
    main()