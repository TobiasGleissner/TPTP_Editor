import os
import pathlib
import shutil
from abc import abstractmethod

from django.conf import settings
from django.db import models

class Disk_filesystem(models.Model):
    def __init__(self,base_path):
        self.base_path = base_path

    @staticmethod
    def same_paths(path1,path2):
        return os.path.normpath(path1) == os.path.normpath(path2)

    def fs_get_base_path(self, user):
        if  settings.CUSTOM['login_required']: # user mode
            return self.base_path.joinpath(str(user.id))
        else: # not user mode
            return self.base_path

    def on_user_creation(self, user):
        try:
            os.makedirs(str(self.fs_get_base_path(user)))
        except Exception as e:
            print(e)

    def info(self,request,received_data):
        base_path = self.fs_get_base_path(request.user)
        path = base_path.joinpath(received_data['path'].strip('/'))
        send_dict = {
            "status": "ok",
            "exists": False,
            "is_dir": False,
            "is_file": False
        }
        if path.exists():
            send_dict['exists'] = True
        if path.is_dir():
            send_dict['is_dir'] = True
        return send_dict

    def retrieve_file(self, request,received_data):
        filename =  self.fs_get_base_path(request.user).joinpath(received_data['filename'].strip('/'))
        send_dict = {}
        f = None
        try:
            f = open(filename,'r')
            content = f.read()
            send_dict['status'] = 'ok'
            send_dict['filename'] = str(filename)
            send_dict['content'] = content
            return send_dict
        except:
            send_dict['status'] = 'error_could_not_open_file'
            return send_dict
        finally:
            try:
                f.close()
            except:
                pass

    def store_file(self, request,received_data):
        filename = self.fs_get_base_path(request.user).joinpath(received_data['filename'].strip('/'))
        content = received_data['content']
        send_dict = {}
        f = None
        try:
            f = open(filename,'w')
            f.write(content)
            send_dict['status'] = 'ok'
            return send_dict
        except:
            send_dict['status'] = 'error_could_write_file'
            return send_dict
        finally:
            try:
                f.close()
            except:
                pass

    def list_directory(self, request,received_data):
        base_path = self.fs_get_base_path(request.user)
        path = base_path.joinpath(received_data['path'].strip('/'))
        contents = list(path.iterdir())
        contents.sort()
        tree_content_list = []
        for p in contents:
            entry = {}
            entry['title'] = str(p.name)
            entry['path'] = str(p.absolute().relative_to(base_path))
            if p.is_dir():
                entry['lazy'] = True
                entry['folder'] = True
            tree_content_list.append(entry)

        send_dict = {
            'status': 'ok',
            'path': str(path),
            'dir_content': tree_content_list
        }
        return send_dict

    def create_directory(self, request, received_data):
        print("create")
        base_path = self.fs_get_base_path(request.user)
        path = base_path.joinpath(received_data['path'].strip('/'))
        try:
            if Disk_filesystem.same_paths(path, base_path):
                send_dict = {
                    'status': 'error_directory_creation',
                    'error_message': "Home directory cannot be altered."
                }
                return send_dict
            if path.exists():
                send_dict = {
                    'status': 'error_directory_creation',
                    'error_message': "Path already exists."
                }
                return send_dict
            os.makedirs(str(path))
        except IOError as e:
            print(e)
            send_dict = {
                'status': 'error_directory_creation',
                'error_message': str(e)
            }
            return send_dict
        send_dict = {
            'status': 'ok'
        }
        return send_dict

    def delete_directory(self, request, received_data):
        base_path = self.fs_get_base_path(request.user)
        path = base_path.joinpath(received_data['path'].strip('/'))
        try:
            if Disk_filesystem.same_paths(base_path,path):
                send_dict = {
                    'status': 'error_directory_deletion',
                    'error_message': "Home directory cannot be deleted."
                }
                return send_dict
            if not path.exists():
                send_dict = {
                    'status': 'error_directory_deletion',
                    'error_message': "Path does not exists."
                }
                return send_dict
            shutil.rmtree(str(path))
        except IOError as e:
            send_dict = {
                'status': 'error_directory_deletion',
                'error_message': str(e)
            }
            return send_dict
        send_dict = {
            'status': 'ok'
        }
        return send_dict

    def rename_directory(self, request, received_data):
        base_path = self.fs_get_base_path(request.user)
        src_path = base_path.joinpath(received_data['src_path'].strip('/'))
        dest_path = src_path.parent.joinpath(received_data['dest_path'].strip('/'))
        print("src_path",src_path)
        print("dest_path",dest_path)
        try:
            if Disk_filesystem.same_paths(src_path,base_path):
                send_dict = {
                    'status': 'error_directory_renaming',
                    'error_message': "Home directory cannot be renamed."
                }
                return send_dict
            if Disk_filesystem.same_paths(dest_path,base_path):
                send_dict = {
                    'status': 'error_directory_renaming',
                    'error_message': "Directory cannot be renamed to home directory."
                }
                return send_dict
            if dest_path.exists():
                send_dict = {
                    'status': 'error_directory_renaming',
                    'error_message': "Destination path already exists."
                }
                return send_dict
            if not src_path.exists():
                send_dict = {
                    'status': 'error_directory_renaming',
                    'error_message': "Source directory does not exist."
                }
                return send_dict
            if not src_path.is_dir():
                send_dict = {
                    'status': 'error_directory_renaming',
                    'error_message': "Source path is not a directory."
                }
                return send_dict
            src_path.rename(dest_path)
        except Exception as e:
            print(e)
            print()
            send_dict = {
                'status': 'error_directory_renaming',
                'error_message': str(e)
            }
            return send_dict
        send_dict = {
            'status': 'ok'
        }
        return send_dict

    def create_file(self, request, received_data):
        base_path = self.fs_get_base_path(request.user)
        path = base_path.joinpath(received_data['path'].strip('/'))
        try:
            if path.exists():
                send_dict = {
                    'status': 'error_file_creation',
                    'error_message': "Path already exists."
                }
                return send_dict
            f = open(path, "w")
        except IOError as e:
            send_dict = {
                'status': 'error_file_creation',
                'error_message': str(e)
            }
            return send_dict
        finally:
            try:
                f.close()
            except:
                pass
        send_dict = {
            'status': 'ok'
        }
        return send_dict

    def delete_file(self, request, received_data):
        base_path = self.fs_get_base_path(request.user)
        path = base_path.joinpath(received_data['path'].strip('/'))
        try:
            if not path.exists():
                send_dict = {
                    'status': 'error_file_deletion',
                    'error_message': "File does not exists"
                }
                return send_dict
            if not path.is_file():
                send_dict = {
                    'status': 'error_file_deletion',
                    'error_message': "Path is not a file."
                }
                return send_dict
            os.remove(str(path))
        except OSError as e:
            send_dict = {
                'status': 'error_file_deletion',
                'error_message': str(e)
            }
            return send_dict
        send_dict = {
            'status': 'ok'
        }
        return send_dict

    def rename_file(self, request, received_data):
        base_path = self.fs_get_base_path(request.user)
        src_path = base_path.joinpath(received_data['src_path'].strip('/'))
        dest_path = src_path.parent.joinpath(received_data['dest_path'].strip('/'))
        print("src_path",src_path)
        print("dest_path",dest_path)
        try:
            if Disk_filesystem.same_paths(dest_path,base_path):
                send_dict = {
                    'status': 'error_file_renaming',
                    'error_message': "File cannot be renamed to home directory."
                }
                return send_dict
            if dest_path.exists():
                send_dict = {
                    'status': 'error_file_renaming',
                    'error_message': "Destination path already exists."
                }
                return send_dict
            if not src_path.exists():
                send_dict = {
                    'status': 'error_file_renaming',
                    'error_message': "Source file does not exist."
                }
                return send_dict
            if not src_path.is_file():
                send_dict = {
                    'status': 'error_file_renaming',
                    'error_message': "Source path is not a file."
                }
                return send_dict
            src_path.rename(dest_path)
        except Exception as e:
            send_dict = {
                'status': 'error_file_renaming',
                'error_message': str(e)
            }
            return send_dict
        send_dict = {
            'status': 'ok'
        }
        return send_dict
