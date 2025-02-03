import os
import subprocess

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def convert_file_list(meta: tuple, lang: str, file_list: dict) -> list:
    index, identifier = meta
    result = []
    for file_number in file_list.keys():
        file = file_list[file_number]
        result.append({
            "index": index,
            "identifier": identifier,
            "lang": lang,
            "id": file_number,
            "LOC": file["LOC"],
            "path": file["path"]
        })
    return result


def convert_set_list(meta: tuple, lang: str, set_list: dict, commit_list: dict) -> list:
    result = []
    for set_info in set_list:
        fragments = []
        for fragment in set_info["fragments"]:
            commits = set()
            if commit_list[fragment["file_number"]] is not None:
                for line in range(fragment["begin"]-1, fragment["end"]):
                    if line >= len(commit_list[fragment["file_number"]]):
                        continue
                    commits.add(commit_list[fragment["file_number"]][line])
            fragments.append({
                "file_number": fragment["file_number"],
                "begin": fragment["begin"],
                "end": fragment["end"],
                "commit_list": list(commits)
            })
        result.append({
            "index": meta[0],
            "identifier": meta[1],
            "lang": lang,
            "clone_id": set_info["clone_id"],
            "fragments": fragments
        })
    return result


def get_commit_list(meta: tuple, file_list: dict) -> dict:
    index, identifier = meta
    target_repo = os.path.join(project_root, "dest", "subjects", "{:04}_{}".format(index, identifier.replace("/", "_")))
    current_dir = os.getcwd()
    os.chdir(target_repo)
    commit_list = {}
    for file_number in file_list.keys():
        file = file_list[file_number]
        rslt = []
        try:
            output =subprocess.run(["git", "blame", file["path"]], capture_output=True, text=True).stdout.split("\n")
        except:
            print("Error: git blame failed for file {}".format(file["path"]))
            commit_list[file_number] = None
            continue
        for line in output:
            if line == "":
                continue
            rslt.append(line.split(" ")[0])
        commit_list[file_number] = rslt
    os.chdir(current_dir)
    return commit_list