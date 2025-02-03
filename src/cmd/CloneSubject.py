import os
import sys
import subprocess

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from src.common import util

def clone_subject(identifier: str, github_path: str, index: int):
    target = "{:0=4}_".format(index) + identifier.replace("/", "_")
    dest = project_root + "/dest/subjects/" + target

    # git clone
    subprocess.run(["git", "clone", github_path, dest, "--depth", "100"])


def main():
    #データセット選択
    if (df := util.get_dataset()) is None:
        return 
    #開始地点選択
    start_point = util.get_start_point()

    os.makedirs(project_root + "/dest/subjects/")

    index = start_point
    while True:
        try:
            identifier = df.at[index, "Identifier"]
            github_path = df.at[index, "URL"]
        except KeyError:
            print("--- 処理終了 ---")
            break
        print("")
        print("---")
        print("{0}: {1}".format(index, identifier))
        print("---")
        clone_subject(identifier, github_path, index)
        index += 1

if __name__ == "__main__":
    main()