var external_tools = {
    default_remote_prover : {},
    init : function (callback) {
        // initialize remote provers
        data = {
            command: 'get_remote_provers'
        }
        send_control(data,function (received_data) {
            external_tools.default_remote_prover = received_data['remote_provers'];
            if (callback) {
                callback();
            }
        })
    },

    /**
     * Creates a tptp logic specification from an embedding dictionary
     *
     * @param {string}      name                    identifier of the TPTP sentence that states the logic specification
     * @param {dict}        embedding_parameters    keys 'domain', 'constants', 'consequence', 'modalities' with
     *                                              valid values in the TPTP logic specification format
     * @returns {string}                            TPTP logic specification
     */
    create_semantics : function (name, embedding_parameters) {
        var specification = "" +
            "thf(" + name + ",logic,(\n" +
            "    $modal := [\n" +
            "        $constants := " + embedding_parameters['constants'] + ",\n" +
            "        $quantification := " + embedding_parameters['domains'] + ",\n" +
            "        $consequence := " + embedding_parameters['consequences'] + ",\n" +
            "        $modalities := " + embedding_parameters['modalities'] + "\n" +
            "]))."
        return specification;
    },
    run_local_prover : function (prover,timeout,problem,callback) {
        data = {};
        data['command'] = 'prove_local';
        data['prover_name'] = prover.name
        data['prover_dialects'] = prover.dialects
        data['prover_command'] = prover.command;
        data['prover_parameters'] = prover.parameters;
        data['wc_limit'] = timeout;
        data['cpu_limit'] = timeout * 100; // TODO make this reasonable
        data['problem'] = problem;
        send_control(data,callback);
    },
    run_predefined_local_prover : function (prover,timeout,problem,callback) {
        data = {};
        data['command'] = 'prove_local_predefined';
        data['prover_name'] = prover.name
        data['wc_limit'] = timeout;
        data['cpu_limit'] = timeout * 100; // TODO make this reasonable
        data['problem'] = problem;
        send_control(data,callback);
    },
    run_remote_prover : function (prover,timeout,problem,callback) {
        data = {};
        data['command'] = 'prove_remote';
        data['prover_name'] = prover.name
        data['prover_dialects'] = prover.dialects
        data['prover_command'] = prover.prover_command;
        data['wc_limit'] = timeout;
        data['cpu_limit'] = timeout * 100; // TODO make this reasonable
        data['problem'] = problem;
        send_control(data,callback);
    },
    export_latex : function (problem,mode,callback) {
        data = {};
        data['command'] = 'export_latex';
        data['problem'] = problem;
        data['mode'] = mode;
        send_control(data,callback);
    },
    /**
     * Starts the embed command on the server and returns an shallow semantical embedding for the problem
     *
     * @param {string}      semantics    semantics in TPTP logic specification format.
     *                                   prepended to the problem, replaces semantics already in the problem (TODO check if this is true),
     *                                   null if no semantics should be prepended (assumes semantics is included in the problem)
     *                                   already in the problem will be used)
     * @param {number}      timeout      wallclock time, may be subject to change
     * @param {string}      problem      problem in THF
     * @returns {string}                 embedded problem in THF
     */
    embed : function (semantics, timeout, problem, parameters, callback) {
        data = {};
        data['command'] = 'embed';
        data['semantics'] = semantics;
        data['wc_limit'] = timeout;
        data['cpu_limit'] = timeout * 100; // TODO make this reasonable
        data['problem'] = problem;
        data['parameters'] = parameters;
        send_control(data,callback);
    }
}

