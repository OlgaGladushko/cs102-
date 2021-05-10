import hashlib
import operator
import os
import pathlib
import struct
import typing as tp

from pyvcs.objects import hash_object


class GitIndexEntry(tp.NamedTuple):
    # @see: https://github.com/git/git/blob/master/Documentation/technical/index-format.txt
    ctime_s: int
    ctime_n: int
    mtime_s: int
    mtime_n: int
    dev: int
    ino: int
    mode: int
    uid: int
    gid: int
    size: int
    sha1: bytes
    flags: int
    name: str

    def pack(self) -> bytes:
        return struct.pack(
            "!10I20sh" + str(len(self.name)) + "s" + str(8 - (62 + len(self.name)) % 8) + "x",
            self.ctime_s,
            self.ctime_n,
            self.mtime_s,
            self.mtime_n,
            self.dev,
            self.ino & 0xFFFFFFFF,
            self.mode,
            self.uid,
            self.gid,
            self.size,
            self.sha1,
            self.flags,
            self.name.encode(),
        )

    @staticmethod
    def unpack(data: bytes) -> "GitIndexEntry":
        index_unpacked_content = struct.unpack(">10I20sh" + str(len(data) - 62) + "s", data)
        return GitIndexEntry(
            index_unpacked_content[0],
            index_unpacked_content[1],
            index_unpacked_content[2],
            index_unpacked_content[3],
            index_unpacked_content[4],
            index_unpacked_content[5],
            index_unpacked_content[6],
            index_unpacked_content[7],
            index_unpacked_content[8],
            index_unpacked_content[9],
            index_unpacked_content[10],
            index_unpacked_content[11],
            index_unpacked_content[12].rstrip(b"\00").decode(),
        )


def read_index(gitdir: pathlib.Path) -> tp.List[GitIndexEntry]:
    index = gitdir / "index"
    if not index.exists():
        return []
    with index.open("rb") as file:
        data = file.read()
    result = []
    header = data[:12]
    main_content = data[12:]
    main_content_copy = main_content
    for _ in range(struct.unpack(">I", header[8:])[0]):
        end_of_entry = len(main_content_copy) - 1
        for j in range(63, len(main_content_copy), 8):
            if main_content_copy[j] == 0:
                end_of_entry = j
                break
        result += [GitIndexEntry.unpack(main_content_copy[: end_of_entry + 1])]
        if len(main_content_copy) > end_of_entry:
            main_content_copy = main_content_copy[end_of_entry + 1 :]
    return result


def write_index(gitdir: pathlib.Path, entries: tp.List[GitIndexEntry]) -> None:
    index = gitdir / "index"
    with index.open("wb") as file:
        data = b"DIRC\00\00\00\02"
        data += struct.pack(">I", len(entries))
        for i in entries:
            data += i.pack()
        file.write(data + hashlib.sha1(data).digest())


def ls_files(gitdir: pathlib.Path, details: bool = False) -> None:
    for entry in read_index(gitdir):
        if details:
            print(f"{entry.mode:o} {entry.sha1.hex()} 0\t{entry.name}")
        else:
            print(entry.name)


def update_index(gitdir: pathlib.Path, paths: tp.List[pathlib.Path], write: bool = True) -> None:
    entries = read_index(gitdir)
    for path in paths:
        with path.open("rb") as f:
            data = f.read()
        stat = os.stat(path)
        entries.append(
            GitIndexEntry(
                ctime_s=int(stat.st_ctime),
                ctime_n=0,
                mtime_s=int(stat.st_mtime),
                mtime_n=0,
                dev=stat.st_dev,
                ino=stat.st_ino,
                mode=stat.st_mode,
                uid=stat.st_uid,
                gid=stat.st_gid,
                size=stat.st_size,
                sha1=bytes.fromhex(hash_object(data, "blob", write=True)),
                flags=7,
                name=str(path),
            )
        )
    if write:
        write_index(gitdir, sorted(entries, key=lambda x: x.name))
        
