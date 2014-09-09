import commands,os,time,urllib2

class Monitor:
    def __init__(self):
        self.__cpu_cores = self.__get_cpu_cores()
        self.__memory_usage = 0
        self.__cpu_usage = 0
        self.__io_usage = 0
        self.__network_rx = 0
        self.__network_tx = 0
        self.__network_rx_speed=0
        self.__network_tx_speed=0
        self.__process_count = 0
        self.__network_face = []
        
    def refresh_usage_info(self):
        status,output = commands.getstatusoutput('top -n 1 -bi')
        if status!=0:
            return -1
        info = output.split('\n')
        
        #cpu usage
        cpu_info = info[2]
        self.monitor_all_cpu_usage(cpu_info)
        
        #io usage
        self.monitor_all_io_usage(cpu_info)
        
        #memory usage
        mem_info = info[3]
        self.monitor_all_memory_usage(mem_info)
        
        #network usage
        self.monitor_all_network_total('eth0')
        self.monitor_all_network_speed('eth0')
        
        #process count
        self.monitor_all_pids_count()
    
    def print_info(self):
        print self.__cpu_cores
        print self.__cpu_usage
        print self.__io_usage
        print self.__memory_usage
        print self.__process_count
        print self.__network_rx_speed
        print self.__network_tx_speed
        self.__get_net_face()
             
    def analyze_system_info(self):
        if self.__cpu_usage>=0.7:
            #indicates high cpu load
            return 1
        if self.__memory_usage>=0.9:
            #indicates high memory load
            return 2
        if self.__io_usage>=0.3:
            #indicates high io load
            return 3
        
        # 0 means the status is OK
        return 0
              
    def __get_cpu_cores(self):
        status,output = commands.getstatusoutput('grep "model name" /proc/cpuinfo | wc -l')
        if status!=0:
            return -1
        return int(output)
    #get the ethernet card information
    def __get_net_face(self):
        status,output = commands.getstatusoutput('ifconfig | grep "Link encap"')
        if status!=0:
            return -1
        cards = [l[0:l.find(' ')].strip() for l in output.split('\n')]
        self.__network_face = cards;
        print self.__network_face
    
    def monitor_all_cpu_usage(self,info):
        cpu_info = info.split(' ')[1:]
        idx = cpu_info.index('id,')
        self.__cpu_usage = 1-(float(cpu_info[idx-1]))/100
        return self.__cpu_usage
    
    #another method for memory usage is using 'free' command and the buffers info
    def monitor_all_memory_usage(self,info):
        mem_info = info.split('  ')[1:4]
        for i in range(len(mem_info)):
            mem_info[i] = mem_info[i].strip()
        used = float(mem_info[1][0:mem_info[1].index(' ')].strip())
        total = float(mem_info[0][0:mem_info[0].index(' ')].strip())
        self.__memory_usage = used/total
        return self.__memory_usage
    
    #wa for CPU, 30% or higher indicates a high overload'
    def monitor_all_io_usage(self,info):
        io_info = info.split(' ')[1:]
        idx = io_info.index('wa,')
        self.__io_usage = float(io_info[idx-1])/100
        return self.__io_usage
    
    def monitor_all_network_total(self,ethernet):
        status,output = commands.getstatusoutput('ifconfig '+ethernet+' | grep bytes')
        if status!=0:
            return -1
        info = output.strip().split(' ')
        rx = info[1].strip()
        tx=info[6].strip()
        self.__network_rx = int(rx[rx.index(':')+1:])
        self.__network_tx = int(tx[tx.index(':')+1:])
    
    def monitor_all_network_speed(self,ethernet):
        self.monitor_all_network_total(ethernet)
        pre_rx = self.__network_rx
        pre_tx = self.__network_tx
        time.sleep(3)
        self.monitor_all_network_total(ethernet)
        #speed in bytes
        diff_rx = self.__network_rx - pre_rx
        diff_tx = self.__network_tx - pre_tx
        self.__network_rx_speed = diff_rx/3
        self.__network_tx_speed = diff_tx/3
    
    def monitor_all_pids_count(self):
        pids = []
        for subdir in os.listdir('/proc'):
            if subdir.isdigit():
                pids.append(subdir)
        self.__process_count = len(pids)
        return self.__process_count
    
    #send a 'overload' signal to the rest server 
    def send_signal(self,rest_server,signal):
        urllib2.urlopen(rest_server+'/'+signal)
        
        

if __name__=='__main__':
    m=Monitor()
    m.refresh_usage_info()
    m.print_info()
    