import os
import pandas


project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def get_dataset() -> pandas.DataFrame:
    print("resourcesディレクトリ上にデータセットを配置してください．")
    dataset_name = input("データセットを入力してください.(空白なら\"Filtered.csv\"): ")
    if dataset_name == "":
        dataset_name = "Filtered.csv"
    dataset_path = project_root + "/resources/" + dataset_name
    df = None
    try:
        df = pandas.read_csv(dataset_path, sep=';')
        print("[Info]データセットを読み込みました.")
    except:
        print("[Error]データセットの読み込みに失敗しました.")
    return df


def get_start_point() -> int:
    while True:
        start_point = int(input("開始地点を入力してください(正の整数): "))
        if start_point >= 0:
            break
        print("[Error]不正な値です.")
    print("[Info]開始地点を" + str(start_point) + "に設定しました.")
    return start_point


def print_error_log(meta: tuple, path: str):
    index, identifier = meta
    with open(os.path.join(project_root, "dest", "error_log.txt"), "a") as f:
        f.write("{}: {} - {}\n".format(index, identifier, path))
