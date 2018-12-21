var importscripts_ace_worker_worker = "/static/editor_component/ace-worker/worker.js";
var importscripts_ace_builds_src_noconflict_ace = "/static/editor_component/ace-builds-src-noconflict/ace.js";
var importscripts_ace_worker_mirror = "/static/editor_component/ace-worker/mirror.js";
var importscripts_require = "/static/editor_component/require.js";

importScripts(importscripts_ace_worker_worker);
importScripts(importscripts_ace_builds_src_noconflict_ace);
importScripts(importscripts_ace_worker_mirror);
//importScripts(importscripts_lexer);
//importScripts(importscripts_parser);


ace.define('ace/worker/tptp-worker',
           ["require", "exports", "module", "ace/lib/oop", "ace/worker/mirror"],
           function (require, exports, module) {
             "use strict";

             var oop = require("ace/lib/oop");
             var Mirror = require("ace/worker/mirror").Mirror;

             var TPTPWorker = function (sender) {
               Mirror.call(this, sender);
               this.setTimeout(200);
               this.$dialect = null;
             };

             oop.inherits(TPTPWorker, Mirror);
             // load nodejs compatible require
             var ace_require = require;
             window.require = undefined; // prevent error: "Honey: 'require' already defined in
                                         // global scope"
             var Honey = {'requirePath': ['..']}; // walk up to js folder, see Honey docs
             importScripts(importscripts_require);
             var antlr4_require = window.require;
             window.require = require = ace_require;

             // load antlr4 and myLanguage
             var antlr4, TptpLexer, TptpParser;
             try {
               window.require = antlr4_require;
               antlr4 = antlr4_require('antlr4/index');
               TptpLexer = antlr4_require('./parser/tptp_v7_0_0_0Lexer.js').tptp_v7_0_0_0Lexer;
               TptpParser = antlr4_require('./parser/tptp_v7_0_0_0Parser.js').tptp_v7_0_0_0Parser;
             } finally {
               window.require = ace_require;
             }

             // class for gathering errors and posting them to ACE editor
             var AnnotatingErrorListener = function (annotations) {
               antlr4.error.ErrorListener.call(this);
               this.annotations = annotations;
               return this;
             };

             AnnotatingErrorListener.prototype =
               Object.create(antlr4.error.ErrorListener.prototype);
             AnnotatingErrorListener.prototype.constructor = AnnotatingErrorListener;

             AnnotatingErrorListener.prototype.syntaxError =
               function (recognizer, offendingSymbol, line, column, msg, e) {
                 this.annotations.push({
                                         row: line - 1,
                                         column: column,
                                         text: msg,
                                         type: "error"
                                       });
               };

             var validate = function (input) {
               var stream = new antlr4.InputStream(input);
               var lexer = new TptpLexer(stream);
               var tokens = new antlr4.CommonTokenStream(lexer);
               var parser = new TptpParser(tokens);
               var annotations = [];
               var listener = new AnnotatingErrorListener(annotations);
               parser.removeErrorListeners();
               parser.addErrorListener(listener);
               parser.tptp_file();
               return annotations;
             };

             (function () {

               this.onUpdate = function () {
                 var value = this.doc.getValue();
                 var annotations = validate(value);
                 this.sender.emit("annotate", annotations);
               };

             }).call(TPTPWorker.prototype);

             exports.TPTPWorker = TPTPWorker;
           });
