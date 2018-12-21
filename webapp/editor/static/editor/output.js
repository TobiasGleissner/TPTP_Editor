var output = {
    process_lineendings(string) {
        return string.replace(/(?:\r\n|\r|\n)/g, '<br>');
    },
    render_prover_result : function (received_data) {
        var output_list_node = $("#output")[0];
        if (received_data['status'].startsWith('error')) {
            output_list_node.insertAdjacentHTML("afterbegin",
                '<li>' +
                'error. output was:' +
                received_data['raw'] +
                '</li>');
        } else {
            output_list_node.insertAdjacentHTML("afterbegin",
                '<li>' +
                received_data['prover_name'] + ' says ' +
                '<span class="output_szs_status" >' + received_data['szs_status'] + '</span>' +
                ' wc=' + received_data['wc'] +
                ' cpu=' + received_data['cpu'] +
                '</li>');
        }
    },
    render_export_latex_result : function (received_data) {
        var output_list_node = $("#output")[0];
        if (received_data['status'].startsWith('error')) {
            output_list_node.insertAdjacentHTML("afterbegin",
                '<li>' +
                'error' +
                '</li>');
        } else {
            output_list_node.insertAdjacentHTML("afterbegin",
                '<li>' +
                output.process_lineendings(received_data['latex']) +
                '</li>');
        }
    },
    render_embedding_result : function (received_data) {
        var output_list_node = $("#output")[0];
        if (received_data['status'].startsWith('error')) {
            output_list_node.insertAdjacentHTML("afterbegin",
                '<li>' +
                'error embedding' +
                '</li>');
        } else {
            output_list_node.insertAdjacentHTML("afterbegin",
                '<li>' +
                output.process_lineendings(received_data['embedded_problem']) +
                '</li>');
        }
    },
    render_file_operation_result: function (received_data) {
        var output_list_node = $("#output")[0];
        if (received_data['status'].startsWith('error')) {
            output_list_node.insertAdjacentHTML("afterbegin",
                '<li>' +
                'error on file operation' + '<br>' +
                received_data['error_message'] +
                '</li>');
        } else {
            // pass
        }
    },
    render_semantics : function (semantics) {
        var output_list_node = $("#output")[0];
        output_list_node.insertAdjacentHTML("afterbegin",
            '<li>' +
            output.process_lineendings(semantics) +
            '</li>');
    }
}