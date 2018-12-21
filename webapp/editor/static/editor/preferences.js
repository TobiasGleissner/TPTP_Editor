// ==================================================================================================
// === preferences modal
// ==================================================================================================

var preferences = {

    init : function () {
        preferences.tree_init();
        preferences.local_prover.init();
        preferences.local_prover_disabled.init();
        preferences.embedding.init();
        preferences.remote_prover.init();
    },
    preferences_modified : null, // preferences loaded, shown, modified and stored in the preferences modal
    preferences : null, // the actual preferences used in all remaining functions - is updated once OK/Apply in the preferences modal is pressend
    predefined : null, // predefined preferences (provers, embeddings, latex export configurations, ...)

    on_modal_open : function () {
        preferences.preferences_modified = JSON.parse(JSON.stringify(preferences.preferences));
    },
    on_modal_close : function () {
        preferences.preferences_modified = null;
    },

    modal_freeze : function () {
        // TODO make preferences window unmodifiable
    },

    modal_unfreeze : function () {
        // TODO make preferences window modifiable
    },

    button_ok : function () {
        this.modal_freeze()
        this.preferences = this.preferences_modified;
        toolbar.prover.render_prover_select();
        toolbar.prover.render_embedding_select();
        this.store(function(json_response){
            modals.preferences.close();
            preferences.modal_unfreeze();
        });
    },

    button_apply : function () {
        this.modal_freeze();
        this.preferences = this.preferences_modified;
        this.preferences_modified = JSON.parse(JSON.stringify(this.preferences));
        toolbar.prover.render_prover_select();
        toolbar.prover.render_embedding_select();
        this.store(function(json_response){
            preferences.modal_unfreeze();
        });
    },

    button_cancel : function () {
        this.modal_freeze();
        modals.preferences.close();
        this.modal_unfreeze();
    },

    load : function (callback) {
        send_control({'command': 'load_preferences'},
            function (json_response) {
                //console.log(json_response['preferences']);
                preferences.preferences = JSON.parse(json_response['preferences']);
                preferences.predefined = JSON.parse(json_response['predefined']);
                //console.log(preferences);
                if (callback != null) {
                    callback(json_response);
                }
            }
        );
    },

    store : function (callback) {
        send_control({
            'command': 'store_preferences',
            'preferences': JSON.stringify(preferences.preferences)},
            function (json_response) {
                if (callback != null) {
                    callback(json_response);
                }
            }
        );
    },

    // =================================================
    // === common inner workings (not pereference content specific
    // === tree creation, display preference content
    // =================================================


    tree_init : function () {
        $("#preferences_tree").fancytree({
            /*
            source: [
                {
                    preferences_content_identifier: "provers", title: "Provers", folder: true, children: [
                        {preferences_content_identifier: "local_prover", title: "Local Provers"}
                    ]
                }
            ],*/
            source: [
                {preferences_content_identifier: "local_prover", title: "Local Provers"},
                {preferences_content_identifier: "embedding", title: "Embedding"}
            ],
            icon: function (event, data) {
                return false;
            },
            click: function (event, data) {
                //console.log(data.node.title);
                //console.log(data.node.data.preferences_content_identifier);
                var preferences_content_identifier = data.node.data.preferences_content_identifier;
                if (!preferences.predefined['allow_custom_local_provers'] && data.node.data.preferences_content_identifier == "local_prover") {
                    preferences_content_identifier = 'local_prover_disabled'
                }
                preferences.display_section(preferences_content_identifier);
            }
        });
        // Note: Loading and initialization may be asynchronous, so the nodes may not be accessible yet.
    },

    display_section : function (preferences_content_identifier) {
        //console.log("ID",preferences_content_identifier);
        // prepare new content
        this[preferences_content_identifier].display();
        // hide old content, show new content
        dom_id = "#preferences_" + preferences_content_identifier;
        //console.log($(".preferences_content_selected"));
        var old_content_div = $(".preferences_content_selected")[0];
        //console.log("OLD", old_content_div);
        old_content_div.classList.remove("preferences_content_selected");
        old_content_div.classList.add("preferences_content_hidden");
        new_content_div = $(dom_id)[0];
        //console.log("NEW", new_content_div);
        //console.log("ID", dom_id);
        new_content_div.classList.remove("preferences_content_hidden");
        new_content_div.classList.add("preferences_content_selected");
    },

    local_prover_disabled : {
        init : function () {

        },
        display : function () {

        }
    },

    local_prover : {
        init : function () {
            $("#preferences_local_prover_configuration")[0].style.visibility = "hidden"; // hide configuration
        },
        display : function () {
            // fill list of provers
            this.render_prover_list();
        },
        render_prover_list : function () {
            // remove all prover entries
            var prover_list_node = $("#preferences_local_prover_sidekick_selection_list")[0];
            while (prover_list_node.firstChild) {
                prover_list_node.removeChild(prover_list_node.firstChild);
            }
            // populate prover entries
            for (i = 0; i < preferences.preferences_modified.local_prover.length; i++) {
                var prover = preferences.preferences_modified.local_prover[i];
                option_node = document.createElement("option");
                option_node.innerText = prover.name;
                option_node.setAttribute("index",i);
                option_node.addEventListener("click", function (event){
                    preferences.local_prover.render_configuration(this.getAttribute("index"));
                });
                $("#preferences_local_prover_sidekick_selection_list").append(option_node);
            }
        },
        render_configuration : function (index) {
            if (index == -1) {
                $("#preferences_local_prover_configuration")[0].style.visibility = "hidden"; // hide configuration
            } else if (index >= preferences.preferences_modified.local_prover.length) {
                console.log("ERROR", "selected index too big"); // this should not happen, for debugging only
            } else {
                $("#preferences_local_prover_configuration")[0].style.visibility = "visible"; // show configuration
                var prover = preferences.preferences_modified.local_prover[index];
                // insert name
                $("#preferences_local_prover_name").val(prover.name);
                // insert command
                $("#preferences_local_prover_command").val(prover.command);
                // insert parameters
                $("#preferences_local_prover_parameters").val(prover.parameters);
                // insert dialects
                var dialect_list_node = $("#preferences_local_prover_configuration_dialect_list")[0];
                for (j = 0; j < dialect_list_node.children.length; j++) {
                    var dialect_node = dialect_list_node.children.item(j);
                    if (prover.dialects.includes(dialect_node.innerHTML)) {
                        dialect_node.classList.add("multi_switch_selected");
                    } else {
                        dialect_node.classList.remove("multi_switch_selected");
                   }
                }
            }
        },
        get_selected_prover_index : function () {
            var prover_list_node = $("#preferences_local_prover_sidekick_selection_list")[0];
            return prover_list_node.selectedIndex;
        },
        contains_prover : function (name) {
            for (i = 0; i < preferences.preferences_modified.local_prover.length; i++) {
                var prover = preferences.preferences_modified.local_prover[i];
                if (name == prover.name) {
                    return true;
                }
            }
            return false;
        },
        select : function (index) { // only marks a selection but does not render configuration
            if (index == -1) {
                $("#preferences_local_prover_configuration")[0].style.visibility = "hidden"; // hide configuration
            } else if (index >= preferences.preferences_modified.local_prover.length) {
                console.log("ERROR", "selected index too big"); // this should not happen, for debugging only
            } else {
                var prover_list_node = $("#preferences_local_prover_sidekick_selection_list")[0];
                prover_list_node.children[index].setAttribute("selected",true);
            }
        },
        add : function () {
            var new_name = "Unnamed";
            var i = 1;
            while (this.contains_prover(new_name)) {
                new_name = "Unnamed_" + i;
                i++;
            }
            preferences.preferences_modified.local_prover.push({
                name:new_name,
                command:"",
                parameters:"",
                dialects:[]
            });
            this.render_prover_list();
            this.render_configuration(preferences.preferences_modified.local_prover.length-1);
            this.select(preferences.preferences_modified.local_prover.length-1);
        },
        remove : function () {
            var index = this.get_selected_prover_index();
            if (index == -1) {
                // TODO indicate nothing was selected
            } else {
                preferences.preferences_modified.local_prover.splice(index, 1);
                this.render_prover_list();
            }
            this.render_configuration(-1);
            this.select(-1);
        },
        movedown : function () {
            var index = this.get_selected_prover_index();
            if (index == -1) {
                // TODO indicate nothing was selected
            } else if (index >= preferences.preferences_modified.local_prover.length - 1) {
                // TODO indicate index too high
            } else {
                temp_prover = preferences.preferences_modified.local_prover[index+1];
                preferences.preferences_modified.local_prover[index+1] = preferences.preferences_modified.local_prover[index];
                preferences.preferences_modified.local_prover[index] = temp_prover;
                this.render_prover_list();
                //this.render_configuration(index+1);
                this.select(index+1);
            }
        },
        moveup : function () {
            var index = this.get_selected_prover_index();
            if (index == -1) {
                // TODO indicate nothing was selected
            } else if (index == 0) {
                // TODO indicate index too small
            } else {
                temp_prover = preferences.preferences_modified.local_prover[index-1];
                preferences.preferences_modified.local_prover[index-1] = preferences.preferences_modified.local_prover[index];
                preferences.preferences_modified.local_prover[index] = temp_prover;
                this.render_prover_list();
                //this.render_configuration(index-1);
                this.select(index-1);
            }
        },
        on_name_change : function (event) {
            var newname = $("#preferences_local_prover_name").val();
            var index = preferences.local_prover.get_selected_prover_index();
            var prover = preferences.preferences_modified.local_prover[index];
            if (preferences.local_prover.contains_prover(newname)) {
                // TODO indicate duplicate name
                console.log("duplicate name");
            } else {
                prover.name = newname;
                preferences.local_prover.render_prover_list();
                preferences.local_prover.select(index); // prover list looses selection once the list is rendered
            }
        },
        on_cmd_change : function (event) {
            var newcmd = $("#preferences_local_prover_command").val();
            var index = preferences.local_prover.get_selected_prover_index();
            var prover = preferences.preferences_modified.local_prover[index];
            prover.command = newcmd;
            preferences.local_prover.select(index);
        },
        on_params_change : function (event) {
            var newparams = $("#preferences_local_prover_parameters").val();
            var index = preferences.local_prover.get_selected_prover_index();
            var prover = preferences.preferences_modified.local_prover[index];
            prover.parameters = newparams;
            preferences.local_prover.select(index);
        },
        on_prover_list_key : function (event) {
            if (event.keyCode == 38 || event.keyCode == 40) {
                var index = preferences.local_prover.get_selected_prover_index();
                preferences.local_prover.render_configuration(index);
                //preferences.local_prover.select(index);
            } else {
                // do nothing
            }
        },
        on_dialect_click : function (event) {
            var index = preferences.local_prover.get_selected_prover_index();
            var prover = preferences.preferences_modified.local_prover[index];
            var dialect = event.target.innerHTML;
            if (prover.dialects.indexOf(dialect) != -1) {
                prover.dialects.splice(prover.dialects.indexOf(dialect),1);
            } else {
                prover.dialects.push(dialect);
            }
            preferences.local_prover.render_configuration(index);
            //preferences.local_prover.select(index);
        }
    },

    embedding : {
        init : function () {
            $("#preferences_embedding_configuration")[0].style.visibility = "hidden"; // hide configuration
        },
        display : function () {
            // fill list of embeddings
            this.render_embedding_list();
        },
        render_embedding_list : function () {
            // remove all embedding entries
            var embedding_list_node = $("#preferences_embedding_sidekick_selection_list")[0];
            while (embedding_list_node.firstChild) {
                embedding_list_node.removeChild(embedding_list_node.firstChild);
            }
            // populate embedding entries
            for (i = 0; i < preferences.preferences_modified.embedding.length; i++) {
                var embedding = preferences.preferences_modified.embedding[i];
                option_node = document.createElement("option");
                option_node.innerText = embedding.name;
                option_node.setAttribute("index",i);
                option_node.addEventListener("click", function (event){
                    preferences.embedding.render_configuration(this.getAttribute("index"));
                });
                $("#preferences_embedding_sidekick_selection_list").append(option_node);
            }
        },
        render_configuration : function (index) {
            if (index == -1) {
                $("#preferences_embedding_configuration")[0].style.visibility = "hidden"; // hide configuration
            } else if (index >= preferences.preferences_modified.embedding.length) {
                console.log("ERROR", "selected index too big"); // this should not happen, for debugging only
            } else {
                $("#preferences_embedding_configuration")[0].style.visibility = "visible"; // show configuration
                var embedding = preferences.preferences_modified.embedding[index];
                // insert name
                $("#preferences_embedding_name").val(embedding.name);
                // insert constants
                $("#preferences_embedding_constants").val(embedding.constants);
                // insert domains
                $("#preferences_embedding_domain").val(embedding.domains);
                // insert consequence
                $("#preferences_embedding_consequence").val(embedding.consequences);
                // insert domains
                $("#preferences_embedding_modalities").val(embedding.modalities);
                // insert parameters
                $("#preferences_embedding_parameters").val(embedding.parameters);
            }
        },
        get_selected_embedding_index : function () {
            var embedding_list_node = $("#preferences_embedding_sidekick_selection_list")[0];
            return embedding_list_node.selectedIndex;
        },
        contains_embedding : function (name) {
            for (i = 0; i < preferences.preferences_modified.embedding.length; i++) {
                var embedding = preferences.preferences_modified.embedding[i];
                if (name == embedding.name) {
                    return true;
                }
            }
            return false;
        },
        select : function (index) { // only marks a selection but does not render configuration
            if (index == -1) {
                $("#preferences_embedding_configuration")[0].style.visibility = "hidden"; // hide configuration
            } else if (index >= preferences.preferences_modified.embedding.length) {
                console.log("ERROR", "selected index too big"); // this should not happen, for debugging only
            } else {
                var embedding_list_node = $("#preferences_embedding_sidekick_selection_list")[0];
                embedding_list_node.children[index].setAttribute("selected",true);
            }
        },
        add : function () {
            var new_name = "Unnamed";
            var i = 1;
            while (this.contains_embedding(new_name)) {
                new_name = "Unnamed_" + i;
                i++;
            }
            preferences.preferences_modified.embedding.push({
                name:new_name,
                constants: "",
                domains:"",
                modalities:"",
                constants:"",
                parameters:""
            });
            this.render_embedding_list();
            this.render_configuration(preferences.preferences_modified.embedding.length-1);
            this.select(preferences.preferences_modified.embedding.length-1);
        },
        remove : function () {
            var index = this.get_selected_embedding_index();
            if (index == -1) {
                // TODO indicate nothing was selected
            } else {
                preferences.preferences_modified.embedding.splice(index, 1);
                this.render_embedding_list();
            }
            this.render_configuration(-1);
            this.select(-1);
        },
        movedown : function () {
            var index = this.get_selected_embedding_index();
            if (index == -1) {
                // TODO indicate nothing was selected
            } else if (index >= preferences.preferences_modified.embedding.length - 1) {
                // TODO indicate index too high
            } else {
                temp_embedding = preferences.preferences_modified.embedding[index+1];
                preferences.preferences_modified.embedding[index+1] = preferences.preferences_modified.embedding[index];
                preferences.preferences_modified.embedding[index] = temp_embedding;
                this.render_embedding_list();
                //this.render_configuration(index+1);
                this.select(index+1);
            }
        },
        moveup : function () {
            var index = this.get_selected_embedding_index();
            if (index == -1) {
                // TODO indicate nothing was selected
            } else if (index == 0) {
                // TODO indicate index too small
            } else {
                temp_embedding = preferences.preferences_modified.embedding[index-1];
                preferences.preferences_modified.embedding[index-1] = preferences.preferences_modified.embedding[index];
                preferences.preferences_modified.embedding[index] = temp_embedding;
                this.render_embedding_list();
                //this.render_configuration(index-1);
                this.select(index-1);
            }
        },
        on_name_change : function (event) {
            var newname = $("#preferences_embedding_name").val();
            var index = preferences.embedding.get_selected_embedding_index();
            var embedding = preferences.preferences_modified.embedding[index];
            if (preferences.embedding.contains_embedding(newname)) {
                // TODO indicate duplicate name
                console.log("duplicate name");
            } else {
                embedding.name = newname;
                preferences.embedding.render_embedding_list();
                preferences.embedding.select(index); // embedding list looses selection once the list is rendered
            }
        },
        on_domain_change : function (event) {
            var newdomain = $("#preferences_embedding_domain").val();
            var index = preferences.embedding.get_selected_embedding_index();
            var embedding = preferences.preferences_modified.embedding[index];
            embedding.domains = newdomain;
            preferences.embedding.select(index);
        },
        on_constants_change : function (event) {
            var newconstants = $("#preferences_embedding_constants").val();
            var index = preferences.embedding.get_selected_embedding_index();
            var embedding = preferences.preferences_modified.embedding[index];
            embedding.constants = newconstants;
            preferences.embedding.select(index);
        },
        on_consequence_change : function (event) {
            var newconsequence = $("#preferences_embedding_consequence").val();
            var index = preferences.embedding.get_selected_embedding_index();
            var embedding = preferences.preferences_modified.embedding[index];
            embedding.consequences = newconsequence;
            preferences.embedding.select(index);
        },
        on_modalities_change : function (event) {
            var newmodalities = $("#preferences_embedding_modalities").val();
            var index = preferences.embedding.get_selected_embedding_index();
            var embedding = preferences.preferences_modified.embedding[index];
            embedding.modalities = newmodalities;
            preferences.embedding.select(index);
        },
        on_parameters_change : function (event) {
            var newparameters = $("#preferences_embedding_parameters").val();
            var index = preferences.embedding.get_selected_embedding_index();
            var embedding = preferences.preferences_modified.embedding[index];
            embedding.parameters = newparameters;
            preferences.embedding.select(index);
        },
        on_embedding_list_key : function (event) {
            if (event.keyCode == 38 || event.keyCode == 40) {
                var index = preferences.embedding.get_selected_embedding_index();
                preferences.embedding.render_configuration(index);
                //preferences.embedding.select(index);
            } else {
                // do nothing
            }
        },
        export : function (event) {
            var embedding_index = preferences.embedding.get_selected_embedding_index();
            console.log(embedding_index);
            var embedding = preferences.preferences_modified.embedding[embedding_index];
            console.log(embedding);
            var semantics = external_tools.create_semantics("mylogic", embedding);
            output.render_semantics(semantics);
        },
        validate_ : function (event) {
            alert("not implemented");
        }
    },

    remote_prover : {
        init : function () {

        },
        display : function () {

        }
    }
}

