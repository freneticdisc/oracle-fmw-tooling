################################################################################
# create_domain_off.py
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
from wlstModule import *    #@UnusedWildImport
from java.util import LinkedHashSet

def main(options, arguments):
    base_dir = os.path.dirname(sys.argv[0])
    if base_dir in [".", ""]: base_dir = os.getcwd()

    if os.path.isfile(os.path.join(base_dir, "metadata.json")):
        mfile = open(os.path.join(base_dir, "metadata.json"), "r")
        domain_metadata = eval(mfile.read())
        mfile.close()
    else:
        print "Mandatory file %s cannot be located in %s." %("metadata.json", base_dir)
        sys.exit(1)

    domain_home = options.get("-h")
    domain_name = options.get("--domain_name", os.path.basename(domain_home))
    shared_home = options.get("-s", domain_home)
    db_conn = options.get("-c", domain_metadata.get("database").get("connect-string"))
    db_pass = options.get("--db_password", domain_metadata.get("database").get("schema-password"))
    db_prfix = options.get("-m")
    nm_pass = options.get("--nm_password", domain_metadata.get("wls").get("nm_password"))
    as_pass = options.get("--as_password", domain_metadata.get("wls").get("as_password"))
    pwd_file = options.get("-w", "")
    nm_port = int(options.get("--nm_port", domain_metadata.get("wls").get("nm-port")))
    as_port = int(options.get("--as_port", domain_metadata.get("wls").get("as-port")))
    as_sport = int(options.get("--as_ssl_port", domain_metadata.get("wls").get("as-ssl-port")))
    
    as_name = domain_metadata.get("wls").get("server-name")
    as_user = domain_metadata.get("wls").get("as-username")
    nm_user = domain_metadata.get("wls").get("nm-username")

    feature_set = LinkedHashSet(arguments)
    feature_set.retainAll(domain_metadata.keys())
    feature_set.remove("jdk")
    feature_set.remove("wcc")
    feature_set.remove("wcp")
    feature_set.remove("wcs")
    if feature_set.size() == 0: sys.exit(0)
    if not(feature_set.size() == 1 and "wls" in feature_set): feature_set.add("em")

    setShowLSResult(false)
    selected_features = []
    avail_tmplts = showAvailableTemplates()
    index1 = avail_tmplts.find("20849: Currently available templates for loading:")
    index2 = avail_tmplts.find("20849: No action required.")
    avail_tmplts = [tmplt.split(":", 1) for tmplt in avail_tmplts[index1 + 50:index2 - 2].splitlines()]
    avail_tmplts = dict(avail_tmplts)

    if not os.path.isfile(os.path.join(domain_home, "config", "config.xml")):
        if os.path.isfile(pwd_file):
            bfile = open(pwd_file, "r")
            fcontents = bfile.read().splitlines()
            bfile.close()
            db_pass = fcontents.pop()
            as_pass = fcontents.pop()
            nm_pass = fcontents.pop()
        
        selected_features.append("wls")
        feature_set.remove("wls")
        if "em" in feature_set and \
        domain_metadata.get("em").get("template-name") in avail_tmplts:
            selected_features.append("em")
            feature_set.remove("em")

        for feature in feature_set:
            if domain_metadata.get(feature).get("template-name") in avail_tmplts:
                selected_features.append(feature)
        if len(selected_features) == 0: return

        print "Creating the Domain."
        print "Loading Required Templates."
        for feature in selected_features:
            print "\t%s version %s" %(domain_metadata.get(feature).get("template-name"), \
                                      domain_metadata.get(feature).get("version"))
            selectTemplate(domain_metadata.get(feature).get("template-name"))
        loadTemplates()

        print "Setting Domain Options."
        start_mode = domain_metadata.get("wls").get("server-start-mode")
        setOption("AppDir", os.path.join(domain_home, "applications"))
        setOption("DomainName", domain_name)
        setOption("OverwriteDomain", "true")
        setOption("ServerStartMode", start_mode)

        selected_features.remove("wls")
        print "Configuring Admin Server."
        cd("/Servers/AdminServer")
        set("ListenAddress", socket.gethostname())
        set("ListenPort", as_port)
        set("Name", as_name)

        print "\tSSL"
        create(as_name, "SSL")
        cd("SSL/%s" %as_name)
        set("Enabled", "True")
        set("ListenPort", as_sport)
        set("HostnameVerificationIgnored", "true")
        set("HostnameVerifier", "None")

        print "\tServerStart"
        cd('/Servers/%s' %as_name)
        create(as_name, 'ServerStart')
        cd('ServerStart/NO_NAME_0')
        # set("Arguments", "-XX:+UnlockCommercialFeatures -XX:+ResourceManagement -Djava.security.egd=file:/dev/./urandom")
        set("Arguments", "-Djava.security.egd=file:/dev/./urandom")

        print "Configuring Admin User."
        cd("/Security/base_domain/User/weblogic")
        set("Name", as_user)
        set("Password", as_pass)

        print "Configuring Security Configuration."
        cd("/SecurityConfiguration/%s"  %"base_domain")
        set("NodeManagerUsername", nm_user)
        set("NodeManagerPasswordEncrypted", nm_pass)

        print "Configuring Nodemanager."
        cd("/NMProperties")
        set("NodeManagerHome", os.path.join(domain_home, "nodemanager"))
        set("ListenAddress", socket.gethostname())
        set("ListenPort", nm_port)

        cluster_set = LinkedHashSet()
        for feature in selected_features:
            print "Configuring feature %s." %feature
            cluster_name = domain_metadata.get(feature).get("cluster-name")
            server_name = domain_metadata.get(feature).get("server-name")

            feature_credentials = domain_metadata.get(feature).get("credentials", {})
            for credential in feature_credentials:
                for credkey in feature_credentials.get(credential, {}):
                    print "\tUpdating Key %s in Credential %s" %(credkey, credential)
                    cd("/Credential/TargetStore/%s/TargetKey/%s" %(credential, credkey))
                    create(credkey, "Credential")
                    cd("Credential")
                    set("Username", feature_credentials.get(credential).get(credkey).get("username"))
                    set("Password", feature_credentials.get(credential).get(credkey).get("password"))

            for filestore in domain_metadata.get(feature).get("file-stores", []):
                print "\tUpdating Filestore %s" %filestore
                cd("/FileStore/%s" %filestore)
                set("Target", as_name)
                set("Directory", os.path.join(shared_home, get("Directory")))

            jms_system_resources = domain_metadata.get(feature).get("jms-system-resources", [])
            for jmssr in jms_system_resources:
                subdeployments = ls("/JMSSystemResource/%s/SubDeployment" %jmssr, returnMap="true")
                for subdeployment in subdeployments:
                    cd("/JMSSystemResource/%s/SubDeployment/%s" %(jmssr, subdeployment))
                    for jmsserver in get("Target"):
                        cd("/JMSServer/%s" %jmsserver.getName())
                        filestore = get("PersistentStore").getName()
                        m_servers = get("Target")
                        if m_servers[0].getName() == server_name:
                            print "\tUpdating Filestore %s" %filestore
                            cd("/FileStore/%s" %filestore)
                            set("Directory", os.path.join(shared_home, get("Directory")))

            for ds in domain_metadata.get(feature).get("datasources", []):
                ds_name = ds.get("name")
                ds_scma = ds.get("schema")
                print "\tUpdating Data Source %s" %ds_name
                cd("/JDBCSystemResources/%s/JdbcResource/%s/JDBCDriverParams/NO_NAME_0" %(ds_name, ds_name))
                set("DriverName", "oracle.jdbc.OracleDriver")
                set("URL", "jdbc:oracle:thin:@%s" %db_conn)
                set("PasswordEncrypted", db_pass)
                cd("Properties/NO_NAME_0/Property/user")
                set("Value", "%s_%s" %(db_prfix, ds_scma))
                cd("/JDBCSystemResources/%s/JdbcResource/%s" %(ds_name, ds_name))
                create(ds_name, "JDBCOracleParams")
                cd("JDBCOracleParams/NO_NAME_0")
                set("FanEnabled", false)
                set("OnsNodeList", "")

            if cluster_name not in cluster_set and cluster_name is not None:
                cluster_set.add(cluster_name)
                print "\tCreating cluster %s" %cluster_name
                cd("/")
                create(cluster_name, "Cluster")
                cd("/Clusters/%s" %cluster_name)
                set("ClusterMessagingMode", "unicast")
                set("WeblogicPluginEnabled", 1)
                cd("/")
                print "\tTargeting resources to cluster %s" %cluster_name
                assign("Server", server_name, "Cluster", cluster_name)

        if len(selected_features) > 0:
            print "Data Sources Auto Config"
            getDatabaseDefaults()
            # setFEHostURL("plainurl", "sslurl", isDefaultPlain="True")

        print "Writing Domain Configuration."
        writeDomain(domain_home)

        print "Writing boot.properties."
        bootdir = File(os.path.join(domain_home, "servers", as_name, "security"))
        bootdir.mkdirs()
        bfile = open(os.path.join(domain_home, "servers", as_name, "security", "boot.properties"), "w")
        bfile.write("username=%s\n" %as_user)
        bfile.write("password=%s\n" %as_pass)
        bfile.flush()
        bfile.close()

        print "Domain built successfully."
    else:
        print "Domain exists already."

if __name__ == "main":
    options, arguments = getopt.getopt(sys.argv[1:], "?h:s:c:m:w:",
                                       ["domain_name=", "nm_port=", "as_port=",
                                        "as_ssl_port=", "db_password=",
                                        "nm_password=", "as_password="])
    options = dict(options)

    if "-?" in options:
        print "Usage: wlst.[sh|cmd] %s %s %s %s %s %s %s %s%s%s%s%s" %("create_domain_off.py",
        "[-?] -h domain_home [-s shared_home] -c db_connect_string -m db_prefix",
        "[-w password_file] [--domain_name domain_name] [--nm_port nm_port]",
        "[--as_port adminserver_port] [--as_ssl_port adminserver_sslport]",
        "[--db_password db_datasource_passwd] [--nm_password nodemanager_passwd]",
        "[--as_password adminserver_password] [wls] [bpm|soa] [ibr] [ucm]",
        "[capture] [wccadf] [portal] [pagelet portlet] [discussions]",
        "[analytics] [sites] [vs] [insights] [sc] [ss] [ohs]",
        "\n\npassword_file format:", "\n\t1st line: nodemanager_passwd",
        "\n\t2nd line: adminserver_password", "\n\tlast line: db_datasource_passwd")
        sys.exit(0)

    main(options, arguments)
    exit()
