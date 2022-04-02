import os
import sqlite3
from getpass import getpass
import multiprocessing
import dropbox
from tqdm import tqdm
import pathlib


def wrapper(token: str, arg_list, queue: multiprocessing.Queue):
    dbx = dropbox.Dropbox(token)

    for (dropbox_path, download_path) in tqdm(arg_list):
        dbx.files_download_to_file(download_path, dropbox_path)
        queue.put(dropbox_path)


def main():
    if 'DROPBOX_TOKEN' in os.environ:
        _token = os.environ['DROPBOX_TOKEN']
    else:
        _token = getpass('Enter your access token: ')

    p = pathlib.Path('task_list_db.sqlite')
    if not p.exists():
        raise FileNotFoundError('task_list_db.sqlite not found')
    sql = sqlite3.connect(p)
    tasks = sql.execute('SELECT DROPBOX_PATH, DOWNLOAD_PATH FROM TASKS WHERE STATUS = 0').fetchall()

    num_procs = 8

    queue: multiprocessing.Queue = multiprocessing.Queue()
    lists = [tasks[len(tasks) // num_procs * i: len(tasks) // num_procs * (i + 1)] for i in range(num_procs - 1)]
    lists.append(tasks[len(tasks) // num_procs * (num_procs - 1):])
    procs = [multiprocessing.Process(target=wrapper, args=(_token, x, queue)) for x in lists]

    for proc in procs:
        proc.start()

    for _i in tqdm(range(len(tasks))):
        done_dropbox_path = queue.get()
        sql.execute('UPDATE TASKS SET STATUS = 1 WHERE DROPBOX_PATH = ?', (done_dropbox_path,))
        sql.commit()
        tqdm.write(done_dropbox_path)

    for proc in procs:
        proc.join()

    sql.close()
    print('Done!')


if __name__ == '__main__':
    main()
