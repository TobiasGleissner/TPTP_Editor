var editor = {
    current_instance : null,
    current_file : null,
    init : function () {
        editor.current_instance = ace.edit("myeditor");
        //editor.current_instance.setTheme("ace/theme/monokai");
        //editor.current_instance.session.setMode("ace/mode/javascript");
        editor.current_instance.getSession().setMode("ace/mode/mode-tptp");
        editor.current_instance.resize();
        /*
        editor.setOptions({
        enableBasicAutocompletion: true,
        enableLiveAutocompletion: false
        });*/
                ///General settings for the editor
        //    editor.session.setUseWrapMode(true);
        //    editor.setHighlightActiveLine(false);
        //    editor.setShowPrintMargin(false);
    },
    on_resize : function () {
        editor.current_instance.resize();
    },
    open_file : function (filename) {
        filesystem.retrieve_file(filename, function (received_data) {
            // TODO: error handling
            var content = received_data['content'];
            var filename = received_data['filename'];
            editor.current_instance.session.setValue(content);
            editor.current_file = filename;
            console.log(received_data);
        });
    },
    save_file : function () {
        var content = editor.get_text();
        var filename = editor.current_file;
        filesystem.store_file(filename, content, function (received_data) {
            // TODO: error handling
        });
    },
    get_text : function () {
        return editor.current_instance.getValue();
    }
}