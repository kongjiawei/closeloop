#smartnic
import threading
from threading import Semaphore
import telnetlib
import sys
#tofino
import threading
from threading import Semaphore
import time
import select
import os
import os
import sys
import struct
import socket
import math
import signal
sys.path.append('/home/sdn/bf-sde-4.1.1.15/install/lib/python2.7/site-packages')
import os
import subprocess
import re
import time
from multiprocessing import Process
from RTEInterface import RTEInterface
updateOpticalEntry_sema = Semaphore(1)
host = "192.168.108.50"
port = '20206'

def updateOpticalEntries(power,power_flag,osnr,osnr_flag):
    action_power = '{  "type" : "int_set_header_switch_id_and_power",  "data" : { "power" : { "value" : ' + '\"' + str(power) + '\"' + ' }, "flag" : { "value" : ' + '\"' + str(power_flag) + '\"' + ' } } }'
    #tbl_id_power = RTEInterface.Tables.ResolveToTableId('tbl_int_instance_set_switch_id_and_power')
    RTEInterface.Tables.EditRule(tbl_id=5,
    rule_name="a", default_rule=True, match=None, actions=action_power)
    print 'power',power
    action_osnr = '{  "type" : "int_set_header_switch_id_and_osnr",  "data" : { "osnr" : { "value" : ' + '\"' + str(osnr) + '\"' + ' }, "flag" : { "value" : ' + '\"' + str(osnr_flag) + '\"' + ' } } }'
    print 'osnr',osnr
    #tbl_id_osnr = RTEInterface.Tables.ResolveToTableId('tbl_int_instance_set_switch_id_and_osnr')
    RTEInterface.Tables.EditRule(tbl_id=4, rule_name="a", default_rule=True, match=None, actions=action_osnr)

def get(s):
    t1, flag = str2int(s)

    return t1 * (-1 if flag == 1 else 1)
def str2int(s):
    flag = 0
    if s[0] == '-':
        flag = 1
        return float(s[1:len(s)]), flag
    elif s[0] == '+':
        flag = 0

        return float(s[1:len(s)]), flag
    else:
        return float(s),flag
f = lambda x: 0 if x >= 0 else 1


def ocm():
    """
    0x0 (never appera)
    0x1 (centerfer,)
    0x2 (centerfer,bandwitdh)
    0x3 (centerfer,bandwitdh,channels)
    sleep for thread scheduling
    """
    s_optical = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_optical.connect(('192.168.108.239', 8888))
    #print "Connect to the OCM.................... \n"
    TLV1 = [3,2]
    TLV2 = [19340,100,1,0,0,0]
    flag = 1
    try:
        while not is_exit:
            buffer = []
            #print 'ready to send\n'
            s_optical.send(struct.pack('%si'%len(TLV1),*TLV1))
            s_optical.send(struct.pack('%si'%len(TLV2),*TLV2))
            #print 'send success\n'

            while not is_exit:
                d = s_optical.recv(32)
                time.sleep(0.1)
                if d != 'end':
                    #print str(bytes(d))
                    receive = struct.unpack('%sd'%TLV1[1]*2, d)
                    buffer.append(receive)
                    #print buffer
                else:
                    #print d
                    break
            l = len(buffer)
            for i in range(0,l,1):
                power_0, osnr_0 = buffer[i][0],buffer[i][1]
                power_0 = power_0 + 10*math.log10(19)
                print 'OCM\n'
                print power_0
                print osnr_0
                #print int(abs(round(power_0*10))),int(abs(round(osnr_0*10)))
                #print int(abs(round(power_0*10))),int(abs(round(osnr_0*10)))
                global power_ocm
                global power_ocm_flag
                global osnr_ocm
                global osnr_ocm_flag
                power_ocm = int(abs(round(power_0 * 10)))
                power_ocm_flag = f(power_0)
                osnr_ocm = int(abs(round(osnr_0*10)))
                osnr_ocm_flag = f(osnr_0)
                #print 'ocm_power',power_ocm
                #print 'ocm_osnr',osnr_ocm

                time.sleep(0.1)

                with updateOpticalEntry_sema:
                    updateOpticalEntries(
                                     power_ocm, power_ocm_flag,
                                     osnr_ocm,osnr_ocm_flag,
                                     )
    finally:
        s_optical.close()


def osa():
    import math
    p = re.compile('\s*-?[0-9]+\.[0-9]+E[+-][0-9]+')
    tn = telnetlib.Telnet('192.168.108.205', port=5024, timeout=10)
    result = tn.read_until("READY>")
    #print result
    tn.write(('CLOSE LINS10\n').encode('ascii'))
    tn.write('CONNECT LINS10\n'.encode('ascii'))
    time.sleep(1)
    tn.write('LINS10:SENS:WAV:STAR 1540.11 NM\n'.encode('ascii'))
    tn.write('LINS10:SENS:WAV:STOP 1565.11 NM\n'.encode('ascii'))
    tn.write('LINS10:STAT?\n'.encode('ascii'))
    tn.write('LINS10:INIT:IMM\n'.encode('ascii'))

    tn.write('LINS10:STAT:OPER:BIT8:COND?\n'.encode('ascii'))
    time.sleep(0.5)#wait for the cond become to 0
    tn.write('LINS10:STAT:OPER:BIT8:COND?\n'.encode('ascii'))
    tn.write('LINS10:CALC:WDM:DATA:CHAN:NSEL 32\n'.encode('ascii'))
    tn.write('LINS10:CALC:WDM:DATA:CHAN:CENT:WAV?\n'.encode('ascii'))
    time.sleep(0.5)
    result = tn.read_very_eager()
    #print result
    try:
        while True:
            tn.write('LINS10:CALC:WDM:DATA:CHAN:SIGP?\n'.encode('ascii'))
            time.sleep(0.1)
            result = tn.read_very_eager()

            a = get(p.findall(result.encode('utf-8'))[0])

            #print 'osa_power', int(round(a + 10 * math.log10(19)) * 10)
            global power_osa
            global power_osa_flag
            global osnr_osa
            global osnr_osa_flag
            global updateOpticalEntry_sema
            #print 'OSA\n'
            #print a + 10 * math.log10(19)
            power_osa = abs(int(
                round(
                    (a + 10 * math.log10(19))*10)))
            power_osa_flag = f(a + 10 * math.log10(19))
            tn.write('LINS10:CALC:WDM:DATA:CHAN:OSNR?\n'.encode('ascii'))
            time.sleep(0.1)
            result = tn.read_very_eager()
            a = get(p.findall(result.encode('utf-8'))[0])
            #print 'osa_osnr', int(round(a * 10))
            #print a
            osnr_osa = abs(int(round(a * 10)))
            osnr_osa_flag = f(a)
            #time.sleep(1)
            #RTEInterface.Registers.Clear('ext_poll_reg', 0, 1)
            with updateOpticalEntry_sema:

                updateOpticalEntries(power=power_osa,power_flag=power_osa_flag,osnr=osnr_osa,osnr_flag=osnr_osa_flag)

    finally:
        tn.close()


is_exit = False
def handler():
    global is_exit
    is_exit = True

if __name__ == '__main__':
    lastCount = [0,0,0,0]
    nowcount = [0,0,0,0]
    RTEInterface.Connect(host,port)
    #print RTEInterface.Registers.List()
    print RTEInterface.Tables.List()
    #print RTEInterface.Tables.ListRules(5)
    #print  RTEInterface.Tables.ListRules(7)

    #action = '{  "type" : "int_set_header_switch_id_and_osnr",  "data" : { "osnr" : { "value" : ' + '\"' + str(40) + '\"' + ' }, "flag" : { "value" : ' + '\"' + str(1) + '\"' + ' } } }'
    #print action
    #action = '{  "type" : "int_set_header_switch_id_and_osnr",  "data" : { "osnr" : { "value" : "40" }, "flag" : { "value" : "1" } } }'
    #print  action
    # RTEInterface.Tables.EditRule(tbl_id=5,
    #                              rule_name="a", default_rule=True, match=None, actions=action)
    #print RTEInterface.Tables.ListRules(5)
    #val = [0 for i in range(1,16)]
    reg = 'flow_counter'
    reused = [1,1,1,1]
    for i in range(4):
        nowcount[i] = RTEInterface.Registers.Get(reg,i,0)
        #print nowcount
        if lastCount[i]  == nowcount[i]:
            reused[i] = 1;



    try:
        #nowCount = RTEInterface.Counters.GetP4Counter(RTEInterface.Counters.GetP4CounterByName('pkt_counter_bytes').id)
        #rate = (nowCount - lastCount) / (1)
        #RTEInterface.Tables.EditRule(table_id,rule_name,default_rule,match,action)
        #print 'nic rate = ',rate
        #lastCount = nowCount

        t_osa = threading.Thread(target=osa, name='cm', args=())
        #t_ocm = threading.Thread(target=ocm,name='ocm',args=())

        t_osa.setDaemon(True)
        #t_ocm.setDaemon(True)

        #t_ocm.start()
        t_osa.start()

        while True:
           alive = False
           alive = alive or t_osa.isAlive()
           if not alive:
               break
        # while True:
        #     # RTEInterface.Registers.Set('reg_1',val,0,15)
        #     # RTEInterface.Registers.Set('reg_2',val,0,15)
        #     # RTEInterface.Registers.Set('reg_3',val,0,15)
        #     # print RTEInterface.Registers.Get('reg_3',0,16)
        #     # print RTEInterface.Registers.Get('reg_2',0,16)
        #     # print RTEInterface.Registers.Get('reg_1',0,16)
        #     # RTEInterface.Registers.Clear('flowlet_timestamp_reg_2',0,16)
        #     # RTEInterface.Registers.Clear('flowlet_timestamp_reg_1',0,16)
        #     print RTEInterface.Registers.Get('ext_poll_reg',0,1)
        #
        #     RTEInterface.Registers.Clear('ext_poll_reg',0,1)
        #     #RTEInterface.Registers.Clear('flowlet_route_reg_1',0,16)
        #     print RTEInterface.Registers.Get('ext_poll_reg',0,1)
        #     time.sleep(20)
        # print RTEInterface.Registers.Get('flowlet_route_reg_1',0,16)
        # print RTEInterface.Registers.Get('flowlet_timestamp_reg_2',0,16)
        # print RTEInterface.Registers.Get('flowlet_timestamp_reg_1',0,16)

        # while True:
        #     time.sleep(1)
        # while True:
        #
        #     #RTEInterface.Registers.Clear('ext_poll_reg', 0, 1)
        #     #RTEInterface.Registers.Clear('int_poll_reg', 0, 1)
        #     #time.sleep(10)



    finally:
        RTEInterface.Disconnect()






