################################################################################
# wait.py
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
import getopt
import socket
import time
from java.sql import DriverManager

def main(options, arguments):
    host = options.get("-h")
    port = int(options.get("-p"))

    timeout = int(options.get("--timeout", 3600))
    delay = int(options.get("--delay", 30))
    socket_timeout = int(options.get("--socket_timeout", 5))
    wait_time = int(options.get("--wait", 0))

    db_conn = options.get("-c", database_metadata.get("database").get("connect-string"))
    dba_user = options.get("--dba_user", "SYS")
    dba_pass = options.get("--dba_password", database_metadata.get("database").get("sys-password"))
    as_port = int(options.get("--as_port", domain_metadata.get("wls").get("as-port")))
    pwd_file = options.get("-w", "")
    if os.path.isfile(pwd_file):
        bfile = open(pwd_file, "r")
        fcontents = bfile.read().splitlines()
        bfile.close()
        dba_pass = fcontents[0]

    now=time.time()
    later = time.time()
    if "--db" in options:
        while int(later - now) < timeout:
            try:
                conn = DriverManager.getConnection("jdbc:oracle:thin:@%s" %db_conn, dba_user, dba_pass)
                conn.close()
                break
            except:
                later = time.time()
                time.sleep(delay)
    else:
        while int(later - now) < timeout:
            try:
                conn=socket.socket()
                conn.settimeout(socket_timeout)
                conn.connect((host, port))
                conn.close()
                break
            except socket.error:
                later = time.time()
                time.sleep(delay)
            except:
                print "ERROR: An unexpected error has occurred."
                sys.exit(2)

    time.sleep(wait_time)

if __name__ == "main":
    options, arguments = getopt.getopt(sys.argv[1:], "?h:p:c:",
                                       ["timeout=", "delay=", "wait=",
                                        "socket_timeout=", "db"])
    options = dict(options)

    if "-?" in options:
        print "Usage: python %s %s %s %s" %("wait.py",
        "[-?] -h host -p port -c db_connect_string [--db] [--wait wait_secs]",
        "[--timeout timeout_in_secs] [--delay delay_in_secs]",
        "[--socket_timeout socket_timeout_in_secs] [--db]")
        sys.exit(0)

    main(options, arguments)
