
import paramiko
import regex
import datetime
import tabulate

class SSHClientPlus:
    def __init__(self, hostname, user, password):
        self._sshClient = paramiko.SSHClient()
        self._sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._hostname = hostname
        self._user = user
        self._password = password
    def connect(self):
        self._sshClient.connect(self._hostname,username=self._user,password=self._password)
    def disconnect(self):
        self._sshClient.close()
    def execute(self, command):
        print command
        command = 'echo $$; exec ' + command
        stdin, stdout, stderr = self._sshClient.exec_command(command)
        pid = int(stdout.readline())
        return pid, stdin, stdout, stderr


class SSHClientLatencyTarget(SSHClientPlus):
    def __init__(self, hostname, ipaddress, user, password):
        SSHClientPlus.__init__(self,hostname, user, password)
        self.connect()
        self._IPAddress = ipaddress
    def startServer(self):
        # get network card name from ipaddress
        command = "ifconfig -a | grep -E 'flags|inet' | sed 's/inet//g' | awk '{print $1}' | sed '$!N;s/\\n/ /' | sed 's/://' | grep %s" %(self._IPAddress)
        pid,stdin,stdout,stderr = self.execute(command)
        line = stdout.readline()
        print line
        items = line.split()
        if len(items)!=2:
            return None
        networkCardName = items[0]
        
        tcpdumpCommand = "tcpdump -ttt -i %s ip proto \\\\icmp and host %s" %(networkCardName,self._IPAddress)
        self._pid, stdin, self._stdout, self._stderr = self.execute(tcpdumpCommand)
        return networkCardName
        
    def stopServer(self):
        self.execute("kill %d" %(self._pid))
        
    def parseLatency(self):
        """
        Output sample:
        00:00:00.000000 IP host1 > 192.168.0.1: ICMP echo request, id 94, seq 0, length 508
        00:00:00.000027 IP 192.168.0.1 > host1: ICMP echo reply, id 94, seq 0, length 508
        00:00:01.000067 IP host1 > 192.168.0.1: ICMP echo request, id 94, seq 1, length 508
        00:00:00.000024 IP 192.168.0.1 > host1: ICMP echo reply, id 94, seq 1, length 508
        00:00:01.000052 IP host1 > 192.168.0.1: ICMP echo request, id 94, seq 2, length 508
        00:00:00.000042 IP 192.168.0.1 > host1: ICMP echo reply, id 94, seq 2, length 508
        00:00:01.000026 IP host1 > 192.168.0.1: ICMP echo request, id 94, seq 3, length 508
        00:00:00.000038 IP 192.168.0.1 > host1: ICMP echo reply, id 94, seq 3, length 508

        """
        microsecond = 0
        pingTimes = 0
        for line in self._stderr.readlines():
            print line
        print "====================================================================="
        for line in self._stdout.readlines():
            print line
            if line.find("ICMP echo reply")!=-1:
                delta = datetime.datetime.strptime(line.split()[0],"%H:%M:%S.%f")
                pingTimes = pingTimes+1
                microsecond = microsecond + delta.microsecond + delta.second*1000 + delta.minute*60*1000
        return microsecond/pingTimes

class SSHClientLatencySource(SSHClientPlus):
    def __init__(self, hostname, user, password):
        SSHClientPlus.__init__(self,hostname,user,password)
        self.connect()

    def getIPaddressFromHostname(self, hostname):
        self._targetHostname = hostname
        pid,stdin,stdout,stderr = self.execute("ping %s 500 1" %(self._targetHostname))
        line = stdout.readline()
        IPRegex = regex.compile("\d+\.\d+\.\d+\.\d+")
        IPAddress = IPRegex.findall(line)
        if len(IPAddress)!=1:
            return None
        return IPAddress[0]
    def pingTarget(self):
        pid,stdin,stdout,stderr = self.execute("ping %s 500 4" %(self._targetHostname))
        stdout.readlines() # wait for the ping command to finish
        
def testlatency(source, target, targetInternal):
    sshSource = SSHClientLatencySource(source,"root","passw0rd")
    targetIP = sshSource.getIPaddressFromHostname(targetInternal)
    sshTarget = SSHClientLatencyTarget(target,targetIP,"root","passw0rd")
    etherName = sshTarget.startServer()
    if etherName==None:
        return "Error","Unknown",targetIP
    sshSource.pingTarget()
    sshTarget.stopServer()
    return sshTarget.parseLatency(),etherName,targetIP

       

import ConfigParser

class NetworkCfg:
    def __init__(self, filename):
        self._config = ConfigParser.RawConfigParser()
        self._config.read(filename)
        self._jobList = []
        for section in self._config.sections():
            try:
                srcHost = self._config.get(section,"SRC_HOST")
                dstHost = self._config.get(section,"DST_HOST")
            except NoOptionError:
                print "Error parsing section",section
                continue
            try:
                dstHostInternal = self._config.get(section,"DST_HOST_INTERNAL")
            except NoOptionError:
                dstHostInternal = dstHost
            self._jobList.append((section,srcHost,dstHost,dstHostInternal))
    def getJobList(self,):
        return self._jobList

        
if __name__ == '__main__':
    tableContent = []
    tableHeader = ["source","target","Ethernet","IP","Latency (micro-second)"]
    cfg = NetworkCfg("network.cfg")
    for (section,source,target,targetInternal) in cfg.getJobList():
        latency,etherName,targetIP = testlatency(source,target,targetInternal)
        tableContent.append([source,target,etherName,targetIP,latency])
    print tabulate.tabulate(tableContent,headers=tableHeader,tablefmt="orgtbl")
