################################################################################
# install_fmw.py
#
# Copyright (C) 2016 Justin Paul <justinpaulthekkan@gmail.com>
#
# @author: Justin Paul
#
# This program is free software: you can redistribute it and/or modify
# it as long as you retain the name of the original author and under
# the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
################################################################################
import os
import grp
import sys
import stat
import getopt
import tarfile
import zipfile
import tempfile
import subprocess

def main(options, arguments):
    products = ["wls", "bpm", "soa", "wcc", "wcp", "wcs", "ohs"]
    base_dir = os.path.dirname(sys.argv[0])
    if base_dir in [".", ""]: base_dir = os.getcwd()

    if os.path.isfile(os.path.join(base_dir, "metadata.json")):
        with open(os.path.join(base_dir, "metadata.json"), "r") as mfile:
            install_metadata = eval(mfile.read())
    else:
        print "Mandatory file %s cannot be located in %s." %("metadata.json", base_dir)
        sys.exit(1)

    scratch = options.get("--tmp_loc", tempfile.gettempdir())
    installer_loc = options.get("-l", base_dir)
    ora_home = options.get("-o", "")
    jdk_home = options.get("-j", os.path.join(ora_home, "jdk"))
    fmw_home = options.get("-f", os.path.join(ora_home, "fmw"))
    rsp_file = options.get("--rsp_file", os.path.join(base_dir, "silentinstall.rsp"))
    inst_grp = options.get("--inst_group", grp.getgrgid(os.getgid()).gr_name)

    install_set = set(arguments).intersection(products)
    if len(install_set) == 0: sys.exit(1)
    if "bpm" in install_set: install_set.discard("soa")
    install_set.add("wls")

    # Check if Java is installed and if not install it
    if not os.path.isfile(os.path.join(jdk_home, "bin", "java")) and \
    not os.path.isfile(os.path.join(jdk_home, "bin", "java.exe")):
        if not os.path.exists(jdk_home): os.makedirs(jdk_home, 0750)
        for jdkfile in install_metadata.get("jdk").get("files"):
            jdk = tarfile.open(os.path.join(installer_loc, jdkfile))
            for tinfo in jdk.getmembers()[1:]:
                tinfo.name = tinfo.name[len(jdk.getmembers()[0].name) + 1:]
                jdk.extract(tinfo, jdk_home)
            jdk.close()

    tmp_file = tempfile.mktemp()
    with open(tmp_file, "w") as bfile:
        bfile.write("inventory_loc=%s\n" %os.path.join(ora_home, "oraInventory"))
        bfile.write("inst_group=%s\n" %inst_grp)
        bfile.flush()

    while len(install_set) > 0:
        if "wls" not in install_set:
            prd = install_set.pop()
        else:
            prd = "wls"
            install_set.remove("wls")
            if not os.path.exists(ora_home): os.makedirs(ora_home, 0750)
            if not os.path.exists(fmw_home): os.makedirs(fmw_home, 0750)

        if not os.path.isdir(os.path.join(fmw_home, install_metadata.get(prd).get("test-dir"))):
            filelist = []
            for wlsfile in install_metadata.get(prd).get("files"):
                wls = zipfile.ZipFile(os.path.join(installer_loc, wlsfile), allowZip64=True)
                filelist.extend(wls.namelist())
                wls.extractall(scratch)
                wls.close()

            command = [os.path.join(jdk_home, "bin", "java"), "-jar"]
            if prd == "ohs":
                command = []
                os.chmod(os.path.join(scratch, install_metadata.get(prd).get("installer")), stat.S_IRWXU)

            command.extend([os.path.join(scratch, install_metadata.get(prd).get("installer")),
                            "-novalidation", "-silent", "-invPtrLoc", tmp_file])
            if os.path.isfile(rsp_file):
                command.extend(["-responseFile", rsp_file])
            command.append("ORACLE_HOME=%s" %fmw_home)
            if install_metadata.get(prd).get("install_type"):
                command.append("INSTALL_TYPE=%s" %install_metadata.get(prd).get("install_type"))

            install_process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            (out, err) = install_process.communicate()
            print out, err

            for filename in filelist:
                os.remove(os.path.join(scratch, filename))

    os.unlink(tmp_file)

if __name__ == "__main__":
    options, arguments = getopt.getopt(sys.argv[1:], "?l:o:j:f:",
                                       ["rsp_file=", "tmp_loc=",
                                        "inst_group="])
    options = dict(options)
    
    if "-?" in options:
        print "Usage: python %s %s %s %s %s" %("install_fmw.py",
        "[-?] -l installers_location -o oracle_home [-j jdk_home] [-f fmw_home]",
        "[--rsp_file install_response_file] [--tmp_loc tmp_location]",
        "[--inst_group install_os_group] [wls] [bpm|soa] [wcc] [wcp] [wcs]",
        "[ohs]")
        sys.exit(0)

    main(options, arguments)
