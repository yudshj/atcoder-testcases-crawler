import json
import os
import pathlib
from getpass import getpass
from multiprocessing.pool import ThreadPool, Pool
from typing import Optional

import dropbox
from dropbox.files import FileMetadata, FolderMetadata
from tqdm import tqdm


def recursive_download(path: pathlib.Path, remote_path: str, dbx: dropbox.Dropbox, thread_num: int = -1):
    print("entering", remote_path)
    path.mkdir(parents=True, exist_ok=True)
    lst = dbx.files_list_folder(remote_path)
    file_list = []

    if thread_num > 1:
        pool = ThreadPool(processes=thread_num)
        events = []
    else:
        pool = None
        events = None

    for x in lst.entries:
        if type(x) == FileMetadata:
            file_list.append([(path / x.name).as_posix(), x.path_lower])
        elif type(x) == FolderMetadata:
            args = (path / x.name, remote_path + '/' + x.name, dbx, -1)
            if pool is not None and events is not None:
                event = pool.apply_async(recursive_download, args=args)
                events.append(event)
            else:
                file_list.extend(recursive_download(*args))

    if events is not None:
        for event in events:
            file_list.extend(event.get())
    print("finished", remote_path)
    return file_list


if __name__ == '__main__':
    if 'DROPBOX_TOKEN' in os.environ:
        _token = os.environ['DROPBOX_TOKEN']
    else:
        _token = getpass('Enter your access token: ')
    dbx = dropbox.Dropbox(_token)
    p = pathlib.Path('./Downloads')
    task_list_json_path = pathlib.Path('task_list.json')
    if task_list_json_path.exists():
        print('using dumped `task_list`')
        with open(task_list_json_path, 'r') as f:
            tasks = json.load(f)
    else:
        print("getting `task_list`")
        tasks = recursive_download(p, '/atcoder_testcases', dbx, thread_num=8)
        try:
            with open(task_list_json_path, 'w') as f:
                json.dump(tasks, f, separators=(',', ':'))
        except:
            import IPython

            IPython.embed()
