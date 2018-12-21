import os
import shutil
import logging
from .db_structure import File_Browser_Stats


'''
any File_Browser instance expects a request_dictionary (at least root path needs to be set): 
[{'status':'some_status'}, {'path': 'path_to_be_extended'}, {'root_path': 'path_to_root_directory'}, {result_tree_set} ]

any functionality of a File_Browser instance will return a dictionary
at least 
{'status':'errorcode'}


1. INIT FULLY REALIZED TREE
File_Browser_Request_Handler.init_result_tree(exchange_set)

1.a.1 INIT DIRECTORY OF TREE
File_Browser_Request_Handler.init_root_tree(exchange_set)

1.a.2 EXTEND_GIVEN_TREE_BY DIRECTORY OF TREE
File_Browser_Request_Handler.extend_file_browser_tree(exchange_set)


File Browser Operations to manipulate file structure:
    2. Create Directory
    create a File_Browser object fb
    fb.create_file(filename)
    
    3. Create Directory
    create a File_Browser object fb
    fb.ceate_folder(dir_name)
    
    4. Move Resource
    create a File_Browser object fb
    fb.move(src, dst)
    
    5. Copy Resource
    create a File_Browser object fb
    fb.copy(src, dst)
    
    6. Rename Resource
    create a File_Browser object fb
    fb.rename(src, dst)
    
    7. Delete Resource
    create a File_Browser object fb
    fb.delete(resource)

'''

'''
INITIALIZE FULLY REALIZED TREE TOP DOWN FROM ROOT_PATH FOR LAZY BUILD UP:

static method: 
File_Browser_Request_Handler.init_result_tree(exchange_set)

expects exchange_set to be given:
[{'status':'some_status'}, {'path': 'path_to_be_extended'}, {'root_path': 'path_to_root_directory'}, {result_tree_set} ]

most request will be handled by GUI, which will take care while handling path names in correct fashion
return a dictionary as shown in FILE_Browser_Request_Handler.result_tree


INITIALIZE ROOT DIRECTORY TREE FOR LAZY BUILD UP:

static method: 
File_Browser_Request_Handler.extend_file_browser_tree(exchange_set)

expects exchange_set to be given:
[{'status':'some_status'}, {'path': 'path_to_be_extended'}, {'root_path': 'path_to_root_directory'}, {result_tree_set} ]


EXTEND DIRECTORY TREE AND INSERT IN SO FAR PARSED TREE:
static method:
File_Browser_Request_Handler.extend_result_tree(path)
'''



class File_Browser_Request_Handler():

    # root path to begin to render the tree
    #chosen initialy by the user
    root_path = False

    # !!!!!!!!!! RETURN VALUE WILL BE TREE AS DESCRIBED BELOW OR ERROR MSG {'status': 'SOMEERROR'} !!!!!!!!
    # fully realized tree, from root path as deep as the user browsed
    # will be build lazy
    # is stored in db in order to reuse it for restoring session purposes
    # the order to build the dictionary is a set of dictionaries containing opened directories and files beginning from root
    # exchange JSON format in between client and server is:
    #
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # !!!!!     status will always be at JSON[0]                                              !!!!!
    # !!!!!     path will always be at JSON[1]                                                !!!!!
    # !!!!!     root path of the tree to be shown will always be at JSON[2]                   !!!!!
    # !!!!!     so far realized tree will be at JSON[3]                                       !!!!!
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    #
    # for instance:
    #
    # [{ 'status': 'errormessage/OK'},
    #  { 'path' : 'path/to/requested/folder'},
    #  { 'root_path' : 'path/to/root/directory'},
    #  { "text" : "Folder 1", "children" : [
    #      { "text" : "ChildNode1.txt", "icon" : "jstree-file" },
    #      { "text" : "Subfolder 1", "state" : { "selected" : true }, "children" : [
    #              { "text" : "ChildNode11.txt", "icon" : "jstree-file" },
    #              { "text" : "ChildNode12.txt", "icon" : "jstree-file" }
    #      ]
    #      }
    #    ]
    #  },
    #  { "text" : "Folder 2" }
    #  ]
    result_data = [{},{},{},{}]

    status = True

    file_browser = False

    def __init__(self):
        pass

    # in case root path is not valid, file_browser stays False and instance of Request Handler will be terminated
    def set_file_browser(self, path = False):
        if path:
            self.file_browser = File_Browser(path)

    # root path will only be set once initialy!!!!
    def set_root_path(self, exchange_set):

        if self.root_path == False:

            if os.path.isdir(exchange_set[2]['root_path']) == False:
                self.status = 'RootPathIsNoDirectory'
                logging.debug('Passed Root Path is no Directory')

            elif self.check_directory_exists(exchange_set[2]['root_path']) == False:
                self.status = 'RootPathNotExists'
                logging.debug('Passed Root Path does not exist')

            elif os.path.isdir(exchange_set[2]['root_path']) and self.check_directory_exists(exchange_set[2]['root_path']):
                self.root_path = exchange_set[2]['root_path']

    def check_directory_exists(self, directory_path):
        if os.path.exists(directory_path):
            return True
        else:
            return False

    def set_pwd(self, path):

        if os.path.isdir(path) == False:
            self.status = 'PassedPathIsNoDirectory'
            logging.debug('Given path is no directory')

        elif os.path.exists(path) == False:
            self.status = 'PassedPathNotExists'
            logging.debug('Passed path does not exist')

        elif os.path.isdir(path) and os.path.exists(path):
            os.chdir(path)
            return True

    # function to set up the root of file browser to be rendered in client
    # initialize function will compute content of chosen root directory and any other folder benaeth it
    @staticmethod
    def init_result_tree(exchange_set):
        print(exchange_set)

        fbrh = File_Browser_Request_Handler()

        # file_browser object will only be instiated, if everything is okay
        # meaning root directory is valid and set
        fbrh.set_root_path(exchange_set)
        fbrh.set_pwd(fbrh.root_path)
        fbrh.set_file_browser(fbrh.root_path)

        # initiate root directory and set contents
        if isinstance(fbrh.file_browser, File_Browser):
            fbrh.file_browser.get_folder_content()
            fbrh.result_data[3]= fbrh.translate_result_dictionary_to_result_tree()

            fbrh.compose_result_data(exchange_set)

            # is a set of folders objects, with 'text' and 'path'
            parser_working_set=[]
            folder_obj_set = fbrh.get_folder_object_set(fbrh.file_browser.result_dic['folders'], fbrh.root_path)

            for dir in folder_obj_set:
                parser_working_set.append(dir)

            while len(parser_working_set)>0:

                # pull 1st element
                folder_object = parser_working_set[0]
                parser_working_set = parser_working_set[1:]
                # set path for current object
                parser_path = folder_object['path']

                content_set= {'content':[], 'files':[], 'folders':[], 'path': parser_path}

                folder_content = os.listdir(parser_path)

                for item in folder_content:
                    content_set['content'].append(item)
                    if os.path.isdir(parser_path+"/"+item):
                        content_set['folders'].append(item)
                    elif os.path.isfile(parser_path+"/"+item):
                        content_set['files'].append({item})

                insert_tree = fbrh.build_insert_tree_from_content(content_set)

                os.chdir(parser_path)
                fbrh.expand_tree(insert_tree, fbrh.result_data[3])

                folder_set = []
                for dir in content_set['folders']:
                    folder_set.append(dir)

                folder_obj_set = fbrh.get_folder_object_set(folder_set, os.getcwd())
                if len(folder_obj_set)>0:

                    for dir in folder_obj_set:
                        parser_working_set.append(dir)

            fbrh.save_file_browser_status()
            return fbrh.result_data

        else:
            # this error handles issues while initializing error of root path
            logging.debug('Directory does not exist')
            return {'status': 'DirectoryNotExistsError'}

    # function to set up the root of file browser to be rendered in client
    # initialize function will compute content of chosen root directory
    # rest will be taken care of in lazy fashion
    @staticmethod
    def init_root_tree(exchange_set):

        fbrh = File_Browser_Request_Handler()

        # file_browser object will only be instiated, if everything is okay
        # meaning root directory is valid and set

        fbrh.set_root_path(exchange_set)

        fbrh.set_pwd(fbrh.root_path)
        fbrh.set_file_browser(fbrh.root_path)

        if isinstance(fbrh.file_browser, File_Browser):
            fbrh.file_browser.get_folder_content()
            fbrh.result_data[3]= fbrh.translate_result_dictionary_to_result_tree()
            fbrh.compose_result_data(exchange_set)
            return fbrh.result_data

        else:
            # this error handles issues while initializing error of root path
            logging.debug('Directory does not exist')
            return {'status': 'DirectoryNotExistsError'}

    # method to set up folder object as helper data structure while parsing
    def get_folder_object_set(self, folder_set, path_to_folders):

        #print(folder_set)
        folder_object_set = []
        for dir in folder_set:

            path = path_to_folders+'/'+dir
            folder_object = {'text':dir, 'path':path}
            folder_object_set.append(folder_object)

        return folder_object_set

    # content_set= {'content':[], 'files':[], 'folders':[], 'path': parser_path}
    def build_insert_tree_from_content(self, content_set):
        result_tree = []
        # appending folders first
        for dir in content_set['folders']:
            leaf = {'text': dir}
            result_tree.append(leaf)

        #appending files into tree
        for file in content_set['files']:
            leaf = {'text': file, "icon" : "jstree-file"}
            result_tree.append(leaf)

        return result_tree

    def restore_tree_from_db(self):

        tree = File_Browser_Stats.load_filebrowser_status()
        if len(tree) > 0:
            self.result_data = [{'status': 'OK'}, {}, {}, {tree}]

        else:
            self.result_data = [{'status': 'LoadDataFromDBError'}, {}, {}, {}]
            logging.debug('The data return by loading function from db returned an empty set / error')

    #commonly used method to migrate results of File_Browser request into result_data
    #the idea is to provide data for jstree to visualize the directory structure
    #returns the result of requested path to be parsed as tree structure of its contents
    def translate_result_dictionary_to_result_tree(self):

        #isinstance(self.file_browser, File_Browser)
        if self.file_browser.result_dic['status'] == 'OK':
            result_tree = []
            # appending folders first
            for dir in self.file_browser.result_dic['folders']:
                leaf = {'text': dir}
                result_tree.append(leaf)

            #appending files into tree
            for file in self.file_browser.result_dic['files']:
                leaf = {'text': file, "icon" : "jstree-file"}
                result_tree.append(leaf)

            return result_tree
        else:
            self.result_data[0] = self.file_browser.result_dic['status']
            return False


    def compose_result_data(self, exchange_set):

        if self.status != True:
            self.result_data[0]['status'] = self.status
        else:
            self.result_data[0]['status'] = 'OK'

            if len(exchange_set[1]['path']) > 0:
                self.result_data[1]['path'] = exchange_set[1]['path']
            if len(exchange_set[2]['root_path']) > 0:
                self.result_data[2]['root_path'] = exchange_set[2]['root_path']


    # idea to push the result tree into the existing one
    # get pwd where tree is to be set: os.getcwd()
    # parse the path into an array
    # for each directory follow from root folder through teh already realized tree
    # insert values for children and put the insert_tree there
    def expand_tree(self, insert_tree, set_tree):

        if self.root_path == "/":
            rel_path_to_root = os.getcwd()
        else:
            rel_path_to_root = os.path.relpath(os.getcwd(), self.root_path)

        rev_ordered_dirs=[]
        con = True

        while con:
            base_name = os.path.basename(rel_path_to_root)
            if base_name =='' or base_name == "/":
                con = False
            else:
                rev_ordered_dirs.append(os.path.basename(rel_path_to_root))
                rel_path_to_root= os.path.dirname(rel_path_to_root)

        # dirs contains all directories leading up to the one where the tree needs to be inserted
        # !!!!!!!dirs is in reverse order!!!!!

        # last item needs to be treated special because it has no children subtree
        last_directory = rev_ordered_dirs[0]
        rev_ordered_dirs=rev_ordered_dirs[1:]
        dirs=[]

        # invert the directory list
        while len(rev_ordered_dirs)>0:

            dirs.append(rev_ordered_dirs[-1])
            rev_ordered_dirs= rev_ordered_dirs[0:-1]

        # traverse the tree for the point to put in the tree
        traverse_tree = set_tree
        error = False

        for folder in dirs:

            found = False
            for item in traverse_tree:
                if item['text'] == folder:
                    traverse_tree = item['children']
                    found = True
                else:
                    pass
            if found == False:
                error = True
                self.status='TraverseTreeAppendingOperationError'
                logging.debug('Error while traversing the already realized tree in order to put in the result tree with resources found.')
            else:
                pass

        # put in the tree at last next point if found at last_directory
        if error:
            pass
        else:
            for item in traverse_tree:

                if item['text'] == last_directory:
                    item['children'] = insert_tree
                    self.result_data[3] = set_tree
                else:
                    pass

    # method to write data into DB for later restoring purposes
    def save_file_browser_status(self):

        if len(self.result_data[3])>0:

            save_object = File_Browser_Stats.save_file_browser_status(self.result_data[3])


    # an already created tree is prerequisite to this function and expected
    # a path needs to be passed wich will be extend from current tree
    # a root directory is to be expected to passed as well
    @staticmethod
    def extend_file_browser_tree(exchange_set):

        fbrh = File_Browser_Request_Handler()

        fbrh.set_root_path(exchange_set)
        fbrh.set_pwd(exchange_set[1]['path'])

        fbrh.set_file_browser(os.getcwd())

        if isinstance(fbrh.file_browser, File_Browser):
            fbrh.file_browser.get_folder_content()
            result_tree = fbrh.translate_result_dictionary_to_result_tree()
            fbrh.compose_result_data(exchange_set)
            fbrh.expand_tree(result_tree, exchange_set[3])
            print(fbrh.result_data)
            return fbrh.result_data

        else:
            # this error handles issues while initializing error of root path
            logging.debug('Directory does not exist')
            return {'status': 'DirectoryNotExistsError'}

class File_Browser:

    result_dic =    {'status': '',
                     'files': [],
                     'folders': [],
                     'dir_name': '',
                     'dir_path': '',
                     'content': []
                     }

    def __init__(self, path):
        self.set_pwd(path)

    def set_pwd(self, path):
        if os.path.isdir(path) and os.path.exists(path):
            os.chdir(path)
            return True
        else:
            return False

    # DirectoryNotExistsError if requested folder does not exist
    def get_folder_content(self):
        if os.getcwd() == False:
            self.result_dict['status'] = 'DirectoryNotExistsError'
            logging.debug('Directory does not exist')

        directory = Directory(os.getcwd())
        self.result_dic = directory.get_content_dict()

    # FileExistsCreateError a ressource with the same name already exists at the location
    @staticmethod
    def create_file(file_name):
        fb = File_Browser
        if fb.check_directory_exists(os.getcwd()+'/'+file_name):
            fb.result_dic['status'] = 'FileExistsCreateError'
            logging.debug('Cannot create that resource due to name is already taken.')
            return {fb.result_dic}
        else:
            with open(file_name, 'w') as f:
                pass
            f.close()
            fb.result_dic['status']= 'OK'
            return fb.result_dic

    # DirExistsCreateError directory already exists or name is taken
    @staticmethod
    def create_folder(folder_name):
        fb = File_Browser
        if fb.check_directory_exists(os.getcwd()+'/'+folder_name):
            fb.result_dic['status'] = 'DirExistsCreateError'
            logging.debug('Directory already exists')
            return fb.result_dic
        else:
            os.mkdir( os.getcwd()+'/'+folder_name )
            fb.result_dic['status'] = 'OK'
            return fb.result_dic

    #SrcDirDoesNotExistsError source resource does not exist
    #DstDirAlreadyExistsError the name is already taken
    @staticmethod
    def rename(src_name, dst_name):
        fb = File_Browser
        if fb.check_directory_exists(os.getcwd()+'/'+src_name):

            if os.path.exists(os.getcwd()+'/'+dst_name):
                fb.result_dic['status'] = 'DstDirAlreadyExistsError'
                logging.debug('The requested name is already taken.')
                return fb.result_dic

            else:
                os.rename(os.getcwd()+'/'+src_name, os.getcwd()+'/'+dst_name)
                fb.result_dic['status'] = 'OK'
                return fb.result_dic
        else:
            fb.result_dic['status'] = 'SrcDirDoesNotExistsError'
            logging.debug('Source does not exists')
            return fb.result_dic

    #CopySrcUnknownTypeError an unknown error occured at the source location that could be specified
    @staticmethod
    def copy(src, dst):

        fb = File_Browser

        #copy type file
        if os.path.isfile(src):
            fb.copyfile(src, dst)
            return fb.result_dic

        #copy type folder
        elif os.path.isdir(src):
            fb.copydirectory(src, dst)
            return fb.result_dic

        #dont copy due to some error
        #could be specified further in the future
        else:
            fb.result_dic['status'] = 'CopySrcUnknownTypeError'
            logging.debug('An unspecified error ocured at the source location to be copied.')
            return fb.result_dic

    '''
    in case dst is already existend, it will be replaced

    elif self.check_directory_exists(dst_file_path):
        return {'status': 'CopyDstFileAlreadyExistsError'}
    '''

    # CopySrcFileNotExistsError - source file does not exist
    # CopyDestinationNotWriteableError - destination is write protected or not mounted or does no exist or not writeable
    # CopyDestinationPermissionError - permission denied to write at destinition
    # CopyUnknownError - catchall for all unkown errors
    def copyfile(self, src_file_path, dst_file_path):

        if self.check_directory_exists(src_file_path) == False:
            self.result_dic['status']= 'CopySrcFileNotExistsError'
            logging.debug('Source file does not exist')

        else:
            try:
                shutil.copyfile(src_file_path, dst_file_path)
                self.result_dic['status'] = 'OK'

            # destinition might be not writable or protected
            except IOError:
                self.result_dic['status'] = 'CopyDestinationNotWriteableError'
                logging.debug('Destination is write protected or not mounted or does no exist or not writeable.')

            # server process might not have permissions on file system
            except PermissionError:
                self.result_dic['status'] = 'CopyDestinationPermissionError'
                logging.debug('Permission denied to write at destinition.')

            # any other error will be fetched
            except Exception:
                self.result_dic['status'] = 'CopyUnknownError'
                logging.debug('Catchall for all unknown errors.')

    '''
    in case dst is already existend, it will be replaced
    elif self.check_directory_exists(dst_dir_path):
        return {'status': 'CopyDstDirAlreadyExistsError'}
    '''

    # CopySrcDirNotExistsError - source directory does not exist
    # CopyDestinationNotWriteableError - destination is not writeable, write protected, not mounted anymore or not writeable
    # CopyDestinationPermissionError - no permission to write at destination
    #CopyFolderUnknownError - catchall error for any unkonwn error
    def copydirectory(self, src_dir_path, dst_dir_path):

        if self.check_directory_exists(src_dir_path) == False:
            self.result_dic['status'] = 'CopySrcDirNotExistsError'
            logging.debug('Source directory does not exist.')

        else:
            try:
                shutil.copytree(src_dir_path, dst_dir_path)
                self.result_dic['status'] = 'OK'

            # destinition might be not writable or protected
            except IOError:
                self.result_dic['status'] = 'CopyDestinationNotWriteableError'
                logging.debug('Destination is not writeable, write protected, not mounted or not writeable.')

            # server process might not have permissions on file system
            except PermissionError:
                self.result_dic['status'] = 'CopyDestinationPermissionError'
                logging.debug('No permission to write at destination.')

            # any other error will be fetched
            except Exception:
                self.result_dic['status'] = 'CopyFolderUnknownError'
                logging.debug('Catchall error for any unspecified error.')

    # MoveSrcNotExistsError - Source does not exist
    # MoveDstAlreadyExistsError - destination resource already exists
    @staticmethod
    def move(src_path, dst_path):

        fb = File_Browser

        if fb.check_directory_exists(src_path) == False:
            fb.result_dic['status'] = 'MoveSrcNotExistsError'
            logging.debug('Source resource does not exist')
            return fb.result_dic

        elif fb.check_directory_exists(dst_path):
            fb.result_dic['status'] = 'MoveDstAlreadyExistsError'
            logging.debug('Destination resource does already exist')
            return fb.result_dic

        else:
            shutil.move(src_path, dst_path)
            fb.result_dic['status'] = 'OK'
            return fb.result_dic

    #DeleteUnknownTypeError - catchall error for any unspecified error
    @staticmethod
    def delete(resource):

        fb = File_Browser

        if os.path.isdir(resource):
            return fb.delete_directory(resource)

        elif os.path.isfile(resource):
            return fb.delete_file(resource)

        else:
            fb.result_dic['status'] = 'DeleteUnknownTypeError'
            logging.debug('An unspecified error occured')

    # FileNotExistsDeleteError - file does not exist or had been deleted already
    def delete_file(self, file_path):

        if self.check_directory_exists(file_path) == False:
            self.result_dic['status'] =  'FileNotExistsDeleteError'
            logging.debug('File does not exist or had been deleted already.')

        else:
            shutil.remove(file_path)
            self.result_dic['status'] = 'OK'

    #DirNotExistsDeleteError - Directory does not exist or had been deleted already
    def delete_directory(self, dir_path):

        if self.check_directory_exists(dir_path) == False:
            self.result_dic['status'] = 'DirNotExistsDeleteError'
            logging.debug('Directory does not exist or had been deleted already.')

        else:
            shutil.rmtree(dir_path)
            self.result_dic['status'] = 'OK'

class Directory:
    directory_name = ""
    path = ""
    content = []
    files = []
    directories = []
    result_dict = {}

    def __init__(self, path):
        self.directory_name = self.get_directory_name_from_path(path)
        self.path = path
        self.init_content()

    def get_directory_name_from_path(self, path):
        return os.path.split(path)[1]

    def init_content(self):

        # check if given path is an actual path or file
        # false if path is broken symlink or permission is denied
        if os.path.exists(self.path):
            self.content = os.listdir(self.path)

        # TODO: something needs to happen here, user interaction and visualisation
        else:
            self.content = False

    def sort_content_by_type(self):

        if len(self.content) > 0:

            # 1 the path needs to be composed in order to use them for isfile and isfolder

            for content_item in self.content:
                if os.path.isfile(self.path + "/" + content_item):
                    self.files.append(content_item)

                elif os.path.isdir(self.path + "/" + content_item):
                    self.directories.append(content_item)

    # get the result dictionary
    # NoDirError - directory to get content from does not exist
    def get_content_dict(self):

        # there is no directory in given path
        if self.content == False:
            self.result_dict['status']= "NoDirError"
            logging.debug('Directoy does not exists.')

        else:
            self.sort_content_by_type()
            self.result_dict = {'status': 'OK', 'content' : self.content, 'dir_name': self.directory_name, 'path':self.path, 'folders':self.directories, 'files':self.files}

        return self.result_dict

'''
root = "/home"
exchange_set = [{'status':'OK'}, {'path':''}, {'root_path': "/home"}, {}]
fbrh = File_Browser_Request_Handler()
fbrh.init_result_tree(exchange_set)
print(fbrh.result_data)
'''