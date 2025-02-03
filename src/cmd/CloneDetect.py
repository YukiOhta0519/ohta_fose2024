import subprocess
import os
import sys
import json
import shutil

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from src.common import util
import config


def convert_to_ccfinder_format(lang: str) -> str:
    match lang:
        case "Java": return "java"
        case "Python": return "python3"
        case "JavaScript": return "javascript"
        case "Go": return "golang"
        case "PHP": return "php"
        case "TypeScript": return "typescript"
        case "Rust": return "rust"
        case "C": return "c"
        case "C++": return "cpp"
        case "C#": return "csharp"
        case "Scala": return "scala"
        case "Ruby": return "ruby"
        case _: return None


def clone_set_detect(meta: tuple, langs_info: dict):
    index, identifier = meta
    target = project_root + "/dest/subjects/{:0=4}_{}".format(index, identifier.replace("/", "_"))
    dest_path = project_root + "/dest/sets/{:0=4}_{}/".format(index, identifier.replace("/", "_"))
    err_path = project_root + "/dest/error.log"
    os.makedirs(dest_path, exist_ok=True)
    # 検出言語を設定
    detect_langs = langs_info.keys()

    # クローンを言語ごとに検出
    for lang in detect_langs:
        lang_ccfinder = convert_to_ccfinder_format(lang)
        if lang_ccfinder in config.ANTLR_LANGUAGES:
            cmd = [
                "java",
                "-jar",
                "-Xms24g",
                "-Xmx24g",
                "-Xss512m",
                project_root + "/" + config.CCFINDER_PATH,
                'D',
                '-d',
                target,
                '-l',
                lang_ccfinder,
                '-o',
                dest_path + lang_ccfinder,
                '-antlr',
                '|'.join(langs_info[lang]),
                '-w',
                '2',
                '-ccfsw',
                'set',
            ]            
        else:
            cmd = [
                "java",
                "-jar",
                "-Xms24g",
                "-Xmx24g",
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
                f.write("Error: {:0=4}_{}: {}\n".format(index, identifier, lang))
            continue

    print("--- 言語 ---")
    for lang in detect_langs:
        print("{}: {}".format(lang, langs_info[lang]))
    print("")


def get_languages(meta: tuple) -> dict:
    index, identifier = meta
    result = {}
    target = project_root + "/dest/subjects/{:0=4}_{}/".format(index, identifier.replace("/", "_"))
    cmd = ["github-linguist", target ,"--json", "--breakdown"]
    output = str(subprocess.run(cmd, capture_output=True, text=True).stdout).replace("\\n", "")
    output_json = json.loads(output)
    for lang in output_json.keys():
        if lang not in config.DETECT_LANGUAGES:
            continue
        exts = set()
        for file in output_json[lang]["files"]:  
            exts.add(os.path.splitext(file)[1].replace(".", ""))
        result[lang] = exts
        print(exts)
    return result


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
        langs_info = get_languages(meta)
        clone_set_detect(meta, langs_info)
        index += 1

if __name__ == "__main__":
    main()