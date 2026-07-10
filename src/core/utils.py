import os


def get_file_basename(file_path):
    return os.path.basename(file_path)


def get_file_extension(file_path):
    return os.path.splitext(file_path)[1].lower()


def validate_output_folder(folder_path):
    if not folder_path:
        return False, "Output folder is empty"
    if not os.path.exists(folder_path):
        return False, "Output folder does not exist"
    if not os.path.isdir(folder_path):
        return False, "Output path is not a directory"
    return True, "Valid output folder"