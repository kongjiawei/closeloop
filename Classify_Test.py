# -*- coding: utf-8 -*-
"""
Created on Tue May 21 17:17:51 2019

@author: 孔嘉伟
"""

from keras.models import load_model
import pandas as pd
import numpy as np
import socket
import struct
#from multiprocessing import Process, Lock, Manager
import json
import time
import threading

'''两个进程，一个收集40服务器上collect的信息，一个收集来自application的异常报告'''

last_time = 0;
datarecv_bigtao_tuple0 = 0
def intsocket(lock, ):
    global IntDataBuffer;
    print('child process:int')
    host_int = '192.168.108.40'
    port_int = 8887
    sock_int = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("wait for int")
    sock_int.connect((host_int, port_int))  # 连接40服务器的客户端
    print("connect int success")

    while (1):
        buffer = [];
        datarecv_int = sock_int.recv(1024)
        datarecv_int = struct.unpack('iiii', datarecv_int)
        #  print('datarecv_int0',datarecv_int);
        buffer.append(list(datarecv_int))
        datarecv_int = sock_int.recv(1024)
        datarecv_int = struct.unpack('iiii', datarecv_int)
        # print('datarecv_int1', datarecv_int);
        buffer.append(list(datarecv_int))
        # print('buffer:', buffer)
        #   print('buffer:', buffer[0][1])
        lock.acquire()  # 加锁
        IntDataBuffer = buffer;
        lock.release()
      #  print("ok")
      #  print("child pro IntData:", IntDatabuffer)


def controlsocket():
    global last_time
    global IntDataBuffer
    global datarecv_bigtao_tuple0
    model = load_model('closeloop' + '.h5')
    print('load model success')
    print("child process controller")
    host_controller = '192.168.108.225'
    port_collector = 9012;
    sock_collector = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
    sock_collector.connect((host_controller, port_collector))
    print("onos connect success")
    '''发送故障类型和定位信息'''
    # send_list = {'fault':1, 'switchid1':2, 'switchid2':3};
    # send_list = json.dumps(send_list);
    # send_list = send_list.encode('utf-8');
    # sock_collector.send(send_list);
    # print("send collector success")
   # while(1):
        #print("datarecv_bigtao_tuple[0]:",datarecv_bigtao_tuple0)
    while(1):
        if (datarecv_bigtao_tuple0 == 1):
            now_time = time.time()
            if (now_time - last_time > 5):  # 防止一直传递故障
                IntDataBuffer = np.array(IntDataBuffer)
            #    print('IntDataBuffer:',IntDataBuffer)
                DataInt = np.delete(IntDataBuffer, 0, axis=1)  # 删除第一列
                predict = model.predict(DataInt)  # 是一个多维0，1数组
                predict_to_value = np.argmax(predict, axis=1)  # 将每一行转化为其最大值的索引
                print(predict_to_value)
                '''进行故障定位'''
                for i in range(len(predict_to_value)):
                    if (predict_to_value[i] > 0):
                        send_control = {'fault': int(predict_to_value[i]), 'switchid1': i + 1,
                                        'switchid2': i + 2};  # 第一个零无作用
                        print('send_control:', send_control)
                        send_control = json.dumps(send_control);
                        send_control = send_control.encode('utf-8');
                        sock_collector.send(send_control);
                        last_time = now_time

if __name__ == '__main__':

    lock = threading.Lock()
    proc = threading.Thread(target=intsocket, args=(lock, ))
    proc.start()
    IntDataBuffer=[]

    proc1 = threading.Thread(target = controlsocket, args=())
    proc1.start();



    # '''连接controller socket'''
    # host_controller = '192.168.108.225'
    # port_collector = 9003;
    # sock_collector = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
    # sock_collector.connect((host_controller, port_collector))
    # print("controller connect success")
    # # from Classify_Training import


    '''连接bigtao socket'''

    host = '192.168.108.25'
    port = 8888
    sock_bigtao = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_bigtao.connect((host, port))
    print('bigtao connect success')

    '''读取测试集的数据'''
    time.sleep(5)
    DataX = []
    DataY = []
    DataX = np.array(DataX)
    DataY = np.array(DataY)

    print('IntDatabuffer:', IntDataBuffer)

    '''载入模型并预测'''

    while(1):
        datarecv_bigtao = sock_bigtao.recv(4)  # 接受的是结构体，需要解析
      #  print("bigtao recv success")
        datarecv_bigtao_tuple = struct.unpack('i', datarecv_bigtao)
        datarecv_bigtao_tuple0 = datarecv_bigtao_tuple[0]# 输出一个tuple，(1)
      #  print("datarecv from application:", datarecv_bigtao_tuple0)
        time.sleep(1)





