################################################################################
# main.py
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
import platform
import subprocess
import install_fmw
import patch_fmw
import create_schemas
import drop_schemas

options, arguments = getopt.getopt(sys.argv[1:], "?ipl:o:j:f:h:s:c:m:w:a:", [
                                    "rsp_file=", "domain_name=", "nm_port=",
                                    "as_port=", "as_ssl_port=", "db_password=",
                                    "nm_password=", "as_username=", "dba_user=",
                                    "dba_password=", "soa_profile=",
                                    "analytics_with_partitioning=",
                                    "as_password=", "tmp_loc=", "inst_group=",
                                    "use_plain", "drop-schemas", "create_domain",
                                    "add_servers", "install", "patch", "all",
                                    "overwrite", "wait_time=", "timeout=",
                                    "wait"])
options = dict(options)

if "-?" in options:
    print "Usage: python %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s" %(
    "main.py [-?ip] -l installers_patches_location -o oracle_home [-j jdk_home]",
    "[-f fmw_home] -h domain_home [-s shared_home] -c db_connect_string",
    "-m db_prefix [-w password_file] [-a admin_server_host]",
    "[--rsp_file install_response_file] [--domain_name domain_name]",
    "[--nm_port nm_port] [--as_port adminserver_port]",
    "[--as_ssl_port adminserver_sslport] [--db_password db_datasource_passwd]",
    "[--nm_password nodemanager_passwd] [--as_username adminserver_username]",
    "[--as_password adminserver_password] [--dba_user SYS|SYSTEM]",
    "[--dba_password dba_password] [--soa_profile SMALL|MED|LARGE]",
    "[--analytics_with_partitioning N|Y] [--tmp_loc tmp_location]",
    "[--inst_group install_os_group] [--use_plain] [--drop-schemas] [-all]",
    "[--create_domain] [--add_servers] [--install] [--patch] [--overwrite]",
    "[--wait milliseconds] [--timeout milliseconds] [jdk] [wls] [bpm|soa]",
    "[wcc] [wcp] [wcs] [ibr] [ucm] [capture] [wccadf] [portal] [pagelet portlet]",
    "[discussions] [analytics] [sites] [vs] [insights] [sc] [ss] [ohs]")
    sys.exit(0)

base_dir = os.path.dirname(sys.argv[0])
if base_dir in [".", ""]: base_dir = os.getcwd()

wlst = "wlst.cmd" if platform.system() == "Windows" else "wlst.sh"

if "--wait" in options:
    if "-c" in options:
        command = [os.path.join(options.get("-f"), "oracle_common", "common", "bin", wlst),
                   os.path.join(base_dir, "wait.py")]
        if "-c" in options: command.extend(["-c", options.get("-c")])
        if "-w" in options: command.extend(["-w", options.get("-w")])
        if "--dba_user" in options: command.extend(["--dba_user", options.get("--dba_user")])
        if "--dba_password" in options: command.extend(["--dba_password", options.get("--dba_password")])
        command.append("--db")
        command.extend(["--wait", "120"])
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (out, err) = process.communicate()
        print out, err
        if process.returncode > 0: sys.exit(process.returncode)

    if "-a" in options:
        command = [os.path.join(options.get("-f"), "oracle_common", "common", "bin", wlst),
                   os.path.join(base_dir, "wait.py")]
        if "-a" in options: command.extend(["-h", options.get("-a")])
        if "--as_port" in options: command.extend(["-p", options.get("--as_port")])
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (out, err) = process.communicate()
        print out, err
        if process.returncode > 0: sys.exit(process.returncode)

if "--drop-schemas" in options:
    suboptions = {}
    if "-f" in options: suboptions["-f"] = options.get("-f")
    if "-c" in options: suboptions["-c"] = options.get("-c")
    if "-m" in options: suboptions["-m"] = options.get("-m")
    if "-w" in options: suboptions["-w"] = options.get("-w")
    if "--dba_user" in options: suboptions["--dba_user"] = options.get("--dba_user")
    if "--dba_password" in options: suboptions["--dba_password"] = options.get("--dba_password")
    if "--all" in options: suboptions["--all"] = options.get("--all")
    drop_schemas.main(suboptions, arguments)
    sys.exit(0)

if "--install" in options or "-i" in options:
    suboptions = {}
    if "-l" in options: suboptions["-l"] = options.get("-l")
    if "-o" in options: suboptions["-o"] = options.get("-o")
    if "-j" in options: suboptions["-j"] = options.get("-j")
    if "-f" in options: suboptions["-f"] = options.get("-f")
    if "--rsp_file" in options: suboptions["--rsp_file"] = options.get("--rsp_file")
    if "--tmp_loc" in options: suboptions["--tmp_loc"] = options.get("--tmp_loc")
    if "--inst_group" in options: suboptions["--inst_group"] = options.get("--inst_group")
    install_fmw.main(suboptions, arguments)

if "--patch" in options or "-p" in options:
    suboptions = {}
    if "-l" in options: suboptions["-l"] = options.get("-l")
    if "-o" in options: suboptions["-o"] = options.get("-o")
    if "-j" in options: suboptions["-j"] = options.get("-j")
    if "-f" in options: suboptions["-f"] = options.get("-f")
    if "--tmp_loc" in options: suboptions["--tmp_loc"] = options.get("--tmp_loc")
    patch_fmw.main(suboptions, arguments)

if "--create_domain" in options:
    suboptions = {}
    if "-f" in options: suboptions["-f"] = options.get("-f")
    if "-c" in options: suboptions["-c"] = options.get("-c")
    if "-m" in options: suboptions["-m"] = options.get("-m")
    if "-w" in options: suboptions["-w"] = options.get("-w")
    if "--dba_user" in options: suboptions["--dba_user"] = options.get("--dba_user")
    if "--dba_password" in options: suboptions["--dba_password"] = options.get("--dba_password")
    if "--db_password" in options: suboptions["--dbs_password"] = options.get("--db_password")
    if "--soa_profile" in options: suboptions["--soa_profile"] = options.get("--soa_profile")
    if "--analytics_with_partitioning" in options:
        suboptions["--analytics_with_partitioning"] = options.get("--analytics_with_partitioning")
    create_schemas.main(suboptions, arguments)

    command = [os.path.join(options.get("-f"), "oracle_common", "common", "bin", wlst),
               os.path.join(base_dir, "create_domain_off.py")]
    if "-h" in options: command.extend(["-h", options.get("-h")])
    if "-s" in options: command.extend(["-s", options.get("-s")])
    if "-c" in options: command.extend(["-c", options.get("-c")])
    if "-m" in options: command.extend(["-m", options.get("-m")])
    if "-w" in options: command.extend(["-w", options.get("-w")])
    if "--domain_name" in options: command.extend(["--domain_name", options.get("--domain_name")])
    if "--nm_port" in options: command.extend(["--nm_port", options.get("--nm_port")])
    if "--as_port" in options: command.extend(["--as_port", options.get("--as_port")])
    if "--as_ssl_port" in options: command.extend(["--as_ssl_port", options.get("--as_ssl_port")])
    if "--db_password" in options: command.extend(["--db_password", options.get("--db_password")])
    if "--nm_password" in options: command.extend(["--nm_password", options.get("--nm_password")])
    if "--as_password" in options: command.extend(["--as_password", options.get("--as_password")])
    command.extend(arguments)
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (out, err) = process.communicate()
    print out, err
    if process.returncode > 0: sys.exit(process.returncode)

if "--extend_domain" in options:
    suboptions = {}
    if "-f" in options: suboptions["-f"] = options.get("-f")
    if "-c" in options: suboptions["-c"] = options.get("-c")
    if "-m" in options: suboptions["-m"] = options.get("-m")
    if "-w" in options: suboptions["-w"] = options.get("-w")
    if "--dba_user" in options: suboptions["--dba_user"] = options.get("--dba_user")
    if "--dba_password" in options: suboptions["--dba_password"] = options.get("--dba_password")
    if "--db_password" in options: suboptions["--dbs_password"] = options.get("--db_password")
    if "--soa_profile" in options: suboptions["--soa_profile"] = options.get("--soa_profile")
    if "--analytics_with_partitioning" in options:
        suboptions["--analytics_with_partitioning"] = options.get("--analytics_with_partitioning")
    create_schemas.main(suboptions, arguments)

    command = [os.path.join(options.get("-f"), "oracle_common", "common", "bin", wlst),
               os.path.join(base_dir, "extend_domain_off.py")]
    if "-h" in options: command.extend(["-h", options.get("-h")])
    if "-s" in options: command.extend(["-s", options.get("-s")])
    if "-c" in options: command.extend(["-c", options.get("-c")])
    if "-m" in options: command.extend(["-m", options.get("-m")])
    if "-w" in options: command.extend(["-w", options.get("-w")])
    if "--domain_name" in options: command.extend(["--domain_name", options.get("--domain_name")])
    if "--nm_port" in options: command.extend(["--nm_port", options.get("--nm_port")])
    if "--as_port" in options: command.extend(["--as_port", options.get("--as_port")])
    if "--as_ssl_port" in options: command.extend(["--as_ssl_port", options.get("--as_ssl_port")])
    if "--db_password" in options: command.extend(["--db_password", options.get("--db_password")])
    if "--nm_password" in options: command.extend(["--nm_password", options.get("--nm_password")])
    if "--as_password" in options: command.extend(["--as_password", options.get("--as_password")])
    command.extend(arguments)
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (out, err) = process.communicate()
    print out, err
    if process.returncode > 0: sys.exit(process.returncode)

if "--add_servers" in options:
    command = [os.path.join(options.get("-f"), "oracle_common", "common", "bin", wlst),
               os.path.join(base_dir, "add_servers_onl.py")]
    if "-a" in options: command.extend(["-a", options.get("-a")])
    if "-h" in options: command.extend(["-h", options.get("-h")])
    if "-s" in options: command.extend(["-s", options.get("-s")])
    if "-w" in options: command.extend(["-w", options.get("-w")])
    if "--nm_port" in options: command.extend(["--nm_port", options.get("--nm_port")])
    if "--as_port" in options: command.extend(["--as_port", options.get("--as_port")])
    if "--as_username" in options: command.extend(["--as_username", options.get("--as_username")])
    if "--as_password" in options: command.extend(["--as_password", options.get("--as_password")])
    if "--use_plain" in options: command.append("--use_plain")
    if "--overwrite" in options: command.append("--overwrite")
    if "--wait_time" in options: command.extend(["--wait", options.get("--wait_time")])
    if "--timeout" in options: command.extend(["--timeout", options.get("--timeout")])
    command.extend(arguments)
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (out, err) = process.communicate()
    print out, err
    if process.returncode > 0: sys.exit(process.returncode)
