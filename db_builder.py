import sqlite3 as sqlite
import json
import pathlib


if __name__ == '__main__':
    task_list_json_path = pathlib.Path('task_list.json')
    if task_list_json_path.exists():
        print('using dumped `task_list`')
        with open(task_list_json_path, 'r') as f:
            tasks = json.load(f)
    else:
        raise Exception('task_list.json not found')

    sql = sqlite.connect('task_list_db.sqlite')
    sql.execute('CREATE TABLE IF NOT EXISTS TASKS (DROPBOX_PATH TEXT PRIMARY KEY, DOWNLOAD_PATH TEXT, STATUS INT)')
    for (download_path, dropbox_path) in tasks:
        sql.execute('INSERT INTO TASKS VALUES (?, ?, ?)', (dropbox_path, download_path, 0))
    sql.commit()
    sql.close()

