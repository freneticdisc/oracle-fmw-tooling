################################################################################
# patch_fmw.py
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
import sys
import stat
import getopt
import shutil
import tarfile
import zipfile
import tempfile
import subprocess

def main(options, arguments):
    products = ["jdk", "wls", "bpm", "soa", "wcc", "wcp", "wcs", "ohs"]
    base_dir = os.path.dirname(sys.argv[0])
    if base_dir in [".", ""]: base_dir = os.getcwd()

    if os.path.isfile(os.path.join(base_dir, "metadata.json")):
        with open(os.path.join(base_dir, "metadata.json"), "r") as mfile:
            patch_metadata = eval(mfile.read())
    else:
        print "Mandatory file %s cannot be located in %s." %("metadata.json", base_dir)
        sys.exit(1)

    scratch = options.get("--tmp_loc", tempfile.gettempdir())
    patches_loc = options.get("-l", base_dir)
    ora_home = options.get("-o", "")
    jdk_home = options.get("-j", os.path.join(ora_home, "jdk"))
    fmw_home = options.get("-f", os.path.join(ora_home, "fmw"))

    patch_set = set(arguments).intersection(products)
    if len(patch_set) == 0: sys.exit(1)
    if "bpm" in patch_set: patch_set.discard("soa")

    if "jdk" in patch_set and len(patch_metadata.get("jdk").get("patches")) > 0:
        patch_set.remove("jdk")
        shutil.rmtree(jdk_home)
        os.makedirs(jdk_home, 0750)
        for jdkfile in patch_metadata.get("jdk").get("patches"):
            jdk = tarfile.open(os.path.join(patches_loc, jdkfile))
            for tinfo in jdk.getmembers()[1:]:
                tinfo.name = tinfo.name[len(jdk.getmembers()[0].name) + 1:]
                jdk.extract(tinfo, jdk_home)
            jdk.close()

    # Patch OPatch if needed
    for opatchfile in patch_metadata.get("opatch").get("patches", []):
        opatch = zipfile.ZipFile(os.path.join(patches_loc, opatchfile), allowZip64=True)
        for zipinfo in opatch.infolist():
            extractedfile = opatch.extract(zipinfo.filename, fmw_home)
            os.chmod(extractedfile, zipinfo.external_attr >> 16 & 0xFFF | stat.S_IWUSR)
        opatch.close()

    while len(patch_set) > 0:
        prd = patch_set.pop()
        if os.path.isdir(os.path.join(fmw_home, patch_metadata.get(prd).get("test-dir"))):
            for patch in patch_metadata.get(prd).get("patches", []):
                filelist = []
                patchfile = zipfile.ZipFile(os.path.join(patches_loc, patch), allowZip64=True)
                filelist.extend(patchfile.namelist())
                for zipinfo in patchfile.infolist():
                    extractedfile = patchfile.extract(zipinfo.filename, scratch)
                    os.chmod(extractedfile, zipinfo.external_attr >> 16 & 0xFFF | stat.S_IRUSR | stat.S_IWUSR)
                patchfile.close()

                command = [os.path.join(fmw_home, "OPatch", "opatch")]
                command.extend(["apply", "-silent", "-force", "-oh", fmw_home])
                command.append(os.path.join(scratch, patch[1:9]))

                install_process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                (out, err) = install_process.communicate()
                print out, err

                while len(filelist) > 0:
                    fsobj = filelist.pop()
                    if os.path.isdir(os.path.join(scratch, fsobj)):
                        os.rmdir(os.path.join(scratch, fsobj))
                    else:
                        os.remove(os.path.join(scratch, fsobj))

if __name__ == "__main__":
    options, arguments = getopt.getopt(sys.argv[1:], "?l:o:j:f:", ["tmp_loc="])
    options = dict(options)
    
    if "-?" in options:
        print "Usage: python %s %s %s" %("patch_fmw.py",
        "[-?] -l patches_location -o oracle_home [-j jdk_home] [-f fmw_home]",
        "[--tmp_loc tmp_location] [jdk] [wls] [bpm|soa] [wcc] [wcp] [wcs] [ohs]")
        sys.exit(0)

    main(options, arguments)
