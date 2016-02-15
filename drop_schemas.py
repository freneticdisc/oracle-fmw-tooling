################################################################################
# drop_schemas.py
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
import getopt
import subprocess

def main(options, arguments):
    base_dir = os.path.dirname(sys.argv[0])
    if base_dir in [".", ""]: base_dir = os.getcwd()

    if os.path.isfile(os.path.join(base_dir, "metadata.json")):
        with open(os.path.join(base_dir, "metadata.json"), "r") as mfile:
            database_metadata = eval(mfile.read())
    else:
        print "Mandatory file %s cannot be located in %s." %("metadata.json", base_dir)
        sys.exit(1)

    fmw_home = options.get("-f")
    db_conn = options.get("-c", database_metadata.get("database").get("connect-string"))
    dba_user = options.get("--dba_user", "SYS")
    dba_pass = options.get("--dba_password", database_metadata.get("database").get("sys-password"))
    db_prfix = options.get("-m")
    pwd_file = options.get("-w", "")
    delete_all = 1 if "--all" in options else 0

    comp_set = set(arguments).intersection(database_metadata)
    if len(comp_set) == 0 and not delete_all: exit(0)
    comp_set.discard("wls")
    # comp_set.add("em")

    rcu_input = "%s\n" %(dba_pass)
    if os.path.isfile(pwd_file):
        with open(pwd_file, "r") as bfile:
            rcu_input = bfile.read()

    # Get the list of schemas for the given prefix
    command = [os.path.join(fmw_home, "oracle_common", "bin", "rcu"),
               '-silent', '-listSchemas', '-connectString', db_conn,
               '-dbUser', dba_user, '-dbRole', 'sysdba', '-schemaPrefixes', db_prfix]

    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (out, err) = process.communicate(input=rcu_input)
    if process.returncode > 0: exit(process.returncode)

    inst_comps = []
    for line in out.splitlines():
        if line.startswith("\t") and \
        not line.startswith("\t---") and \
        not line.startswith("\tRCU") and \
        not line.startswith("\tCOMP_ID"):
            comp = line.split()[0]
            comp = "CONTENT" if comp == "OCS" else comp
            comp = "CONTENTSEARCH" if comp == "OCSSEARCH" else comp
            inst_comps.append(comp)

    comp_ids = []
    if delete_all:
        for comp in inst_comps:
            comp_ids.extend(["-component", comp])
    else:
        for prd in comp_set:
            for comp in database_metadata.get(prd).get("comp_ids", []):
                if comp in inst_comps:
                    comp_ids.extend(["-component", comp])
                    inst_comps.append(comp)

    # Execute RCU to drop schemas
    command = [os.path.join(fmw_home, "oracle_common", "bin", "rcu"), "-silent",
               "-dropRepository", "-databaseType", "ORACLE", "-connectString", db_conn,
               "-dbUser", dba_user, "-dbRole", "SYSDBA", "-schemaPrefix", db_prfix]
    command.extend(comp_ids)

    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (out, err) = process.communicate(input=rcu_input)
    print out, err
    if process.returncode > 0: sys.exit(process.returncode)

if __name__ == "__main__":
    options, arguments = getopt.getopt(sys.argv[1:], "?f:c:m:w:",
                                       ["all", "dba_user=", "dba_password="])
    options = dict(options)
    
    if "-?" in options:
        print "Usage: python %s %s %s %s %s" %("drop_schemas.py",
        "[-?] [--all] -f fmw_home -c db_connect_string -m db_prefix [-w password_file]",
        "[--dba_user db_admin_user] [--dba_password db_admin_password]",
        "[em] [bpm|soa] [ucm] [capture] [wccadf] [portal] [pagelet portlet]",
        "[discussions] [analytics] [sites] [vs] [insights] [sc] [ss]")
        sys.exit(0)

    main(options, arguments)
