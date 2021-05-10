import os
import pathlib
import typing as tp


def repo_find(workdir: tp.Union[str, pathlib.Path] = ".") -> pathlib.Path:
    git_dir = os.environ.get("GIT_DIR", default=".pyvcs")
    dir = pathlib.Path(workdir)
    while str(dir.absolute()) != "/":
        if (dir / git_dir).exists():
            return dir / git_dir
        dir = dir.parent
    if (dir / git_dir).exists():
        return dir / git_dir
    raise Exception("Not a git repository")


def repo_create(workdir: tp.Union[str, pathlib.Path]) -> pathlib.Path:
    git_dir = os.environ.get("GIT_DIR", default=".pyvcs")
    dir = pathlib.Path(workdir)
    if not dir.is_dir():
        raise Exception(f"{workdir} is not a directory")
    os.makedirs(dir / git_dir / "refs" / "heads")
    os.makedirs(dir / git_dir / "refs" / "tags")
    os.makedirs(dir / git_dir / "objects")
    with (dir / git_dir / "HEAD").open("w") as f:
        f.write("ref: refs/heads/master\n")
    with (dir / git_dir / "config").open("w") as f:
        f.write(
            "[core]\n\trepositoryformatversion = 0\n\tfilemode = true\n\tbare = false\n\tlogallrefupdates = false\n"
        )
    with (dir / git_dir / "description").open("w") as f:
        f.write("Unnamed pyvcs repository.\n")
    return dir / git_dir

