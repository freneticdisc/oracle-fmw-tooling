## Oracle Fusion Middleware 12c Domain Creation Scripts
Project to build WebLogic Domains with Oracle Fusion Middleware 12c components using scripts. These components include the BPM Suite, SOA Suite, B2B and Healthcare, WebCenter Content, WebCenter Portal, WebCenter Sites and WebTier Utilities.

These scripts will be able to install one or more products and create a domain with one or more product templates. You will have fine grained control on what features you want to enable for the domain as well.

### Pre-requisites
These scripts assume that the Hardware, Software and the Kernel Parameters pre-requisites have all been met for the Oracle Fusion Middleware product stack. You can review these pre-requisites on the [Oracle Fusion Middleware Documentation][oradocs] website.

Apart from these requirements, these scripts use python to perform its tasks. This means that the all product installs, configuration, domain creation and configuration commands will be run from a python shell. Note that Python 2.6 or later must be installed on the servers for the scripts to work properly.

### Usage
To install the Oracle Fusion Middleware Components. Download the gz archive for Java and the zip archives for the FMW products and make it available in the installer_location. There is no need to extract the software; the script will take care of it.

There is a wrapper script available that you can use to execute one or more scripts in order. The usage of the script is as follows:

`/usr/bin/python main.py [-?ip] -l installers_patches_location -o oracle_home [-j jdk_home] [-f fmw_home] -h domain_home [-s shared_home] -c db_connect_string -m db_prefix [-w password_file] [-a admin_server_host] [--rsp_file install_response_file] [--domain_name domain_name] [--nm_port nm_port] [--as_port adminserver_port] [--as_ssl_port adminserver_sslport] [--db_password db_datasource_passwd] [--nm_password nodemanager_passwd] [--as_username adminserver_username] [--as_password adminserver_password] [--dba_user SYS|SYSTEM] [--dba_password dba_password] [--soa_profile SMALL|MED|LARGE] [--analytics_with_partitioning N|Y] [--tmp_loc tmp_location] [--inst_group install_os_group] [--use_plain] [--drop-schemas] [-all] [--create_domain] [--add_servers] [--install] [--patch] [--overwrite] [jdk] [wls] [bpm|soa] [wcc] [wcp] [wcs] [ibr] [ucm] [capture] [wccadf] [portal] [pagelet portlet] [discussions] [analytics] [sites] [vs] [insights] [sc] [ss][ohs]`

If you want to have more fine grained control on the install and configure process, you could use the individual scripts. The usage of these scripts is shown below:

To install the software:

`/usr/bin/python install_fmw.py [-?] -l installers_location -o oracle_home [-j jdk_home] [-f fmw_home] [--rsp_file install_response_file] [--tmp_loc tmp_location] [--os_install_group install_os_group] [wls] [bpm|soa] [wcc] [wcp] [wcs] [ohs]`

To create product schemas.

`/usr/bin/python create_schemas.py [-?] -f fmw_home -c db_connect_string -m db_prefix [-w password_file] [--dba_user db_admin_user] [--dba_password db_admin_password] [--dbs_password db_schema_password] [--soa_profile SMALL|MED|LARGE] [--analytics_with_partitioning N|Y] [em] [bpm|soa] [ucm] [capture] [wccadf] [portal] [pagelet portlet] [discussions] [analytics] [sites] [vs] [insights] [sc] [ss]`

To drop any product schemas.

`/usr/bin/python drop_schemas.py [-?] [--all] -f fmw_home -c db_connect_string -m db_prefix [-w password_file] [--dba_user db_admin_user] [--dba_password db_admin_password] [em] [bpm|soa] [ucm] [capture] [wccadf] [portal] [pagelet portlet] [discussions] [analytics] [sites] [vs] [insights] [sc] [ss]`

To create a basic weblogic domain with just the admin server configured:

`wlst.[sh|cmd] build_domain_off.py [-?] -h domain_home [-s shared_home] -c db_connect_string -m db_prefix [-w password_file] [--domain_name domain_name] [--nm_port nm_port] [--as_port adminserver_port] [--as_ssl_port adminserver_sslport] [--db_password db_datasource_passwd] [--nm_password nodemanager_passwd] [--as_password adminserver_password] wls`

To create a weblogic domain with fusion middleware components:

`wlst.[sh|cmd] build_domain_off.py [-?] -h domain_home [-s shared_home] -c db_connect_string -m db_prefix [-w password_file] [--domain_name domain_name] [--nm_port nm_port] [--as_port adminserver_port] [--as_ssl_port adminserver_sslport] [--db_password db_datasource_passwd] [--nm_password nodemanager_passwd] [--as_password adminserver_password] [wls] [bpm|soa] [ibr] [ucm] [capture] [wccadf] [portal] [pagelet portlet] [discussions] [analytics] [sites] [vs] [insights] [sc] [ss] [ohs]`

To add a new managed server to the domain:

`wlst.[sh|cmd] add_servers_onl.py [-?] -a admin_server_host -h domain_home [-s shared_home] [-w password_file] [--as_port adminserver_port] [--nm_port nm_port] [--use_plain] [--as_username adminserver_username] [--as_password adminserver_password] [--overwrite]`

### License
This program is free software: you can redistribute it and/or modify it as long as you retain the name of the original author and under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.

[oradocs]: http://docs.oracle.com/en/middleware/middleware.html "Oracle Fusion Middleware Documentation"
