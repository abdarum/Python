import pathlib
import pprint
import os
import stat
import tqdm

FILE_TREE_ROOT = 'Z:\\'


def list_paths_of_all_files_and_directories(root_path: pathlib.Path, tqdm_progress=None):
    if not tqdm_progress is None:
        tqdm_progress.set_description('{}'.format(str(root_path)[-60:]))
        tqdm_progress.update()

    assert root_path.is_dir()
    list_of_files = []
    list_of_files.append(root_path)
    for item in root_path.iterdir():
        if item.is_dir():
            list_of_files.extend(list_paths_of_all_files_and_directories(item, tqdm_progress))
        else:
            list_of_files.append(item)
    return list_of_files


def remove_readonly_flag_from_files_tree(path_to_tree_root):
    root_path = pathlib.Path(path_to_tree_root).resolve()
    print('Collecting list of elements. It may take a while...')
    tqdm_progress = tqdm.tqdm([])
    list_of_files_and_dirs = list_paths_of_all_files_and_directories(root_path, tqdm_progress)
    tqdm_progress.close()

    for path in tqdm.tqdm(list_of_files_and_dirs, desc='Changing permissions'):
        # https://docs.python.org/3/library/os.html#os.chmod
        os.chmod(path, stat.S_IWRITE)


if __name__ == '__main__':
    remove_readonly_flag_from_files_tree(FILE_TREE_ROOT)
