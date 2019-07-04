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
sys.path.extend(['../p4testutils','../tofino','../tofinopd','../'])
from thriftutils import *
import pd_base_tests
import bf_switchd_dev_status
#
import telnetlib
import time
from encodings import *
import re
from pltfm_pm_rpc.ttypes import *
from int_poll.p4_pd_rpc.ttypes import *
from res_pd_rpc.ttypes import *
source = 0
meter = 0
optical = 0
color_green = 0
color_yellow = 1
color_red = 3
#ver = 1
ver = 1
centerfer2port = {
    50 : 0,
    100 : 160
}
updateOpticalEntry_sema = Semaphore(1)
def installOpticalEntries(client,sess_hdl,dev_tgt):
    match_spec = int_tbl_int_instance_set_optical_data_match_spec_t(ig_intr_md_ingress_port=160)
    action_spec_data = int_int_set_header_optical_data_action_spec_t(action_power_ocm=1,action_power_ocm_flag=0,
                                                                      action_osnr_ocm=1,action_osnr_ocm_flag=0,
                                                                     action_power_osa=2,action_power_osa_flag=0,
                                                                     action_osnr_osa=2,action_osnr_osa_flag=0)
    client.tbl_int_instance_set_optical_data_table_add_with_int_set_header_optical_data(sess_hdl=sess_hdl,
                                                                                        dev_tgt=dev_tgt,
                                                                                        match_spec=match_spec,
                                                                                        action_spec=action_spec_data)

def updateOpticalEntries(client,sess_hdl,dev_tgt,power,power_flag,osnr,osnr_flag):
    #port = centerfer2port[centerfer]
    #match_spec = int_tbl_int_instance_set_optical_data_match_spec_t(ig_intr_md_ingress_port=160)

    if power is not None and osnr is not None:
        #print 'power_ocm / power_osa', power_ocm,osnr_osa
        # action_spec_data = int_int_set_header_optical_data_action_spec_t(action_power_ocm=power_ocm,
        #                                                                  action_power_ocm_flag=power_ocm_flag,
        #                                                                  action_osnr_ocm=osnr_ocm,
        #                                                                  action_osnr_ocm_flag=osnr_ocm_flag,
        #                                                                  action_power_osa=power_osa,
        #                                                                  action_power_osa_flag=power_osa_flag,
        #                                                                  action_osnr_osa=osnr_osa,
        #                                                                  action_osnr_osa_flag=osnr_osa_flag)
        # client.tbl_int_instance_set_optical_data_table_modify_with_int_set_header_optical_data_by_match_spec(sess_hdl=sess_hdl,
        #                                                                                                      dev_tgt=dev_tgt,
        #                                                                                                      match_spec=match_spec,
        #                                                                                                      action_spec=action_spec_data)
        #

        # client.tbl_int_instance_set_switch_id_and_osnr_set_default_action_int_set_header_switch_id_and_osnr(
        #     dev_tgt=dev_tgt, sess_hdl=sess_hdl,
        #     action_spec=int_int_set_header_switch_id_and_osnr_action_spec_t(action_osnr=osnr, action_flag=osnr_flag)
        # )
        # client.tbl_int_instance_set_switch_id_and_power_set_default_action_int_set_header_switch_id_and_power(
        #     dev_tgt=dev_tgt, sess_hdl=sess_hdl,
        #     action_spec=int_int_set_header_switch_id_and_power_action_spec_t(action_power=power, action_flag=power_flag)
        # )

        client.tbl_int_instance_set_power_set_default_action_int_set_header_optical_power(dev_tgt=dev_tgt,
                                                                                          sess_hdl=sess_hdl,
                                                                                          action_spec=int_poll_int_set_header_optical_power_action_spec_t(
                                                                                              action_power=power,
                                                                                              action_flag=power_flag))
        client.tbl_int_instance_set_osnr_set_default_action_int_set_header_optical_osnr(dev_tgt=dev_tgt,
                                                                                        sess_hdl=sess_hdl,
                                                                                        action_spec=int_poll_int_set_header_optical_osnr_action_spec_t(
                                                                                            action_osnr=osnr,
                                                                                            action_flag=osnr_flag));







def installEntries(client,sess_hdl,dev_tgt):
    if meter:
        meter_idx = 0
        global color_green
        global color_yellow
        global color_red
        global ver


        match_spec_0 = int_tbl_meter_policy_match_spec_t(color_red)

        meter_0_spec = int_bytes_meter_spec_t(10000000, 200000, 20000000, 400000, False)
        client.meter_set_meter_0(sess_hdl, dev_tgt, meter_idx, meter_0_spec)
        print "Adding entry"
        entry_hdl_2 = client.tbl_meter_policy_table_add_with_do_drop(sess_hdl, dev_tgt, match_spec_0)

    match_spec_1 = int_poll_tbl_forward_match_spec_t(
        ipv4Addr_to_i32("1.0.0.1"),
        24
    )
    for i in range(4):
        if used[i] == 0:

            client.tbl_forward_table_add_with_do_forward(sess_hdl=sess_hdl, dev_tgt=dev_tgt,
                                                 match_spec=match_spec_1,
                                                 action_spec=int_poll_do_forward_action_spec_t(action_espec=36,
                                                                                          action_int_idx=i))
            used[0] = 1
            break

    # match_spec_2 = int_tbl_forward_match_spec_t(
    #     ipv4Addr_to_i32('10.0.1.1')
    #     ,24)
    #
    # client.tbl_forward_table_add_with_do_forward(sess_hdl=sess_hdl, dev_tgt=dev_tgt,
    #                                              match_spec= match_spec_2,
    #                                              action_spec=int_do_forward_action_spec_t(action_espec=160,action_idx=1))
    #
    # match_spec_3 = int_tbl_forward_match_spec_t(
    #     ipv4Addr_to_i32('192.168.1.0')
    #     ,24)
    #
    # client.tbl_forward_table_add_with_do_forward(sess_hdl=sess_hdl, dev_tgt=dev_tgt,
    #                                              match_spec= match_spec_3,
    #                                              action_spec=int_do_forward_action_spec_t(action_espec=160,action_idx=2))
    #
    # match_spec_3 = int_tbl_forward_match_spec_t(
    #     ipv4Addr_to_i32('192.168.0.0')
    #     , 24)
    #
    # client.tbl_forward_table_add_with_do_forward(sess_hdl=sess_hdl, dev_tgt=dev_tgt,
    #                                              match_spec=match_spec_3,
    #                                              action_spec=int_do_forward_action_spec_t(action_espec=36,
    #                                                                                       action_idx=3))

    if source:
        client.int_instance_insert_header_source_set_default_action_int_set_header(sess_hdl=sess_hdl, dev_tgt=dev_tgt)
        client.int_instance_update_header_source_set_default_action_int_update_header_source(sess_hdl=sess_hdl,
                                                                                             dev_tgt=dev_tgt)

        #client.tbl_set_sampling_rate_set_default_action_set_sampling_rate(sess_hdl=sess_hdl, dev_tgt=dev_tgt,
        #                                                                 action_spec=int_set_sampling_rate_action_spec_t(
        #                                                                     action_rate=1))
        #client.register_write_sampling_cntr(sess_hdl=sess_hdl,dev_tgt=dev_tgt,register_value=0,index=0)
        #client.tbl_sip_sampler_set_default_action_sample(sess_hdl=sess_hdl, dev_tgt=dev_tgt,
        #                                                 action_spec=int_sample_action_spec_t(0))

        #print client.register_read_sampling_cntr(sess_hdl=sess_hdl,dev_tgt=dev_tgt,index=0,flags=None)

        # client.tbl_int_sip_sampler_set_default_action_int_sample(sess_hdl=sess_hdl, dev_tgt=dev_tgt,
        #                                                  action_spec=int_int_sample_action_spec_t(0))
    if ver == 1:
        #client.tbl_int_instance_set_q_occupancy_set_default_action_int_set_header_q_occupancy(dev_tgt=dev_tgt,sess_hdl=sess_hdl)
        #client.tbl_int_instance_set_hop_latency_set_default_action_int_set_header_hop_latency(dev_tgt=dev_tgt,sess_hdl=sess_hdl)
        #client.tbl_int_instance_set_port_id_set_default_action_int_set_header_port_id(dev_tgt=dev_tgt,sess_hdl=sess_hdl)
        client.tbl_int_instance_set_power_set_default_action_int_set_header_optical_power(dev_tgt=dev_tgt,
                                                                                          sess_hdl=sess_hdl,
                                                                                          action_spec=int_poll_int_set_header_optical_power_action_spec_t(action_power=10,action_flag=1))
        client.tbl_int_instance_set_osnr_set_default_action_int_set_header_optical_osnr(dev_tgt=dev_tgt,sess_hdl=sess_hdl,
                                                                                         action_spec=int_poll_int_set_header_optical_osnr_action_spec_t(action_osnr=10,action_flag=1));
        client.tbl_int_instance_set_switch_id_set_default_action_int_set_header_switch_id(dev_tgt=dev_tgt,sess_hdl=sess_hdl)
        client.tbl_get_length_set_default_action_get_length(sess_hdl=sess_hdl, dev_tgt=dev_tgt)
        client.tbl_pkt_length_checker_set_default_action_pkt_length_checking(sess_hdl=sess_hdl,
                                                                             dev_tgt=dev_tgt,
                                                                             action_spec=
                                                                             int_poll_pkt_length_checking_action_spec_t(0))
    if ver == 2:
        #client.tbl_sip_sampler_set_default_action_sample(sess_hdl=sess_hdl, dev_tgt=dev_tgt,
        #                                                 action_spec=int_sample_action_spec_t(0))
        client.tbl_int_instance_set_switch_id_set_default_action_int_set_header_switch_id(dev_tgt=dev_tgt,sess_hdl=sess_hdl)
        client.tbl_int_instance_set_switch_id_and_osnr_set_default_action_int_set_header_switch_id_and_osnr(
            dev_tgt=dev_tgt,sess_hdl=sess_hdl,action_spec=int_int_set_header_switch_id_and_osnr_action_spec_t(action_osnr=20,action_flag=1)
        )
        client.tbl_int_instance_set_switch_id_and_power_set_default_action_int_set_header_switch_id_and_power(
            dev_tgt=dev_tgt, sess_hdl=sess_hdl,
            action_spec=int_int_set_header_switch_id_and_power_action_spec_t(action_power=20, action_flag=1)
        )
        #client.tbl_int_instance_set_switch_id_and_port_id_set_default_action_int_set_header_switch_id_and_port_id(dev_tgt=dev_tgt,sess_hdl=sess_hdl)

        client.tbl_int_instance_set_switch_id_and_latency_set_default_action_int_set_header_switch_id_and_latency(dev_tgt=dev_tgt,sess_hdl=sess_hdl)

class Test(pd_base_tests.ThriftInterfaceDataPlane):
    def __init__(self):
        pd_base_tests.ThriftInterfaceDataPlane.__init__(self,["int_poll"],server='192.168.108.88')

    def setUp(self):
        pd_base_tests.ThriftInterfaceDataPlane.setUp(self)

        self.sess_hdl = self.conn_mgr.client_init()
        self.dev = 0
        self.dev_tgt = DevTarget_t(self.dev, hex_to_i16(0xFFFF))

        print("\nConnected to Device %d, Session %d" % (
            self.dev, self.sess_hdl))
        print "enable ports\n"
        self.setUpPorts()

    def runTest(self):

        installEntries(self.client, self.sess_hdl, self.dev_tgt)
        if optical:
            #installOpticalEntries(self.client,self.sess_hdl,self.dev_tgt)
            with updateOpticalEntry_sema:
                updateOpticalEntries(test.client, test.sess_hdl, test.dev_tgt, 120, 0, 180, 0)

    def tearDown(self):
        self.conn_mgr.complete_operations(self.sess_hdl)
        self.conn_mgr.client_cleanup(self.sess_hdl)
        print("Closed Session %d" % self.sess_hdl)

        pd_base_tests.ThriftInterfaceDataPlane.tearDown(self)

    def enablePort(self, port_id, chann_id, speed):

        self.pltfm_pm.pltfm_pm_port_add(self.dev, port_id, speed,
                                        pltfm_pm_fec_type_t.BF_FEC_TYP_NONE)
        self.pltfm_pm.pltfm_pm_port_an_set(self.dev, port_id, 2)
        self.pltfm_pm.pltfm_pm_port_enable(self.dev, port_id)

    def setUpPorts(self):

        ports_10g = [160,161,162,163,36,37,38,39]
        for port in ports_10g:

            self.enablePort(port, 0, pltfm_pm_port_speed_t.BF_SPEED_10G)


        ports_40g = []
        for port in ports_40g:

            self.enablePort(port, 0, pltfm_pm_port_speed_t.BF_SPEED_40G)


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
def get(s):

    t1, flag = str2int(s)

    return t1*(-1 if flag == 1 else 1)
power_ocm = 0
power_ocm_flag = 0
osnr_ocm = 0
osnr_ocm_flag = 0
power_osa = 0
power_osa_flag = 0
osnr_osa = 0
osnr_osa_flag = 0
f = lambda x : 0 if x >=0 else 1
lastcount = [0,0,0,0]
nowcount = [0,0,0,0]
used = [0,0,0,0]
def reset_INT_arbiter():
    while True:
        time.sleep(100)
        for i in range(4):
            nowcount [i] = client.counter_read_flow_counter(sess_hdl=sess_hdl,dev_tgt=dev_tgt,index=i,flags=0)
            if nowcount[i] == lastcount[i]:
                used[i] = 0
                client.counter_write_flow_counter(sess_hdl=sess_hdl,dev_tgt=dev_tgt,index=i,counter_value=0)
                client.register_read_int_reg(sess_hdl=sess_hdl,dev_tgt=dev_tgt,index=i,flags=0)
                client.register_write_int_reg(sess_hdl=sess_hdl,dev_tgt=dev_tgt,index=i,register_value=0)


def osa():

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
    tn.write('LINS10:CALC:WDM:DATA:CHAN:NSEL 14\n'.encode('ascii'))
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
            print a
            #print 'osa_power', int(round(a + 10 * math.log10(19)) * 10)
            global power_osa
            global power_osa_flag
            global osnr_osa
            global osnr_osa_flag
            #print 'OSA\n'
            #print a + 10 * math.log10(19)
            power_osa = abs(int(
                round(
                    (a + 10 * math.log10(19))*10)))
            power_osa_flag = f(a)
            tn.write('LINS10:CALC:WDM:DATA:CHAN:OSNR?\n'.encode('ascii'))
            time.sleep(0.1)
            result = tn.read_very_eager()
            a = get(p.findall(result.encode('utf-8'))[0])
            #print 'osa_osnr', int(round(a * 10))
            #print a
            osnr_osa = abs(int(round(a * 10)))
            osnr_osa_flag = f(a)
            time.sleep(1)

            with updateOpticalEntry_sema:
                pass
                updateOpticalEntries(test.client, test.sess_hdl, test.dev_tgt,power_ocm,power_ocm_flag,
                                 osnr_ocm,osnr_ocm_flag,
                                 )

    finally:
        tn.close()


is_exit = False
def handler():
    global is_exit
    is_exit = True

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
    TLV2 = [19270,100,1,0,0,0]
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

                time.sleep(1)

                with updateOpticalEntry_sema:
                    updateOpticalEntries(test.client, test.sess_hdl, test.dev_tgt,
                                     power_ocm, power_ocm_flag,
                                     osnr_ocm,osnr_ocm_flag,
                                     )
    finally:
        s_optical.close()



if __name__ == '__main__':
    test = Test()
    bf_switchd_dev_status.check_bf_switchd_dev_status(host="192.168.108.88")
    test.setUp()
    test.runTest()
    signal.signal(signal.SIGTERM,handler)
    signal.signal(signal.SIGINT,handler)

    try:
        pass
        t_osa = threading.Thread(target=osa, name='osa', args=())
        t_ocm = threading.Thread(target=ocm,name='ocm',args=())

        t_osa.setDaemon(True)
        t_ocm.setDaemon(True)
        #
        t_ocm.start()
        #t_osa.start()
        t_poll = threading.Thread(target=reset_INT_arbiter,name='reset_int_arbiter',args=())
        t_poll.setDaemon(True)
        t_poll.start()
        while True:
            alive = False
            alive = alive or t_ocm.isAlive() or t_poll.isAlive() or t_osa.isAlive()
            if not alive:
                break
    finally:

        test.tearDown()








