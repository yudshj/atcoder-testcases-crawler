import json
import os
import pathlib
from getpass import getpass
import multiprocessing
import dropbox
from tqdm import tqdm


def wrapper(arg_list, queue: multiprocessing.Queue):
    if 'DROPBOX_TOKEN' in os.environ:
        _token = os.environ['DROPBOX_TOKEN']
    else:
        _token = getpass('Enter your access token: ')
    dbx = dropbox.Dropbox(_token)
    
    for arg in tqdm(arg_list):
        dbx.files_download_to_file(*arg)
        queue.put(arg[0])


if __name__ == '__main__':
    task_list_json_path = pathlib.Path('task_list.json')
    if task_list_json_path.exists():
        print('using dumped `task_list`')
        with open(task_list_json_path, 'r') as f:
            tasks = json.load(f)
    else:
        raise Exception('task_list.json not found')

    num_procs = 8

    queue: multiprocessing.Queue = multiprocessing.Queue()
    lists = [tasks[len(tasks) // num_procs * i : len(tasks) // num_procs * (i + 1)] for i in range(num_procs - 1)]
    lists.append(tasks[len(tasks) // num_procs * (num_procs - 1):])
    procs = [multiprocessing.Process(target=wrapper, args=(x, queue)) for x in lists]

    fp = open("finished_paths.txt", "w")


    for proc in procs:
        proc.start()

    for i in tqdm(range(len(tasks))):
        current = queue.get()
        fp.write(current + "\n")
        fp.flush()
        tqdm.write(current)
    
    for proc in procs:
        proc.join()

    fp.close()