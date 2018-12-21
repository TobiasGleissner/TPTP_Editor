import os
import shutil
import pathlib
import subprocess
import sys

# TODO
# follow todos
# create binaries
# targets as classes? how to pass function?

#######################################
### BINARIES
#######################################

bin_git = "git"
bin_python = "python3"
bin_pip = "pip3"
bin_pip_arguments = []
bin_mvn = "mvn"
bin_java = "java"
bin_gcc = "gcc"


#######################################
### MAIN
#######################################

# phases
all_phases = {"compile","build","clone","clean_compile","clean_clone","clean_build"}
compile = False
clone = False
clean_compile = False
clean_clone = False

# targets
target_name_antlr4 = "antlr4"
target_name_tptp_antlr_grammar = "tptp_antlr_grammar"
target_name_honey_require = "honey_require"
target_name_ace_build = "ace_build"
target_name_ace_worker = "ace_worker"
target_name_tptp_tools = "tptp_tools"
target_name_embed_modal = "embed_modal"
target_name_treelimitedrun = "treelimitedrun"
target_name_fancytree = "fancytree"
target_name_webapp = "webapp"

all_targets = [
    target_name_antlr4,
    target_name_tptp_antlr_grammar,
    target_name_honey_require,
    target_name_ace_build,
    target_name_ace_worker,
    target_name_tptp_tools,
    target_name_embed_modal,
    target_name_treelimitedrun,
    target_name_fancytree,
    target_name_webapp
]

# main
if len(sys.argv) < 2:
    print("invalid args: enter a phase")
    sys.exit(1)
cmd = sys.argv[1]
if cmd == "compile":
    compile = True
elif cmd == "clone":
    clone = True
elif cmd == "build": # clone + compile
    clone = True
    compile = True
elif cmd == "clean_compile": # clean compiled parts
    clean_compile = True
elif cmd == "clean_clone": # clean compiled parts
    clean_clone = True
elif cmd == "clean_build": # clean compiled parts and cloned repositories
    clean_clone = True
    clean_compile = True
else:
    print(cmd,"is not a valid phase. possible phases are:"," ".join(all_phases))
    sys.exit(1)
print("phase:",cmd)
selected_targets = set(sys.argv[2:])
for target in selected_targets:
    if target not in all_targets:
        print(target,"is not a valid target")
        print("possible targets are:"," ".join(all_targets))
        sys.exit(1)
if len(selected_targets) == 0:
    selected_targets = all_targets
print("targets:"," ".join(selected_targets))


# functions
def delete_file(path):
    print("TASK","removing old",path," file...")
    try:
        os.remove(str(path))
        print("SUCCESS","removing old", path, " file")
    except OSError:
        print("WARNING","could not remove",path)

def delete_dir(path):
    print("TASK","removing old ",path," dir")
    try:
        shutil.rmtree(str(path))
        print("SUCCESS","removing old ", path, " dir")
    except OSError:
        print("WARNING","could not remove",path)

def create_dir(path):
    print("TASK","creating new ",path," dir...")
    try:
        os.makedirs(str(path))
        print("SUCCESS", "creating new ", path, " dir")
    except OSError:
        print("WARNING",path,"dir already exists, using existing ",path," dir")

def copy_dir(src,dst):
    print("TASK","copying dir",src,"to",dst,"...")
    try:
        shutil.copytree(str(src),str(dst))
        print("SUCCESS","copying dir",src,"to",dst)
    except OSError:
        print("ERROR","copying dir",src,"to",dst)
        print("ERROR","copying dir",src,"to",dst)
        sys.exit(1)

def copy_file(src,dst):
    print("TASK","copying file",src,"to",dst,"...")
    try:
        shutil.copy(str(src),str(dst))
        print("SUCCESS","copying file",src,"to",dst)
    except OSError:
        print("ERROR","copying file",src,"to",dst)
        sys.exit(1)

def cloning(repo, path):
    print("TASK","cloning ",repo,"...")
    process = subprocess.Popen([bin_git, 'clone', repo, str(path)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.wait()
    stdout, stderr = process.communicate()
    print("stdout",stdout)
    print("stderr",stderr)
    print("return_code",process.returncode)
    if process.returncode == 0:
        print("SUCCESS","cloning ",repo,"...")
    else:
        print("ERROR","cloning ",repo,"...")
        sys.exit(1)

# TODO
# this is just an unfinished copy paste
def checkout(repo,path,commit):
    print("TASK;","checking out commit",commit,"of repo",repo,"...")
    process = subprocess.Popen([bin_git, 'checkout', repo, str(path)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.wait()
    stdout, stderr = process.communicate()
    print("stdout",stdout)
    print("stderr",stderr)
    print("return_code",process.returncode)
    if process.returncode == 0:
        print("SUCCESS","checking out commit",commit,"of repo",repo)
    else:
        print("ERROR","checking out commit",commit,"of repo",repo)
        sys.exit(1)

def execute_command(cmd):
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=os.environ.copy())
    process.wait()
    stdout, stderr = process.communicate()
    print("stdout", stdout)
    print("stderr", stderr)
    print("return_code", process.returncode)
    return process.returncode

#######################################
### BASIC DIRECTORIES
#######################################

# root directory
dir_root = pathlib.Path(os.path.dirname(os.path.realpath(__file__)))

# build directory
dir_build = dir_root.joinpath("build")
if clone:
    create_dir(dir_build)

# contrib directory
dir_contrib = dir_root.joinpath("contrib")

# django static directories
dir_django_static = dir_root.joinpath("webapp","editor","static")
dir_django_static_editor_component = dir_django_static.joinpath("editor_component")

# bin directory
dir_bin = dir_root.joinpath("bin")
if compile:
    create_dir(dir_bin)

#######################################
### BINARY CHECKS
#######################################
cmd = [bin_python, "--version"]
return_code = execute_command(cmd)
if return_code != 0:
    print("ERROR", "compiling", target_name_webapp)
    sys.exit(1)

#######################################
### TARGETS
#######################################
#TODO remove .git and .github

# ANTLR runtime for javascript
if target_name_antlr4 in selected_targets:
    print("TARGET",target_name_antlr4)
    repo_antlr4 = "https://github.com/TobiasGleissner/antlr4.git"
    dir_build_antlr4 = dir_build.joinpath(target_name_antlr4)
    if clone:
        cloning(repo_antlr4, dir_build_antlr4)
    src = dir_build_antlr4.joinpath("runtime","JavaScript","src","antlr4")
    dir_django_static_editor_component_antlr4 = dir_django_static_editor_component.joinpath("antlr4")
    if compile:
        copy_dir(src,dir_django_static_editor_component_antlr4)
    if clean_compile:
        delete_dir(dir_django_static_editor_component_antlr4)
    if clean_clone:
        delete_dir(dir_build_antlr4)

# ANTLR TPTP grammar
if target_name_tptp_antlr_grammar in selected_targets:
    print("TARGET",target_name_tptp_antlr_grammar)
    dir_build_tptp_antlr_grammar = dir_build.joinpath(target_name_tptp_antlr_grammar)
    repo_tptp_antlr_grammar = "https://github.com/TobiasGleissner/TPTP-ANTLR4-Grammar.git"
    if clone:
        cloning(repo_tptp_antlr_grammar, dir_build_tptp_antlr_grammar)
    if compile:
        pass #TODO do we need this?
    if clean_compile:
        pass #TODO do we need this?
    if clean_clone:
        delete_dir(dir_build_tptp_antlr_grammar)

# Honey require
if target_name_honey_require in selected_targets:
    print("TARGET", target_name_honey_require)
    if clone:
        pass # nothing to do - comes with contrib
    src = dir_contrib.joinpath("honey_require","require.js")
    dir_django_static_editor_component_honey_require = dir_django_static_editor_component.joinpath("require.js")
    if compile:
        copy_file(src,dir_django_static_editor_component_honey_require)
    if clean_compile:
        delete_file(dir_django_static_editor_component_honey_require)
    if clean_clone:
        pass  # nothing to do - comes with contrib

# ace-build
if target_name_ace_build in selected_targets:
    print("TARGET", target_name_ace_build)
    if clone:
        pass # nothing to do - comes with contrib
    src = dir_contrib.joinpath("ace-builds-src-noconflict")
    dir_django_static_editor_component_ace_build_src_noconflict = dir_django_static_editor_component.joinpath("ace-builds-src-noconflict")
    if compile:
        copy_dir(src,dir_django_static_editor_component_ace_build_src_noconflict)
    if clean_compile:
        delete_dir(dir_django_static_editor_component_ace_build_src_noconflict)
    if clean_clone:
        pass  # nothing to do - comes with contrib

# ace-worker
if target_name_ace_worker in selected_targets:
    print("TARGET", target_name_ace_worker)
    if clone:
        pass # nothing to do - comes with contrib
    src = dir_contrib.joinpath("ace-worker")
    dir_django_static_editor_component_ace_worker = dir_django_static_editor_component.joinpath("ace-worker")
    if compile:
        copy_dir(src,dir_django_static_editor_component_ace_worker)
    if clean_compile:
        delete_dir(dir_django_static_editor_component_ace_worker)
    if clean_clone:
        pass  # nothing to do - comes with contrib

# tptp tools
if target_name_tptp_tools in selected_targets:
    print("TARGET", target_name_tptp_tools)
    dir_build_tptp_tools = dir_build.joinpath(target_name_tptp_tools)
    repo_tptp_tools = "https://github.com/TobiasGleissner/tptp_tools.git"
    if clone:
        cloning(repo_tptp_tools, dir_build_tptp_tools)
    if compile:
        cmd = [bin_pip,"install",str(dir_build_tptp_tools)] + bin_pip_arguments
        return_code = execute_command(cmd)
        if return_code == 0:
            print("SUCCESS","compiling", target_name_tptp_tools)
        else:
            print("ERROR","compiling", target_name_tptp_tools)
            sys.exit(1)
    if clean_compile:
        cmd = [bin_pip,"uninstall","-y",str(dir_build_tptp_tools)] + bin_pip_arguments
        return_code = execute_command(cmd)
        if return_code == 0:
            print("SUCCESS","cleaning", target_name_tptp_tools)
        else:
            print("WARNING","cleaning", target_name_tptp_tools, "did not work.")
    if clean_clone:
        delete_dir(dir_build_tptp_tools)

# embed_modal
if target_name_embed_modal in selected_targets:
    print("TARGET", target_name_embed_modal)
    dir_build_embed_modal = dir_build.joinpath(target_name_embed_modal)
    repo_embed_modal = "https://github.com/leoprover/embed_modal.git"
    dest_binary = dir_bin.joinpath("embedlogic")
    if clone:
        cloning(repo_embed_modal, dir_build_embed_modal)
    if compile:
        print("TASK","compiling", target_name_embed_modal)
        # execute maven
        cmd = [bin_mvn, '-f',str(dir_build_embed_modal),'package']
        return_code = execute_command(cmd)
        if return_code != 0:
            print("ERROR","compiling", target_name_embed_modal, "could not create Maven package")
            sys.exit(1)
        # create executable from jar
        exec_dummy = dir_build_embed_modal.joinpath("util","exec_dummy")
        jar = dir_build_embed_modal.joinpath("embed","target","embed-1.0-SNAPSHOT-shaded.jar")
        try:
            fd_out = open(dest_binary, 'wb')
            fd_exec_dummy = open(exec_dummy, 'rb')
            fd_jar = open(jar, 'rb')
            shutil.copyfileobj(fd_exec_dummy, fd_out)
            shutil.copyfileobj(fd_jar, fd_out)
        except Exception as e:
            try: fd_out.close()
            except: pass
            try: fd_exec_dummy.close()
            except: pass
            try: fd_jar.close()
            except: pass
            print("ERROR", "compiling", target_name_embed_modal, "could not write to binary")
            print(e)
            sys.exit(1)
        try:
            os.chmod(dest_binary, 0o775)
        except Exception as e:
            print("ERROR", "compiling", target_name_embed_modal, "could make binary executable")
            print(e)
            sys.exit(1)

    if clean_compile:
        print("TASK","removing", target_name_embed_modal)
        delete_file(dest_binary)
        process = subprocess.Popen([bin_mvn, '-f',str(dir_build_embed_modal),'clean'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.wait()
        stdout, stderr = process.communicate()
        print("stdout",stdout)
        print("stderr",stderr)
        print("return_code",process.returncode)
        if process.returncode == 0:
            print("SUCCESS","clean_compile", target_name_embed_modal)
        else:
            print("WARNING","clean_compile", target_name_embed_modal)
    if clean_clone:
        delete_dir(dir_build_embed_modal)

# TreeLimitedRun
if target_name_treelimitedrun in selected_targets:
    print("TARGET", target_name_webapp)
    src = dir_contrib.joinpath("TreeLimitedRun", "TreeLimitedRun.c")
    bin_treelimitedrun = dir_bin.joinpath("TreeLimitedRun")
    if clone:
        pass  # nothing to do - comes from webapp
    if compile:
        print("TASK","compiling", target_name_treelimitedrun)
        cmd = [bin_gcc,str(src),"-o",str(bin_treelimitedrun)]
        return_code = execute_command(cmd)
        if return_code == 0:
            print("SUCCESS","compiling", target_name_treelimitedrun)
        else:
            print("ERROR","compiling", target_name_treelimitedrun)
            sys.exit(1)
    if clean_compile:
        delete_file(bin_treelimitedrun)
    if clean_clone:
        pass  # nothing to do - comes from webapp

# fancytree
if target_name_fancytree in selected_targets:
    print("TARGET", target_name_fancytree)
    repo_fancytree = "https://github.com/TobiasGleissner/fancytree.git"
    dir_build_fancytree = dir_build.joinpath(target_name_fancytree)
    dir_django_static_fancytree = dir_django_static.joinpath("fancytree")
    if clone:
        cloning(repo_fancytree,dir_build_fancytree)
    if compile:
        print("TASK","compiling", target_name_fancytree)
        create_dir(dir_django_static_fancytree)
        copy_dir(dir_build_fancytree.joinpath("dist"),dir_django_static_fancytree.joinpath("dist"))
    if clean_compile:
        delete_dir(dir_django_static_fancytree)
    if clean_clone:
        delete_dir(dir_build_fancytree)

# webapp
if target_name_webapp in selected_targets:
    print("TARGET", target_name_webapp)
    dir_webapp = dir_root.joinpath("webapp")
    manage_webapp_file = dir_webapp.joinpath("manage.py")
    sqlite_file = dir_webapp.joinpath("db.sqlite3")
    dir_webapp_migrations = dir_webapp.joinpath("editor","migrations")
    dir_webapp_editor_models_pycache = dir_webapp.joinpath("editor","models","__pycache__")
    dir_webapp_editor_pycache = dir_webapp.joinpath("editor","__pycache__")
    dir_webapp_serverapp_pycache = dir_webapp.joinpath("serverapp","__pycache__")
    if clone:
        pass  # nothing to do - comes from webapp
    if compile:
        cmd = [bin_pip, "install", "django"] # install django package
        return_code = execute_command(cmd)
        if return_code != 0:
            print("ERROR", "compiling", target_name_webapp)
            sys.exit(1)
        cmd = [bin_python, str(manage_webapp_file), "makemigrations","editor"] # django makemigrations for app editor
        return_code = execute_command(cmd)
        if return_code != 0:
            print("ERROR","compiling", target_name_webapp)
            sys.exit(1)
        cmd = [bin_python, str(manage_webapp_file), "migrate"] # django migrate
        return_code = execute_command(cmd)
        if return_code != 0:
            print("ERROR","compiling", target_name_webapp)
            sys.exit(1)
        print("SUCCESS", "compiling", target_name_webapp)
    if clean_compile:
        delete_file(sqlite_file)
        delete_dir(dir_webapp_migrations)
        delete_dir(dir_webapp_editor_models_pycache)
        delete_dir(dir_webapp_editor_pycache)
        delete_dir(dir_webapp_serverapp_pycache)
    if clean_clone:
        pass  # nothing to do - comes from webapp


#######################################
### ADDITIONAL STUFF
#######################################

# in phase clean_clone if all targets are matched remove build directory
if clean_clone and selected_targets == all_targets:
    delete_dir(dir_build)

if clean_compile and selected_targets == all_targets:
    delete_dir(dir_bin)


