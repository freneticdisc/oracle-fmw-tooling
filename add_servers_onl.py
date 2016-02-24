################################################################################
# add_servers_onl.py
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
import datetime
import tempfile
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

    admin_host = options.get("-a")
    domain_home = options.get("-h")
    shared_home = options.get("-s", domain_home)
    as_username = options.get("--as_username", domain_metadata.get("wls").get("as-username"))
    as_password = options.get("--as_password", domain_metadata.get("wls").get("as_password"))
    nm_port = int(options.get("--nm_port", domain_metadata.get("wls").get("nm-port")))
    pwd_file = options.get("-w", "")
    if "--use_plain" not in options:
        as_port = int(options.get("--as_port", domain_metadata.get("wls").get("as-ssl-port")))
        admin_url = "t3s://%s:%s" %(admin_host, as_port)
    else:
        as_port = int(options.get("--as_port", domain_metadata.get("wls").get("as-port")))
        admin_url = "t3://%s:%s" %(admin_host, as_port)
    if "--overwrite" in options:
        overwrite = True
    else:
        overwrite = False

    wait = int(options.get("--wait", 300000))
    timeout = int(options.get("--timeout", -1))
    feature_set = LinkedHashSet(arguments)
    feature_set.retainAll(domain_metadata.keys())
    if feature_set.size() == 0: return

    if not os.path.isdir(domain_home) or overwrite:
        if os.path.isfile(pwd_file):
            bfile = open(pwd_file, "r")
            fcontents = bfile.read().splitlines()
            bfile.close()
            as_password = fcontents.pop()

        host_name = socket.gethostname()
        machine_name = host_name.split(".")[0]
        connect(as_username, as_password, admin_url)
        edit()
        startEdit(waitTimeInMillis=wait, timeOutInMillis=timeout, exclusive="true")
        try:
            dtop_cmo = getMBean("/")
            if machine_name not in [mb.getName() for mb in dtop_cmo.getMachines()]:
                print "Creating Machine %s." %machine_name
                machine = create(machine_name, "UnixMachine")
                cd("/Machines/%s/NodeManager/%s" %(machine_name, machine_name))
                set("DebugEnabled", "true")
                set("ListenAddress", host_name)
                set("ListenPort", int(nm_port))
            else:
                machine = getMBean("/Machines/%s" %machine_name)

            for feature in feature_set:
                server_name = domain_metadata.get(feature).get("server-name")
                server_port = domain_metadata.get(feature).get("server-port")
                server_ssl_port = domain_metadata.get(feature).get("server-ssl-port")
                cluster_name = domain_metadata.get(feature).get("cluster-name")
                # server_name = "%s_%s" %(feature, machine_name)
                today = datetime.datetime.now().strftime("%m%d%Y%H%M%S")

                mserver = getMBean("/Servers/%s" %server_name)
                if mserver.getListenAddress() in (None, ""):
                    print "Configuring Server %s." %server_name
                    mserver.setMachine(machine)
                    mserver.setListenAddress(host_name)
                    mserver.setListenPort(int(server_port))
                    mserver_ssl = mserver.getSSL()
                    mserver_ssl.setEnabled(True)
                    mserver_ssl.setListenPort(int(server_ssl_port))
                    mserver_ssl.setHostnameVerificationIgnored(True)
                    mserver_ssl.setHostnameVerifier("None")
                    mserver_svs = mserver.getServerStart()
                    # mserver_svs.setArguments("-Djava.security.egd=file:/dev/./urandom -XX:+UnlockCommercialFeatures -XX:+ResourceManagement")
                    mserver_svs.setArguments("-Djava.security.egd=file:/dev/./urandom")
                else:
                    counter = 2
                    mserver_list = [mb.getName() for mb in dtop_cmo.getServers()]
                    while True:
                        if "%s%i" %(server_name[:-1], counter) in mserver_list:
                            counter = counter + 1
                        else:
                            server_name = "%s%i" %(server_name[:-1], counter)
                            break
                    cluster = getMBean("/Clusters/%s" %cluster_name)
                    print "Creating Server %s." %server_name
                    cd("/")
                    mserver = create(server_name, "Server")
                    mserver.setMachine(machine)
                    mserver.setCluster(cluster)
                    mserver.setListenAddress(host_name)
                    mserver.setListenPort(int(server_port))
                    mserver_ssl = mserver.getSSL()
                    mserver_ssl.setEnabled(True)
                    mserver_ssl.setListenPort(int(server_ssl_port))
                    mserver_ssl.setHostnameVerificationIgnored(True)
                    mserver_ssl.setHostnameVerifier("None")
                    mserver_svs = mserver.getServerStart()
                    mserver_svs.setArguments("-Djava.security.egd=file:/dev/./urandom -XX:+UnlockCommercialFeatures -XX:+ResourceManagement")

                    jms_resources = domain_metadata.get(feature).get("jms-system-resources", [])
                    for resource in jms_resources:
                        cd("/")
                        fs_name = "%sFileStore%s" %(feature, today)
                        print "Creating FileStore %s." %fs_name
                        filestore = create(fs_name, "FileStore")
                        filestore.setDirectory(os.path.join(shared_home, fs_name))
                        filestore.addTarget(mserver)
                        js_name = "%sJmsServer%s" %(feature, today)
                        print "Creating JMSServer %s." %js_name
                        jmsserver = create(js_name, "JMSServer")
                        jmsserver.addTarget(mserver)
                        cd("/JMSSystemResources/%s" %resource)
                        print "Creating SubDeployment %s." %js_name
                        deployment = create(js_name, "SubDeployment")
                        deployment.addTarget(jmsserver)
                        cd("JMSResource/%s" %resource)
                        jmsmodule = getMBean("/JMSSystemResources/%s/JMSResource/%s" %(resource, resource))
                        for dqueue in jmsmodule.getDistributedQueues():
                            print "Updating DistributedQueue %s." %dqueue.getName()
                            dqueue.setSubDeploymentName(deployment.getName())
                        for queue in jmsmodule.getQueues():
                            print "Updating Queue %s." %queue.getName()
                            queue.setSubDeploymentName(deployment.getName())
                        for udqueue in jmsmodule.getUniformDistributedQueues():
                            print "Updating UniformDistributedQueue %s." %udqueue.getName()
                            udqueue.setSubDeploymentName(deployment.getName())
                        for dtopic in jmsmodule.getDistributedTopics():
                            print "Updating DistributedTopic %s." %dtopic.getName()
                            dtopic.setSubDeploymentName(deployment.getName())
                        for topic in jmsmodule.getTopics():
                            print "Updating Topic %s." %topic.getName()
                            topic.setSubDeploymentName(deployment.getName())
                        for udtopic in jmsmodule.getUniformDistributedTopics():
                            print "Updating UniformDistributedTopic %s." %udtopic.getName()
                            udtopic.setSubDeploymentName(deployment.getName())
        except:
            undo(defaultAnswer="y", unactivatedChanges="true")
            # cancelEdit("y")
            stopEdit("y")
            serverConfig()
            disconnect()
        else:
            save()
            activate(block="true")
            serverConfig()
            print "Writing domain to a template."
            domain_template = tempfile.mktemp() + ".jar"
            writeTemplate(domain_template)
            disconnect()
            print "Loading the template."
            selectCustomTemplate(domain_template)
            loadTemplates()
            setOption("AppDir", os.path.join(domain_home, "applications"))
            setOption("OverwriteDomain", "true")
            print "Configuring Nodemanager."
            cd("/NMProperties")
            set("NodeManagerHome", os.path.join(domain_home, "nodemanager"))
            set("ListenAddress", socket.gethostname())
            set("ListenPort", nm_port)
            print "Writing Domain Configuration."
            writeDomain(domain_home)
            os.unlink(domain_template)
            print "Writing boot.properties."
            bootdir = File(os.path.join(domain_home, "servers", server_name, "security"))
            bootdir.mkdirs()
            bfile = open(os.path.join(domain_home, "servers", server_name, "security", "boot.properties"), "w")
            bfile.write("username=%s\n" %as_username)
            bfile.write("password=%s\n" %as_password)
            bfile.flush()
            bfile.close()
            print "Managed Domain built successfully."

if __name__ == "main":
    options, arguments = getopt.getopt(sys.argv[1:], "?a:h:s:w:", ["use_plain",
                                       "as_port=", "nm_port=", "as_username=",
                                       "as_password=", "wait=", "timeout=",
                                       "overwrite"])
    options = dict(options)
    
    if "-?" in options:
        print "Usage: wlst.[sh|cmd] %s %s %s %s %s %s" %("add_servers_onl.py",
        "[-?] -a admin_server_host -h domain_home [-s shared_home]",
        "[-w password_file] [--as_port adminserver_port] [--nm_port nm_port]",
        "[--use_plain] [--as_username adminserver_username]",
        "[--as_password adminserver_password] [--wait wait_millisecs]",
        "[--timeout timeout_millisecs] [--overwrite]")
        sys.exit(0)

    main(options, arguments)
    exit()
