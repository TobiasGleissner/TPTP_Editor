// ==================================================================================================
// === init
// ==================================================================================================

var enable_provers = false;
//
enable_provers = true;
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$(function () {  // on page load
    $.ajaxSetup({ // for crsf protection
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", $("[name=csrfmiddlewaretoken]").val());
            }
        }
    });
    preferences.load(function () { // initialize preferences
        preferences.init();
        if (enable_provers) {
            external_tools.init(function () { // initialize prover module
                toolbar.prover.render_prover_select(); // render prover dropdown on toolbar
                toolbar.prover.render_embedding_select() // render embedding dropdown on toolbar
            });
        }
    });
    layout.init();
    editor.init();
    filebrowser.init();
    modals.init();
});


var layout = {
    // TODO
    // move dragbars where they can be seen
    resize : function (event,init) {
        // init should be true if called for the first time
        // otherwise it should be false
        // default values
        var left_container_width = 200; // TODO
        var footer_height = 50; // TODO
        if (!init) {
            left_container_width = $("#left_container").outerWidth();
            footer_height = $("#footer_container").outerHeight();
        }
        var total_width = $("#wrapper").outerWidth();
        var total_height = $("#wrapper").outerHeight();
        $("#footer_container").css({height:footer_height});
        var header_height = $("#header_container").outerHeight();
        var dragbar_left_width = $("#dragbar_left").outerWidth();
        var dragbar_footer_height = $("#dragbar_footer").outerHeight();

        var main_container_height = total_height - header_height - footer_height;
        var footer_position_top = $("#footer_container").position().top;
        var dragbar_footer_position_top = footer_position_top - 0.5*dragbar_footer_height;
        var dragbar_left_position_left = left_container_width - 0.5*dragbar_left_width;
        var middle_container_position_left = left_container_width;
        var middle_container_width = total_width - left_container_width;
        $("#main_container").css({
            height:main_container_height
        });
        var middle_container_height = $("#middle_container").outerHeight();
        $("#left_container").css({width:left_container_width});
        $("#dragbar_left").css({left:dragbar_left_position_left});
        $("#middle_container").css({left:middle_container_position_left});
        $("#dragbar_footer").css({top:dragbar_footer_position_top});
        // editor resize
        $("#myeditor").css({
            width:middle_container_width,
            height:middle_container_height
        });
        if (!init) { // TODO this is not available from start since ace might be initialized asynchronouesly
            editor.current_instance.resize();
        }
    },
    init : function () {
        // gui resizing
        layout.resize(null,true);
        window.addEventListener("resize", function (event) {
            layout.resize(event,false);
        });
        // dragbar left
        document.getElementById("dragbar_left").addEventListener("mousedown", layout.dragbar_left_start_dragging);
        document.getElementById("dragbar_left").addEventListener("touchstart", layout.dragbar_left_start_dragging);
        document.addEventListener("mousemove", layout.dragbar_left_move);
        document.addEventListener("touchmove", layout.dragbar_left_move);
        document.addEventListener("mouseup", layout.dragbar_left_stop_dragging);
        document.addEventListener("touchend", layout.dragbar_left_stop_dragging);
        // dragbar footer
        document.getElementById("dragbar_footer").addEventListener("mousedown", layout.dragbar_footer_start);
        document.getElementById("dragbar_footer").addEventListener("touchstart", layout.dragbar_footer_start);
        document.addEventListener("mousemove", layout.dragbar_footer_move);
        document.addEventListener("touchmove", layout.dragbar_footer_move);
        document.addEventListener("mouseup", layout.dragbar_footer_stop);
        document.addEventListener("touchend", layout.dragbar_footer_stop);
    },
    resize_dragbar : function (dragbar_left_position_left, dragbar_footer_position_top) {
        if (dragbar_left_position_left) {
            var dragbar_left_width = $("#dragbar_left").outerWidth();
            var main_container_width = $("#main_container").outerWidth();
            // dragbar constraints
            var dragbar_left_min_position_left = -0.5*dragbar_left_width;
            var dragbar_left_max_position_left = main_container_width - 0.5*dragbar_left_width;
            if (dragbar_left_position_left < dragbar_left_min_position_left) {
                dragbar_left_position_left = dragbar_left_min_position_left;
            }
            if (dragbar_left_position_left > dragbar_left_max_position_left) {
                dragbar_left_position_left = dragbar_left_max_position_left;
            }
            // calculations
            var middle_container_position_left = dragbar_left_position_left + dragbar_left_width
            // styles
            $("#left_container").css({width: dragbar_left_position_left});
            $("#dragbar_left").css({left: dragbar_left_position_left});
            $("#middle_container").css({left:middle_container_position_left});
        }
        if (dragbar_footer_position_top) {
            var dragbar_footer_height = $("#dragbar_footer").outerHeight();
            var wrapper_height = $("#wrapper").outerHeight();
            var header_container_height = $("#header_container").outerHeight();
            var main_container_height = $("#main_container").outerHeight();
            // dragbar constraints
            var dragbar_footer_min_position_top = header_container_height - 0.5*dragbar_footer_height;
            var dragbar_footer_max_position_top = wrapper_height + 0.5*dragbar_footer_height;
            if (dragbar_footer_position_top < dragbar_footer_min_position_top) {
                dragbar_footer_position_top = dragbar_footer_min_position_top;
            }
            if (dragbar_footer_position_top > dragbar_footer_max_position_top) {
                dragbar_footer_position_top = dragbar_footer_max_position_top;
            }
            // calculations
            var footer_container_height = wrapper_height - dragbar_footer_position_top;
            // styles
            $("#dragbar_footer").css({top:dragbar_footer_position_top});
            $("#footer_container").css({height:footer_container_height});
        }
        layout.resize(null,false);
    },
    dragging_left : false,
    dragbar_left_start_dragging : function (event) {
        event.preventDefault();
        layout.dragging_left = true;
    },
    dragbar_left_stop_dragging : function (event) {
        event.preventDefault();
        layout.dragging_left = false;
    },
    dragbar_left_move : function (event) {
        if (layout.dragging_left){
            event.preventDefault();
            // position relative to the container (main_container) of dragbar_left
            var x = event.pageX - $('#main_container').offset().left;
            var y = event.pageY - $('#main_container').offset().top;
            layout.resize_dragbar(x,null);
        }
    },
    dragging_footer : false,
    dragbar_footer_start : function (event) {
        event.preventDefault();
        layout.dragging_footer = true;
    },
    dragbar_footer_stop : function (event) {
        event.preventDefault();
        layout.dragging_footer = false;
    },
    dragbar_footer_move : function (event) {
        if (layout.dragging_footer){
            event.preventDefault();
            // position relative to the container (wrapper) of dragbar_footer
            var x = event.pageX - $('#wrapper').offset().left;
            var y = event.pageY - $('#wrapper').offset().top;
            layout.resize_dragbar(null,y);
        }
    }
}


// ==================================================================================================
// === menu user interface
// ==================================================================================================

var menu = {
    file : {
        open_home_directory : function () {
            filebrowser.open_home_directory();
        },
        open_directory : function () {
            modals.directorypicker.open();
        },
        save : function () {
            editor.save_file();
        },
        export : function () {
            var mode = 'document';
            external_tools.export_latex(editor.get_text(), mode , output.render_export_latex_result);
        },
        preferences : function () {
            modals.preferences.open();
        }
    },
    help : {
        about : function () {
            modals.about.open();
        }
    },
    user : function () {
        modals.user.open();
    }
}

// ==================================================================================================
// === toolbar user interface
// ==================================================================================================

var toolbar = {
    prover : {
        run : function () {
            var original_problem = editor.current_instance.getValue();
            // embedding active
            var selected_embedding_option = $("#toolbar_embedding_select")[0].options[$("#toolbar_embedding_select")[0].options.selectedIndex];
            var embedding_type = selected_embedding_option.getAttribute("embeddingtype");
            if (embedding_type != "none") {
                toolbar.prover.run_selected_embedding(original_problem, function (received_data) {
                    output.render_embedding_result(received_data);
                    var status = received_data['status'];
                    if (status == "ok") {
                        var embedded_problem = received_data['embedded_problem'];
                        toolbar.prover.run_selected_prover(embedded_problem,output.render_prover_result);
                    } else {
                        //TODO error
                    }
                });
            // embedding inactive
            } else {
                toolbar.prover.run_selected_prover(original_problem,output.render_prover_result);
            }
        },
        run_selected_embedding : function (problem, callback) {
            var timeout = $("#toolbar_prover_timeout")[0].getAttribute("value");
            var selected_embedding_option = $("#toolbar_embedding_select")[0].options[$("#toolbar_embedding_select")[0].options.selectedIndex];
            var embedding_index = selected_embedding_option.getAttribute("index");
            var embedding_type = selected_embedding_option.getAttribute("embeddingtype");
            var semantics = null;
            var parameters = null;
            switch (embedding_type) {
                case "none":
                    // is catched by toolbar.prover.run
                    break;
                case "semantics_included_in_problem":
                    // do nothing, semantics should be null
                    break;
                case "custom":
                    var embedding = preferences.preferences.embedding[embedding_index];
                    semantics = external_tools.create_semantics("mylogic", embedding);
                    parameters = embedding['parameters'];
                    break;
                case "predefined":
                    var embedding = preferences.predefined.embedding[embedding_index];
                    semantics = external_tools.create_semantics("mylogic", embedding);
                    parameters = embedding['parameters'];
                    break;
            }
            external_tools.embed(semantics, timeout, problem, parameters, callback);
        },
        run_selected_prover : function (problem, callback) {
            var timeout = $("#toolbar_prover_timeout")[0].getAttribute("value");
            var selected_prover_option = $("#toolbar_prover_select")[0].options[$("#toolbar_prover_select")[0].options.selectedIndex]
            var prover_type = selected_prover_option.getAttribute("provertype");
            // TODO
            switch (prover_type) {
                case "predefined_local":
                    var prover_index = selected_prover_option.getAttribute("index");
                    var selected_prover = preferences.predefined.local_provers[prover_index];
                    external_tools.run_predefined_local_prover(selected_prover,timeout,problem,callback);
                    break;
                case "local":
                    var prover_index = selected_prover_option.getAttribute("index");
                    var selected_prover = preferences.preferences.local_prover[prover_index];
                    external_tools.run_local_prover(selected_prover,timeout,problem,callback);
                    break;
                case "remote_default":
                    var prover_index = selected_prover_option.getAttribute("index");
                    var selected_prover = external_tools.default_remote_prover[prover_index];
                    external_tools.run_remote_prover(selected_prover,timeout,problem,callback);
                    break;
                case "remote_configured":
                    ;
            }
        },
        render_prover_select : function () {
            var select_node = $("#toolbar_prover_select")[0];
            // remove all entries first
            while (select_node.firstChild) {
                select_node.removeChild(select_node.firstChild);
            }
            // add predefined local provers
            for (i = 0; i < preferences.predefined.local_provers.length;i++) {
                var prover = preferences.predefined.local_provers[i];
                var option_node = document.createElement("option");
                option_node.innerText = prover.name;
                option_node.setAttribute("index",i);
                option_node.setAttribute("provertype","predefined_local");
                select_node.append(option_node);
            }
            // add local provers
            for (i = 0; i < preferences.preferences.local_prover.length;i++) {
                var prover = preferences.preferences.local_prover[i];
                var option_node = document.createElement("option");
                option_node.innerText = prover.name;
                option_node.setAttribute("index",i);
                option_node.setAttribute("provertype","local");
                select_node.append(option_node);
            }
            // add default remote provers
            for (i = 0; i < external_tools.default_remote_prover.length;i++) {
                var prover = external_tools.default_remote_prover[i];
                var option_node = document.createElement("option");
                option_node.innerText = prover.name;
                option_node.setAttribute("index",i);
                option_node.setAttribute("provertype","remote_default");
                select_node.append(option_node);
            }
        },
        render_embedding_select : function () {
            var select_node = $("#toolbar_embedding_select")[0];
            // remove all entries first
            while (select_node.firstChild) {
                select_node.removeChild(select_node.firstChild);
            }
            // add an element for no embedding
            var option_node = document.createElement("option");
            option_node.innerText = "Do not embed"
            option_node.setAttribute("embeddingtype","none");
            select_node.append(option_node);
            // add an element for embedding with the semantics included in the problem
            var option_node = document.createElement("option");
            option_node.innerText = "Use semantics in the problem"
            option_node.setAttribute("embeddingtype","semantics_included_in_problem");
            select_node.append(option_node);
            // add custom embeddings
            for (i = 0; i < preferences.preferences.embedding.length;i++) {
                var embedding = preferences.preferences.embedding[i];
                var option_node = document.createElement("option");
                option_node.innerText = embedding.name;
                option_node.setAttribute("index",i);
                option_node.setAttribute("embeddingtype","custom");
                select_node.append(option_node);
            }
            // add predefined embeddings
            for (i = 0; i < preferences.predefined.embedding.length;i++) {
                var embedding = preferences.predefined.embedding[i];
                var option_node = document.createElement("option");
                option_node.innerText = embedding.name;
                option_node.setAttribute("index",i);
                option_node.setAttribute("embeddingtype","predefined");
                select_node.append(option_node);
            }
        }
    }
}

// ==================================================================================================
// === modals api interfaces
// ==================================================================================================

var modals = {
    init : function () {
        modals.create_file.init();
        modals.create_directory.init();
        modals.delete_directory.init();
        modals.delete_file.init();
        modals.rename_directory.init();
        modals.rename_file.init();
    },
    about : {
        open : function () {
            $("#about_modal_container").css("display", "block");
        },
        close : function () {
            $("#about_modal_container").css("display", "none");
        }
    },
    directorypicker : {
        open : function () {
            directorypicker.on_modal_open();
            $("#directorypicker_modal_container").css("display", "block");
        },
        close : function () {
            $("#directorypicker_modal_container").css("display", "none");
        }
    },
    preferences : {
        open : function () {
            preferences.on_modal_open();
            $("#preferences_modal_container").css("display", "block");
        },
        close : function () {
            preferences.on_modal_close();
            $("#preferences_modal_container").css("display", "none");
        },
    },
    user : {
        open : function () {
            //user.on_modal_open();
            $("#user_modal_container").css("display", "block");
        },
        close : function () {
            //user.on_modal_close();
            $("#user_modal_container").css("display", "none");
        },
    },
    create_file : {
        node : null, // context node from filebrowser
        init : function () {
            $("#filebrowser_create_file_input_filename").keyup(function(event) {
                if (event.keyCode === 13) {
                    modals.create_file.button_ok();
                }
            });
        },
        open : function (node) {
            modals.create_file.node = node;
            var container = $("#filebrowser_create_file_modal");
            container.parent().parent().css("display", "block");
            $("#filebrowser_create_file_input_filename").focus();
        },
        close : function () {
            $("#filebrowser_create_file_modal").parent().parent().css("display", "none");
            $("#filebrowser_create_file_input_filename").val(""); // reset field
        },
        button_ok : function () {
            var filename = $("#filebrowser_create_file_input_filename").val();
            var path = modals.create_file.node.data.path;
            filesystem.create_file(path + "/" + filename.trim(), function (received_data) {
                if (received_data['status'] == 'ok') {
                    filebrowser.reload_node_content(modals.create_file.node);
                } else {
                    alert(received_data['error_message']);
                }
            });
            modals.create_file.close();
        },
        button_cancel : function () {
            modals.create_file.close();
        }
    },
    create_directory : {
        node : null, // context node from filebrowser
        init : function () {
            $("#filebrowser_create_directory_input_directory").keyup(function(event) {
                if (event.keyCode === 13) {
                    modals.create_directory.button_ok();
                }
            });
        },
        open : function (node) {
            modals.create_directory.node = node;
            var container = $("#filebrowser_create_directory_modal");
            container.parent().parent().css("display", "block");
            $("#filebrowser_create_directory_input_directory").focus();
        },
        close : function () {
            $("#filebrowser_create_directory_modal").parent().parent().css("display", "none");
            $("#filebrowser_create_directory_input_directory").val(""); // reset field
        },
        button_ok : function () {
            var directory = $("#filebrowser_create_directory_input_directory").val();
            var path = modals.create_directory.node.data.path;
            filesystem.create_directory(path + "/" + directory.trim(), function (received_data) {
                if (received_data['status'] == 'ok') {
                    filebrowser.reload_node_content(modals.create_directory.node);
                } else {
                    alert(received_data['error_message']);
                }
            });
            modals.create_directory.close();
        },
        button_cancel : function () {
            modals.create_directory.close();
        }
    },
    delete_directory : {
        node : null, // context node from filebrowser
        init : function () {
            $("#filebrowser_delete_directory_input_directory").keyup(function(event) {
                if (event.keyCode === 13) {
                    modals.delete_directory.button_ok();
                }
            });
        },
        open : function (node) {
            modals.delete_directory.node = node;
            var path = modals.delete_directory.node.data.path;
            var container = $("#filebrowser_delete_directory_modal");
            $("#filebrowser_delete_directory_warning_text").text("All files and subdirectories in " + path + " will be deleted. You might not be able to fully undo this operation!");
            container.parent().parent().css("display", "block");
        },
        close : function () {
            $("#filebrowser_delete_directory_modal").parent().parent().css("display", "none");
        },
        button_delete : function () {
            var path = modals.delete_directory.node.data.path;
            filesystem.delete_directory(path, function (received_data) {
                if (received_data['status'] == 'ok') {
                    filebrowser.reload_node_content(modals.delete_directory.node.getParent());
                } else {
                    alert(received_data['error_message']);
                }
            });
            modals.delete_directory.close();
        },
        button_cancel : function () {
            modals.delete_directory.close();
        }
    },
    rename_directory : {
        node : null, // context node from filebrowser
        init : function () {
            $("#filebrowser_rename_directory_input_directory").keyup(function(event) {
                if (event.keyCode === 13) {
                    modals.rename_directory.button_ok();
                }
            });
        },
        open : function (node) {
            modals.rename_directory.node = node;
            var container = $("#filebrowser_rename_directory_modal");
            container.parent().parent().css("display", "block");
            $("#filebrowser_rename_directory_input_directory").focus();
        },
        close : function () {
            //user.on_modal_close();
            $("#filebrowser_rename_directory_modal").parent().parent().css("display", "none");
            $("#filebrowser_rename_directory_input_directory").val(""); // reset field
        },
        button_ok : function () {
            var directory = $("#filebrowser_rename_directory_input_directory").val();
            var path = modals.rename_directory.node.data.path;
            filesystem.rename_directory(path, directory, function (received_data) {
                if (received_data['status'] == 'ok') {
                    if (modals.rename_directory.node.isRootNode()) { // altered node is visible root node
                        modals.rename_directory.node.data.path = directory;
                        modals.rename_directory.node.setTitle(directory);
                        filebrowser.reload_node_content(modals.rename_directory.node);
                    } else {
                        filebrowser.reload_node_content(modals.rename_directory.node.getParent());
                    }
                } else {
                    alert(received_data['error_message']);
                }
            });
            modals.rename_directory.close();
        },
        button_cancel : function () {
            modals.rename_directory.close();
        }
    },
    delete_file : {
        node : null, // context node from filebrowser
        init : function () {
            $("#filebrowser_delete_file_input_file").keyup(function(event) {
                if (event.keyCode === 13) {
                    modals.delete_file.button_ok();
                }
            });
        },
        open : function (node) {
            modals.delete_file.node = node;
            var path = modals.delete_file.node.data.path;
            var container = $("#filebrowser_delete_file_modal");
            $("#filebrowser_delete_file_warning_text").text("The file " + path + " will be deleted. You might not be able to fully undo this operation!");
            container.parent().parent().css("display", "block");
        },
        close : function () {
            $("#filebrowser_delete_file_modal").parent().parent().css("display", "none");
        },
        button_delete : function () {
            var path = modals.delete_file.node.data.path;
            filesystem.delete_file(path, function (received_data) {
                if (received_data['status'] == 'ok') {
                    filebrowser.reload_node_content(modals.delete_file.node.getParent());
                } else {
                    alert(received_data['error_message']);
                }
            });
            modals.delete_file.close();
        },
        button_cancel : function () {
            modals.delete_file.close();
        }
    },
    rename_file : {
        node : null, // context node from filebrowser
        init : function () {
            $("#filebrowser_rename_file_input_file").keyup(function(event) {
                if (event.keyCode === 13) {
                    modals.rename_file.button_ok();
                }
            });
        },
        open : function (node) {
            modals.rename_file.node = node;
            var container = $("#filebrowser_rename_file_modal");
            container.parent().parent().css("display", "block");
            $("#filebrowser_rename_file_input_file").focus();
        },
        close : function () {
            //user.on_modal_close();
            $("#filebrowser_rename_file_modal").parent().parent().css("display", "none");
            $("#filebrowser_rename_file_input_file").val(""); // reset field
        },
        button_ok : function () {
            var file = $("#filebrowser_rename_file_input_file").val();
            var path = modals.rename_file.node.data.path;
            filesystem.rename_file(path, file, function (received_data) {
                if (received_data['status'] == 'ok') {
                    filebrowser.reload_node_content(modals.rename_file.node.getParent());
                } else {
                    alert(received_data['error_message']);
                }
            });
            modals.rename_file.close();
        },
        button_cancel : function () {
            modals.rename_file.close();
        }
    }
}

function send_control(data, callback) {
    /*
    var data = {
        command: "prove_local",
        prover_command: "satallax",
        prover_arguments: "-t 200",
        logic_problem: "thf(1,conjecture,$true)."
    };
    */
    // url, data, callback
    // static links have to be defined in a template i.e. in the header of editor.html
    // by convention we define all urls in the header of editor.html
    $.ajax({
        url: control_url,
        type: 'POST',
        contentType: 'application/json; charset=utf-8',
        data: JSON.stringify(data),
        dataType: 'text',
        success: function(response_data) {
            var json_dict = JSON.parse(response_data);
            if (callback != null){
                callback(json_dict);
            } else {
                console.log("no callback on send_control");
            }
        },
        error: function(response_data) {
            // for debugging
            alert("server not working correctly.");
            var json_dict = {'status':'server_error'};
            if (callback != null){
                callback(json_dict);
            } else {
                console.log("no callback on send_control");
            }
        }
    });
}
