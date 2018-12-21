ace.define('ace/mode/mode-tptp',
           ["require",
            "exports",
            "module",
            "ace/lib/oop",
            "ace/mode/text",
            "ace/mode/text_highlight_rules",
            "ace/worker/worker_client"],

           function (require, exports, module) {
             var oop = require("ace/lib/oop");
             var TextMode = require("ace/mode/text").Mode;
             var TextHighlightRules = require("ace/mode/text_highlight_rules").TextHighlightRules;

             var TptpHighlightRules = function () {
/*
               var keywords = (
                 "select|insert|update|delete|from|where|and|or|group|by|order|limit|offset|having|as|case|"
                 +
                 "list|show|print|"
                 +
                 "when|else|end|type|left|right|join|on|outer|desc|asc|union|create|table|stream|primary|key|if|"
                 +
                 "foreign|not|references|default|null|inner|cross|natural|database|drop|grant"
               );

               var builtinConstants = (
                 "true|false"
               );

               var builtinFunctions = (
                 "avg|count|first|last|max|min|sum|ucase|lcase|mid|len|round|rank|now|format|"
                 +
                 "coalesce|ifnull|isnull|nvl"
               );

               var dataTypes = (
                 "int|numeric|decimal|date|varchar|char|bigint|float|double|bit|binary|text|set|timestamp|"
                 +
                 "money|real|number|integer"
               );
*/
               var keywords = (
                 "axiom|hypothesis|definition|assumption|lemma|theorem|corollary|conjecture|negated_conjecture|plain|type|fi_domain|fi_functors|fi_predicates|unknown|$constants|$quantification|$consequence|$modalities|$rigid|$flexible|$constant|$varying|$cumulative|$decreasing|$local|$global|$modal_system_K|$modal_system_T|$modal_system_D|$modal_axiom_K|$modal_axiom_T|$modal_axiom_B|$modal_axiom_D|$oType|$o|$iType|$i|$tType|$real|$rat|$int|$true|$false|$distinct|$less|$lesseq|$greater|$greatereq|$is_int|$is_rat|$box_P|$box_i|$box_int|$box|$dia_P|$dia_i|$dia_int|$dia|$uminus|$sum|$difference|$product|$quotient|$quotient_e|$quotient_t|$quotient_f|$remainder_e|$remainder_t|$remainder_f|$floor|$ceiling|$truncate|$round|$to_int|$to_rat|$to_real|unknown|definition|axiom_of_choice|tautology|assumption|equality|ac|suc|unp|sap|esa|sat|fsa|thm|eqv|tac|wec|eth|tau|wtc|wth|cax|sca|tca|wca|cup|csp|ecs|csa|cth|ceq|unc|wcc|ect|fun|uns|wuc|wct|scc|uca|noc"
	       );
               var builtinFunctions = (
                 "tpi|thf|tff|tcf|fof|cnf|$ite|$let|$ite|$let|inference|introduced|file|theory|creator|description|iquote|status|assumptions|refutation|new_symbols|include|bind|$thf|$tff|$fof|$cnf|$fot"
	       );
               var dataTypes = ("");
               var builtinConstants = ("");
               var keywordMapper = this.createKeywordMapper({
                                                              "support.function": builtinFunctions,
                                                              "keyword": keywords,
                                                              "constant.language": builtinConstants,
                                                              "storage.type": dataTypes
                                                            }, "identifier", true);

               this.$rules = {
                 "start": [{
                   token: "comment",
                   regex: "%.*$"
                 }, {
                   token: "comment",
                   start: "/\\*",
                   end: "\\*/"
                 }, {
                   token: "string",           // " string
                   regex: '".*?"'
                 }, {
                   token: "string",           // ' string
                   regex: "'.*?'"
                 }, {
                   token: "string",           // ` string (apache drill)
                   regex: "`.*?`"
                 }, {
                   token: "constant.numeric", // float
                   regex: "[+-]?\\d+(?:(?:\\.\\d*)?(?:[eE][+-]?\\d+)?)?\\b"
                 }, {
                   token: keywordMapper,
                   regex: "[a-zA-Z_$][a-zA-Z0-9_$]*\\b"
                 }, {
                   token: "keyword.operator",
                   regex: "\\+|\\-|\\/|\\/\\/|%|<@>|@>|<@|&|\\^|~|<|>|<=|=>|==|!=|<>|="
                 }, {
                   token: "paren.lparen",
                   regex: "[\\(]"
                 }, {
                   token: "paren.rparen",
                   regex: "[\\)]"
                 }, {
                   token: "text",
                   regex: "\\s+"
                 }]
               };
               this.normalizeRules();
             };
             oop.inherits(TptpHighlightRules, TextHighlightRules);

             var ModeTPTP = function () {
               this.HighlightRules = TptpHighlightRules;
             };
             oop.inherits(ModeTPTP, TextMode);

             (function () {

               this.$id = "ace/mode/mode-tptp";
               var WorkerClient = require("ace/worker/worker_client").WorkerClient;
                //importScripts(self.importscripts_ace_worker_worker);
                //importScripts(self.importscripts_ace_builds_src_noconflict_ace);
                //importScripts(self.importscripts_ace_worker_mirror);
                 //  var WorkerClient = function(topLevelNamespaces, mod, classname, workerUrl) {
               this.createWorker = function (session) {
                 this.$worker =
                   new WorkerClient(["ace"], "ace/worker/tptp-worker", "TPTPWorker",
                                    url_tptp_worker);
                 this.$worker.attachToDocument(session.getDocument());

                 this.$worker.on("errors", function (e) {
                   session.setAnnotations(e.data);
                 });

                 this.$worker.on("annotate", function (e) {
                   session.setAnnotations(e.data);
                 });

                 this.$worker.on("terminate", function () {
                   session.clearAnnotations();
                 });

                 return this.$worker;

               };

             }).call(ModeTPTP.prototype);

             exports.Mode = ModeTPTP;
           });
