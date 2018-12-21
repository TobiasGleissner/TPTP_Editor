var filesystem = {
    info : function (path_, callback) {
        data = {
            command : 'path_info',
            path : path_
        };
        send_control(data, callback);
    },
    retrieve_file : function (file, callback) {
        data = {
            command : 'retrieve_file',
            filename : file
        };
        send_control(data, callback);
    },
    store_file : function (file, cont, callback) {
        data = {
            command : 'store_file',
            filename : file,
            content : cont
        };
        send_control(data, callback);
    },
    create_file: function (path_, callback) {
        data = {
            command : 'create_file',
            path : path_
        };
        send_control(data, callback);
    },
    create_directory: function (path_, callback) {
        data = {
            command : 'create_directory',
            path : path_
        };
        send_control(data, callback);
    },
    delete_file: function (path_, callback) {
        data = {
            command : 'delete_file',
            path : path_
        };
        send_control(data, callback);
    },
    delete_directory (path_, callback) {
        data = {
            command : 'delete_directory',
            path : path_
        };
        send_control(data, callback);
    },
    rename_file: function (src_path_, dest_path_, callback) {
        data = {
            command : 'rename_file',
            src_path : src_path_,
            dest_path : dest_path_
        };
        send_control(data, callback);
    },
    rename_directory: function (src_path_, dest_path_, callback) {
        data = {
            command : 'rename_directory',
            src_path : src_path_,
            dest_path : dest_path_
        };
        send_control(data, callback);
    }
}

var filebrowser = {
    init : function () {
        filebrowser.contextmenu_directory._menu = new ContextMenu(
            "filebrowser_contextmenu_directory",
            function (el) {
                if (!el.classList || !el.classList.contains("fancytree-title")) return false; // class is not "fancytree-title"
                if (el.parentNode.classList && el.parentNode.classList.contains("fancytree-folder")) return true; // is a folder
                return false;
            },
            [
                {
                    "name": "Create File",
                    "class": "",
                    "action": filebrowser.contextmenu_directory.create_file
                },
                {
                    "name": "Create Directory",
                    "class": "",
                    "action": filebrowser.contextmenu_directory.create_directory
                },
                {
                    "name": "Delete",
                    "class": "",
                    "action": filebrowser.contextmenu_directory.delete_directory
                },
                {
                    "name": "Rename",
                    "class": "",
                    "action": filebrowser.contextmenu_directory.rename_directory
                }
            ]
        );

        filebrowser.contextmenu_file._menu = new ContextMenu(
            "filebrowser_contextmenu_file",
            function (el) {
                if (!el.classList || !el.classList.contains("fancytree-title")) return false; // class is not "fancytree-title"
                if (el.parentNode.classList && el.parentNode.classList.contains("fancytree-folder")) return false; // parent is a folder
                return true;
            },
            [
                {
                    "name": "Delete",
                    "class": "",
                    "action": filebrowser.contextmenu_file.delete_file
                },
                {
                    "name": "Rename",
                    "class": "",
                    "action": filebrowser.contextmenu_file.rename_file
                },
                {
                    "name": "Run Prover",
                    "class": "",
                    "action": filebrowser.contextmenu_file.run_prover
                }
            ]
        );
    },
    open_home_directory : function () {
        filebrowser.open_directory("/");
    },
    open_directory : function (directory_path) {
        var filebrowser_container_node = $("#sidekick_filebrowser_content")[0];
        // remove all entries firsttask
        while (filebrowser_container_node.firstChild) {
            filebrowser_container_node.removeChild(filebrowser_container_node.firstChild);
        }
        filebrowser_container_node.insertAdjacentHTML("afterbegin",
            '<div id="file_browser"></div>'
        );
        filebrowser.tree = $("#file_browser").fancytree({
            //escapeTitles: true,
            //quicksearch: true,
            //aria: true,
            //strings: this.opts.loc,
            debugLevel: 0, // 0:quiet, 1:normal, 2:debug
            source: [{title:directory_path,folder:true,lazy:true,path:directory_path}],
            lazyLoad: function(event, treedata){
                //var node = treedata.node;
                //data.node.load(true);
                d = {
                    command: 'list_directory',
                    path: treedata.node.data.path
                };
                treedata.result = {
                    url: control_url,
                    type: 'POST',
                    data: JSON.stringify({command:'list_directory',path: treedata.node.data.path}),
                    cache: false
                }
            },
            postProcess : function(event, treedata) { // process original answer on lazyload here
                var original_response = treedata.response;
                treedata.result = original_response.dir_content
            },
            click : function (event, treedata) {
                if (!treedata.node.folder){
                    editor.open_file(treedata.node.data.path);
                }
            }
        }).fancytree("getTree");;
    },
    contextmenu_directory : {
        create_file: function (clickedElement) {
            modals.create_file.open(filebrowser.get_last_node());
        },
        create_directory: function (clickedElement) {
            modals.create_directory.open(filebrowser.get_last_node());
        },
        delete_directory: function (clickedElement) {
            modals.delete_directory.open(filebrowser.get_last_node());
        },
        rename_directory: function (clickedElement) {
            modals.rename_directory.open(filebrowser.get_last_node());
        }
    },
    contextmenu_file: {
        delete_file: function (clickedElement) {
            modals.delete_file.open(filebrowser.get_last_node());
        },
        rename_file: function (clickedElement) {
            modals.rename_file.open(filebrowser.get_last_node());
        },
        run_prover: function (clickedElement) {
            console.log("run_prover");
            // TODO
        }
    },
    get_last_node : function () {
        return filebrowser.tree._lastMousedownNode;
    },
    reload_node_content : function (node) {
        node.load(forceReload = true);
    }

}

// TODO alter the prototype for instantiating this
var directorypicker = {
    root_path : "/", // this has to change somehow, probably on django
    selected : null,
    on_modal_open : function () {
        $("#directorypicker_tree").fancytree({
            //escapeTitles: true,
            //quicksearch: true,
            //aria: true,
            //strings: this.opts.loc,
            debugLevel: 0, // 0:quiet, 1:normal, 2:debug
            source: [{title:directorypicker.root_path,folder:true,lazy:true,path:directorypicker.root_path}],
            lazyLoad: function(event, treedata){
                //var node = treedata.node;
                //data.node.load(true);
                d = {
                    command: 'list_directory',
                    path: treedata.node.data.path
                };
                treedata.result = {
                    url: control_url,
                    type: 'POST',
                    data: JSON.stringify({command:'list_directory',path: treedata.node.data.path}),
                    cache: false
                }
            },
            postProcess : function(event, treedata) { // process original answer on lazyload here
                var original_response = treedata.response;
                treedata.result = original_response.dir_content
            },
            click : function (event, treedata) {
                if (treedata.node.folder){
                    directorypicker.selected = treedata.node.data.path;
                } else {
                    directorypicker.selected = null;
                }
            }
        });
    },
    button_open : function () {
        if (directorypicker.selected) {
            filebrowser.open_directory(directorypicker.selected);
        } else {
        }
        modals.directorypicker.close();
    },
    button_cancel : function () {
        modals.directorypicker.close();
    }
}

