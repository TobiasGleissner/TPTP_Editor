import subprocess
import pathlib
import tempfile
import os
from django.db import models
from django.conf import settings
from tptp_tools import system_on_tptp
from tptp_tools import tptp_to_latex

class OutputNotInterpretable(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return repr(self.msg)

class ExternalTools(models.Model):

    #########################
    # here come some settings
    #########################

    #dir_root = pathlib.Path(settings.BASE_DIR).parent
    bin_treelimitedrun = settings.CUSTOM['treelimitedrun_binary']
    bin_embed = settings.CUSTOM['embedding_binary']

    ################################################################################################
    # here come the external tool wrappers that take a dictionary with data received from the client
    ################################################################################################


    @staticmethod
    def run_predefined_local_prover(received_data):
        """ Starts a local prover and returns its result

        Parameters
        ----------
        received_data: dict
            A dictionary that must contain the following keys:
            * prover_command                            string, binary of the prover
            * prover_parameters                         string, arguments for the command line, %d %s are placeholders for the timeout and filename
            * problem                                   string, logical problem in TPTP syntax
            * wc_limit
            * cpu_limit

        Returns
        -------
        dict
            A dictionary containing the following keys:
            * status                                    indicator of success, values: ok TODO
            * szs_status                                string, from szs ontology (Theorem, CounterSatisfiable, ...)
            * wc                                        float, wall clock time in milli seconds
            * cpu                                       float, cpu time in milli seconds
            * plain_prover_output                       string, plain console output of the prover
            * return_code                               return value of the prover binary
        """
        # get data
        try:
            prover_name = received_data['prover_name']
            wc_limit = received_data['wc_limit']
            cpu_limit = received_data['cpu_limit']
            problem = received_data['problem']
        except KeyError as e:
            send_data = {}
            send_data['status'] = 'error_keyerror'
            send_data['raw'] = "prover not configured correctly or insufficient parameters: " + str(e)
            return send_data

        # check if this is a custom prover or a predefined prover
        entries = list(filter(lambda e: e['name'] == prover_name, settings.CUSTOM['predefined_local_provers']))
        if len(entries) == 0:
            send_data = {}
            send_data['status'] = 'error_not_allowed'
            send_data['raw'] = "not allowed"
            return send_data
        # get predefined arguments
        entry = entries[0]
        prover_dialects = entry['dialects']
        prover_command = entry['command']
        prover_parameters = entry['parameters']
        return ExternalTools.run_local_prover_helper(prover_name, prover_command, prover_parameters, problem, wc_limit, cpu_limit)

    @staticmethod
    def run_local_prover(received_data):
        """ Starts a local prover and returns its result

        Parameters
        ----------
        received_data: dict
            A dictionary that must contain the following keys:
            * prover_command                            string, binary of the prover
            * prover_parameters                         string, arguments for the command line, %d %s are placeholders for the timeout and filename
            * problem                                   string, logical problem in TPTP syntax
            * wc_limit
            * cpu_limit

        Returns
        -------
        dict
            A dictionary containing the following keys:
            * status                                    indicator of success, values: ok TODO
            * szs_status                                string, from szs ontology (Theorem, CounterSatisfiable, ...)
            * wc                                        float, wall clock time in milli seconds
            * cpu                                       float, cpu time in milli seconds
            * plain_prover_output                       string, plain console output of the prover
            * return_code                               return value of the prover binary
        """
        # get data
        try:
            prover_name = received_data['prover_name']
            prover_dialects = received_data['prover_dialects']
            wc_limit = received_data['wc_limit']
            cpu_limit = received_data['cpu_limit']
            prover_command = received_data['prover_command']
            prover_parameters = received_data['prover_parameters']
            problem = received_data['problem']
        except KeyError as e:
            send_data = {}
            send_data['status'] = 'error_keyerror'
            send_data['raw'] = "prover not configured correctly or insufficient parameters: " + str(e)
            return send_data

        # check if custom provers are allowed
        if not settings.CUSTOM['allow_custom_local_provers']:
            send_data = {}
            send_data['status'] = 'error_local_prover_not_allowed'
            send_data['raw'] = "custom local provers are not allowed"
            return send_data

        return ExternalTools.run_local_prover_helper(prover_name, prover_command, prover_parameters, problem, wc_limit, cpu_limit)

    @staticmethod
    def run_local_prover_helper(prover_name, prover_command, prover_parameters, problem, wc_limit, cpu_limit):
        # create temp file
        filename = ExternalTools.create_temp_file(problem)

        #  execute prover command with tree limited run on temp file
        cmd = prover_command + " " + prover_parameters.replace("%s",filename).replace("%d",str(wc_limit))
        stdout,stderr,returncode = ExternalTools.execute_treelimitedrun(cmd, wc_limit, cpu_limit)

        # delete temp file
        try:
            os.remove(filename)
        except:
            pass

        # extract information from prover result
        str_stdout = stdout.decode('utf-8')
        str_err = stderr.decode('utf-8')
        str_returncode = str(returncode)
        try:
            szs_status = ExternalTools.parse_szs_status(str_stdout)
            wc = ExternalTools.parse_wc(str_stdout)
            cpu = ExternalTools.parse_cpu(str_stdout)
        except OutputNotInterpretable:
            send_data = {}
            send_data['status'] = 'error_output_not_interpretable'
            send_data['raw'] = str_stdout + "\n" + str_err
            send_data['return_code'] = str_returncode
            return send_data

        # success data
        send_data = {}
        send_data['status'] = 'ok'
        send_data['szs_status'] = szs_status
        send_data['wc'] = wc
        send_data['cpu'] = cpu
        send_data['raw'] = str_stdout + "\n" + str_err
        send_data['return_code'] = str_returncode
        send_data['prover_name'] = prover_name
        #send_data['prover_dialects'] = prover_dialects
        #send_data['prover_command'] = prover_command
        #send_data['prover_parameters'] = prover_parameters
        #send_data['wc_limit'] = wc_limit
        #send_data['cpu_limit'] = cpu_limit
        #send_data['problem'] = problem
        return send_data

    @staticmethod
    def get_remote_provers(received_data):
        solvers = system_on_tptp.getSolvers()
        send_data = {}
        send_data['status'] = 'ok'
        send_data['remote_provers'] = solvers
        return send_data

    @staticmethod
    def run_remote_prover(received_data):
        """ Starts a remote prover and returns its result

                Parameters
                ----------
                received_data: dict
                    A dictionary that must contain the following keys:
                    * prover_command                            string, binary of the prover
                    * prover_parameters                         string, arguments for the command line, %d %s are placeholders for the timeout and filename
                    * problem                                   string, logical problem in TPTP syntax
                    * wc_limit
                    * cpu_limit

                Returns
                -------
                dict
                    A dictionary containing the following keys:
                    * status                                    indicator of success, values: ok TODO
                    * szs_status                                string, from szs ontology (Theorem, CounterSatisfiable, ...)
                    * wc                                        float, wall clock time in milli seconds
                    * cpu                                       float, cpu time in milli seconds
                    * console                                   string, plain console output of the prover
                    * return_code                               return value of the prover binary
                """
        # get data
        try:
            prover_name = received_data['prover_name']
            prover_dialects = received_data['prover_dialects']
            wc_limit = received_data['wc_limit']
            cpu_limit = received_data['cpu_limit']
            prover_command = received_data['prover_command']
            #prover_parameters = received_data['prover_parameters'] included in prover_command for remote provers
            problem = received_data['problem']
        except KeyError:
            send_data = {}
            send_data['status'] = 'error_keyerror'
            send_data['plain_prover_output'] = "prover not configured correctly"
            return send_data
        # send request to systemOnTPTP
        try:
            ret = system_on_tptp.request(prover_name,prover_command,problem,wc_limit)
        except Exception as e:
            send_data = {}
            send_data['status'] = 'error_systemontptp'
            send_data['raw'] = str(e)
            return send_data
        send_data = {}
        send_data['status'] = 'ok'
        send_data['szs_status'] = ret['szs_status']
        send_data['cpu'] = ret['cpu']
        send_data['wc'] = ret['wc']
        send_data['console'] = ret['raw']
        send_data['prover_name'] = prover_name
        send_data['prover_dialects'] = prover_dialects
        send_data['prover_command'] = prover_command
        send_data['wc_limit'] = wc_limit
        send_data['cpu_limit'] = cpu_limit
        send_data['problem'] = problem
        return send_data

    @staticmethod
    def export_latex(received_data):
        # TODO maybe add some timeout here?
        mode = received_data['mode']
        problem = received_data['problem']
        latex = None
        if mode == 'document':
            latex = tptp_to_latex.create_latex_file(problem,ExternalTools.get_default_export_latex_configuration())
        elif mode == 'list':
            #TODO
            pass
        else:
            #TODO error
            pass
        send_data = {}
        send_data['status'] = 'ok'
        send_data['mode'] = mode
        send_data['problem'] = problem
        send_data['latex'] = latex
        return send_data

    @staticmethod
    def embed(received_data):
        """ Starts a remote prover and returns its result

                Parameters
                ----------
                received_data: dict
                    A dictionary that must contain the following keys:
                    * semantics                                 semantics in TPTP logic specification format, replaces
                                                                semantics already existing in the problem. If None problem
                                                                is assumed to already has semantics specified within
                    * problem                                   string, logical problem in TPTP syntax
                    * parameters                                a list of embedding parameter strings, might be None
                    * wc_limit
                    * cpu_limit

                Returns
                -------
                dict
                    A dictionary containing the following keys:
                    * status                                    indicator of success, values: ok TODO
                    * wc                                        float, wall clock time in milli seconds
                    * cpu                                       float, cpu time in milli seconds
                    * console                                   string, plain console output of the embedding software
                    * embedded_problem                          embedded problem in TPTP syntax
                    * return_code                               return value of the embedding binary
                """
        # get data
        try:
            semantics = received_data['semantics']
            wc_limit = received_data['wc_limit']
            cpu_limit = received_data['cpu_limit']
            parameters = received_data['parameters']
            problem = received_data['problem']
        except KeyError as e:
            send_data = {}
            send_data['status'] = 'error_keyerror'
            send_data['plain_prover_output'] = "prover not configured correctly"
            return send_data

        # check validity of parameters
        if not parameters == None:
            allowed_parameters = [
                "semantical_modality_axiomatization",
                "syntactical_modality_axiomatization"
            ]
            params = list(filter(lambda p: len(p) != 0, map(lambda p: p.strip(), parameters.split(','))))
            for p in params:
                if p not in allowed_parameters:
                    send_data = {}
                    send_data['status'] = 'error_not_allowed'
                    send_data['plain_prover_output'] = "parameters invalid"
                    return send_data
        else:
            params = []

        # validate semantics
        # TODO
        if semantics == None:
            filecontent = problem
        else:
            filecontent =  semantics + "\n" + problem

        # create temp files
        filename_original = ExternalTools.create_temp_file(filecontent) # TODO pass semantics through cli somehow or strip semantics from problem first
        filename_embedded = ExternalTools.create_temp_file("")

        #  execute prover command with tree limited run on temp file
        cmd = str(ExternalTools.bin_embed) + " -i " + filename_original + " -o " + filename_embedded
        if len(params) != 0:
            cmd += " -t " + ",".join(params)
        stdout, stderr, returncode = ExternalTools.execute_treelimitedrun(cmd, wc_limit, cpu_limit)
        str_stdout = stdout.decode('utf-8')
        str_err = stderr.decode('utf-8')
        str_returncode = str(returncode)
        try:
            fd = open(filename_embedded,"r")
            problem_embedded = fd.read()
        except:
            send_data = {}
            send_data['status'] = 'error_output_file_not_readable'
            send_data['plain_prover_output'] = str_stdout + "\n" + str_err
            send_data['return_code'] = str_returncode
            return send_data
        finally:
            try:
                fd.close()
            except:
                pass

        # delete temp files
        try:
            os.remove(filename_original)
        except:
            pass
        try:
            os.remove(filename_embedded)
        except:
            pass

        # extract information from embedding console
        try:
            wc = ExternalTools.parse_wc(str_stdout)
            cpu = ExternalTools.parse_cpu(str_stdout)
        except OutputNotInterpretable:
            send_data = {}
            send_data['status'] = 'error_output_not_interpretable'
            send_data['plain_prover_output'] = str_stdout + "\n" + str_err
            send_data['return_code'] = str_returncode
            return send_data

        # success data
        send_data = {}
        send_data['status'] = 'ok'
        send_data['wc'] = wc
        send_data['cpu'] = cpu
        send_data['console'] = str_stdout + "\n" + str_err
        send_data['return_code'] = str_returncode
        send_data['embedded_problem'] = problem_embedded
        return send_data

    ##############################
    # here come the helper methods
    ##############################

    @staticmethod
    def parse_cpu(s):
        cpu_start = s.find("FINAL WATCH:") + 12
        cpu_end = s.find("CPU")
        return s[cpu_start:cpu_end].strip()

    @staticmethod
    def parse_wc(s):
        wc_start = s.find("CPU") + 3
        wc_end = s.find("WC")
        return s[wc_start:wc_end].strip()

    @staticmethod
    def parse_szs_status(s):
        status_start = s.find("SZS status")
        if status_start == -1:
            raise OutputNotInterpretable("status_start == -1")
        status_start += 10
        s = s[status_start:].strip()
        status_end = s.find(" ")
        return s[:status_end].strip()

    @staticmethod
    def execute_treelimitedrun(cmd,wc_limit,cpu_limit):
        newcmd = str(ExternalTools.bin_treelimitedrun) + " " + str(cpu_limit) + " " + str(wc_limit) + " " + cmd
        process = subprocess.Popen(newcmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        process.wait()
        stdout, stderr = process.communicate()
        return stdout, stderr, process.returncode

    @staticmethod
    def create_temp_file(content):
        fd, filename = tempfile.mkstemp()
        os.write(fd,content.encode('utf-8'))
        os.close(fd)
        return filename

    @staticmethod
    def get_default_export_latex_configuration():
        conf = """
{
  "replacementSymbols": {
    "!": "\\\\forall",
    "Forall": "forall",
    "?": "\\\\exists",
    "Exists": "\\\\exists",
    "<=>": "\\\\iff",
    "Iff": "\\\\iff",
    "=>": "\\\\Longrightarrow",
    "Impl": "\\\\Longrightarrow",
    "<=": "\\\\Longleftarrow",
    "If": "\\\\Longleftarrow",
    "<~>": "\\\\centernot\\\\Longleftrightarrow",
    "Niff": "\\\\centernot\\\\Longleftrightarrow",
    "~|": "\\\\downarrow",
    "Nor": "\\\\downarrow",
    "~&": "\\\\uparrow",
    "Nand": "\\\\uparrow",
    "|": "\\\\lor",
    "Or": "\\\\lor",
    "&": "\\\\land",
    "And": "\\\\land",
    "~": "\\\\lnot",
    "Not": "\\\\lnot",
    "!=": "\\\\neq",
    "_": "\\\\_",
    "[": "",
    "]": "",
    "$oType": "\\\\sigma",
    "$o": "\\\\sigma",
    "$iType": "\\\\iota",
    "$i": "\\\\iota",
    "$tType": "{\\\\$tType}",
    "$real": "\\\\mathbb{R}",
    "rat": "\\\\mathbb{Q}",
    "$int": "\\\\mathbb{N}",
    "$true": "\\\\top",
    "$false": "\\\\bot",
    "^": "\\\\lambda",
    "@": "",
    "fof(": "",
    ").": "",
    "thf(": "",
    ",": ""
  },
  "formulas":["thf_formula","fof_formula"],
  "customParsing":{"thf_variable_list":{
    "customTex":" {variable}_{{{atomic_defined_word}{atomic_word}}}",
    "rules":["variable","atomic_defined_word","atomic_word"]
  }},
"rulesStyling":{
  "functor":"\\\\tptpred",
  "fof_formula":"\\\\tptpblue"
},
  "deleteRules":["name","formula_role"],
  "latexPreamble":["\\\\newcommand\\\\tptpfontsize{\\\\footnotesize}","\\\\newcommand\\\\tptpred[1]{\\\\textcolor{red}{#1}}",
    "\\\\newcommand\\\\tptpblue[1]{\\\\textcolor{blue}{#1}}","\\\\newcommand\\\\tptpgreen[1]{\\\\textcolor{green}{#1}}",
    "\\\\newcommand\\\\tptpyellow[1]{\\\\textcolor{yellow}{#1}}"]


}
"""

        return conf