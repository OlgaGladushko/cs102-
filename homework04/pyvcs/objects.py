import hashlib
import os
import pathlib
import re
import stat
import typing as tp
import zlib

from pyvcs.refs import update_ref
from pyvcs.repo import repo_find


def hash_object(data: bytes, fmt: str, write: bool = False) -> str:
    sha = hashlib.sha1((fmt + " " + str(len(data))).encode() + b"\00" + data).hexdigest()
    if write:
        obj_dir = repo_find() / "objects" / sha[:2]
        if not obj_dir.exists():
            obj_dir.mkdir()
        with (obj_dir / sha[2:]).open("wb") as file:
            file.write(zlib.compress((fmt + " " + str(len(data))).encode() + b"\00" + data))
    return sha


def resolve_object(obj_name: str, gitdir: pathlib.Path) -> tp.List[str]:
    if 4 > len(obj_name) or len(obj_name) > 40:
        raise Exception(f"Not a valid object name {obj_name}")
    objects = repo_find() / "objects"
    obj_list = []
    for file in (objects / obj_name[:2]).glob("*"):
        cur_obj_name = file.parent.name + file.name
        if obj_name == cur_obj_name[: len(obj_name)]:
            obj_list.append(cur_obj_name)
    if not obj_list:
        raise Exception(f"Not a valid object name {obj_name}")
    return obj_list


def find_object(obj_name: str, gitdir: pathlib.Path) -> str:
    # PUT YOUR CODE HERE
    ...


def read_object(sha: str, gitdir: pathlib.Path) -> tp.Tuple[str, bytes]:
    objects = repo_find() / "objects"
    with (objects / sha[:2] / sha[2:]).open("rb") as f:
        data = zlib.decompress(f.read())
    return (
        data.split(b"\00")[0].split(b" ")[0].decode(),
        data.split(b"\00", maxsplit=1)[1],
    )


def read_tree(data: bytes) -> tp.List[tp.Tuple[int, str, str]]:
    tree = []
    while data:
        start_sha = data.index(b"\00")
        mode_b: bytes
        name_b: bytes
        mode_b, name_b = data[:start_sha].split(b" ")
        mode = mode_b.decode()
        name = name_b.decode()
        sha = data[start_sha + 1 : start_sha + 21]
        tree.append((int(mode), name, sha.hex()))
        data = data[start_sha + 21 :]
    return tree


def cat_file(obj_name: str, pretty: bool = True) -> None:
    gitdir = repo_find()
    fmt, file_content = read_object(obj_name, gitdir)
    blob_or_commit_tuple = ("blob", "commit")
    if fmt in blob_or_commit_tuple:
        print(file_content.decode())
    else:
        for tree in read_tree(file_content):
            if tree[0] != 40000:
                print(f"{tree[0]:06}", "blob", tree[2] + "\t" + tree[1])
            else:
                print(f"{tree[0]:06}", "tree", tree[2] + "\t" + tree[1])


def find_tree_files(tree_sha: str, gitdir: pathlib.Path) -> tp.List[tp.Tuple[str, str]]:
    # PUT YOUR CODE HERE
    ...


def commit_parse(raw: bytes, start: int = 0, dct=None):
    result: tp.Dict[str, tp.Any] = {"message": []}
    for i in map(lambda x: x.decode(), raw.split(b"\n")):
        if "tree" in i or "parent" in i or "author" in i or "committer" in i:
            name, val = i.split(" ", maxsplit=1)
            result[name] = val
        else:
            result["message"].append(i)
    return result


