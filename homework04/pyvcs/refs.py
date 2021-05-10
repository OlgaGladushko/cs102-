import pathlib
import typing as tp


def update_ref(gitdir: pathlib.Path, ref: tp.Union[str, pathlib.Path], new_value: str) -> None:
    ref_file = gitdir / ref
    with ref_file.open("w") as s:
        s.write(new_value)


def symbolic_ref(gitdir: pathlib.Path, name: str, ref: str) -> None:



def ref_resolve(gitdir: pathlib.Path, refname: str) -> tp.Optional[str]:
    if refname == "HEAD" and not is_detached(gitdir):
        return resolve_head(gitdir)
    if (gitdir / refname).exists():
        with (gitdir / refname).open() as f:
            return f.read().strip()
    return None


def resolve_head(gitdir: pathlib.Path) -> tp.Optional[str]:
    with (gitdir / "HEAD").open() as f:
        return ref_resolve(gitdir, get_ref(gitdir))


def is_detached(gitdir: pathlib.Path) -> bool:
    if get_ref(gitdir) == "":
        return True
    return False


def get_ref(gitdir: pathlib.Path) -> str:
    with (gitdir / "HEAD").open() as f:
        data = f.read().strip().split()
        if len(data) == 2:
            return data[1]
        else:
            return ""
