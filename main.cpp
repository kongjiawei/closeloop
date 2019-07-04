#include<afxtempl.h>
#include <atlstr.h>
#include "TeleApi.h"
#include<iostream>
#include<winsock2.h>
#include<stdio.h>
//#include "stdafx.h"
#pragma comment(lib, "ws2_32.lib")

#define MYPORT 8888
#define MYIP "192.168.108.25"
#define MAX_CONNECT_NUM 10

typedef struct {
	int excep;
}StrExcep;

//注意添加.lib库
int main() {

    ULONG error = 1;
    ULONG ulChassisId = 0;
    ULONG ulSlotId = 2;
    ULONG ulPortId = 1;
	ULONG ulPortId_v1 = 2;
    UINT64 SendframeRate = 0;
	UINT64 RecvframeRate = 0;
   // UINT64 last = 0;
	float ratio = 0.9; 
  //  int i = 1;

//服务端，先连接socket
	//初始化WSA
	WORD sockVersion = MAKEWORD(2, 2);
	WSADATA wsaData;
	if (WSAStartup(sockVersion, &wsaData) != 0)
	{
		return 0;
	}

	//创建套接字
	SOCKET slisten = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP); //TCP
	if (slisten == INVALID_SOCKET)
	{
		printf("socket error");
		return 0;
	}

	//绑定IP和端口
	sockaddr_in sin;
	sin.sin_family = AF_INET;
	sin.sin_port = htons(MYPORT);
	sin.sin_addr.S_un.S_addr = inet_addr(MYIP);
	if (bind(slisten, (LPSOCKADDR)&sin, sizeof(sin)) == SOCKET_ERROR)
	{
		printf("bind error");
		return 0;
	}

	//开始监听
	if (listen(slisten, MAX_CONNECT_NUM) == SOCKET_ERROR)
	{
		printf("listen error");
		return 0;
	}

	//确认连接
	SOCKET sClient; //客户端句柄
	sockaddr_in remoteAddr; //连接的客户端IP地址
	int nAddrlen = sizeof(remoteAddr);
	printf("等待连接...\n");

	sClient = accept(slisten, (SOCKADDR *)&remoteAddr, &nAddrlen);
	if (sClient == INVALID_SOCKET)
	{
		printf("accept error");
		return 0;
	}

	printf("接收到一个连接：%s \r\n", inet_ntoa(remoteAddr.sin_addr));
	StrExcep *Exception = (StrExcep*)malloc(sizeof(StrExcep)); //Exception 结构体

	int needSend = sizeof(StrExcep); //结构体长度
	char *sendData = (char*)malloc(needSend); //发送数据需是char类型
	std::cout << "Exception_length: " << sizeof(Exception) << std::endl;
    /*Regular Operation srart*/
    InitAllModules();  //初始化所有模块，需要在程序的入口处调用该函数
    error = ResChassisAdd(RES_CHASSIS_TYPE_220, 0xC0A86CB4, &ulChassisId); //添加一个型号未RES_CHASSIS_TYPE_220, 网口IP地址为192.168.108.180的机箱
    if (error != 0) {
        std::cout << "Error Code: " << error << std::endl;
        exit(error);
    }
    error = ResCardAdd(ulChassisId, ulSlotId, RES_CARD_TYPE_V8002F); //在机箱的第一个槽位添加一块RES_CARD_TYPE_V8002F的接口卡
    if (error != 0) {
        std::cout << "Error Code: " << error << std::endl;
        exit(error);
    }
    std::cout << "Card Added \n" << std::endl;


    error = ResChassisConnect(ulChassisId); //和指定机箱建立TCP连接
    if (error != 0) {
        std::cout << "Error Code: " << error << std::endl;
        exit(error);
    }
    std::cout << "Chassis connected \n" << std::endl;


    error = ResPortReserve(ulChassisId, ulSlotId, ulPortId); //预约指定机箱第一槽位上的第一个端口
    if (error != 0) {
        std::cout << "Error Code: " << error << std::endl;
        exit(error);
    }
	error = ResPortReserve(ulChassisId, ulSlotId, ulPortId_v1); //预约指定机箱第一槽位上的第二个端口
	if (error != 0) {
		std::cout << "Error Code: " << error << std::endl;
		exit(error);
	}
    std::cout << "Port Reserved \n" << std::endl;

    error = TraEnablePort(ulChassisId, ulSlotId, ulPortId, TRUE); //使能指定机箱第一槽位上第一个端口的流发送功能
    if (error != 0) {
        std::cout << "Error Code: " << error << std::endl;
        exit(error);
    }
    std::cout << "Stream send enabled \n" << std::endl;
    /*Regular Operation end*/

    /*Setup start*/
    error = TraSetPortTransmitMode(ulChassisId, ulSlotId, ulPortId, TRA_TX_MODE_CONTINUOUS, 0, 0, 0); //这只指定机箱第一槽位上接口卡的第一端口的发送模式为连续发送，后面三个参数对连续发送无效。
    /*
    mode to be select :
    TRA_TX_MODE_CONTINUOUS表示连续发送，
    TRA_TX_MODE_SINGLE_BURST表示单次突发，
    TRA_TX_MODE_MULTI_BURST表示多次突发
    TRA_TX_MODE_TIME_BURST表示按时间发送
    */ 
    if (error != 0) {
        std::cout << "Error Code: " << error << std::endl;
        exit(error);
    }
    std::cout << "Transmit Mode set \n" << std::endl;

    error = TraSetPortScheduleMode(ulChassisId, ulSlotId, ulPortId, TRA_SCHEDULE_MODE_IFG); //设置指定机箱第一槽位上接口卡的第一端口的流调度方式
    /*
    TRA_SCHEDULE_MODE_IFG（基于端口调速）
    TRA_SCHEDULE_MODE_FPS（基于流调速）
    */
    if (error != 0) {
        std::cout << "Error Code: " << error << std::endl;
        exit(error);
    }
    std::cout << "Schedule Mode set \n" << std::endl;

	
    error = TraAddStream(ulChassisId, ulSlotId, ulPortId, "s1", TRA_PRO_TYPE_UDP, 1, TRA_LEN_TYPE_FIXED, 1000, 1000, FALSE, TRA_PAY_TYPE_CYCLE, 0x5a,
        0, 0x000001020304, 0x000001020305, 0x01000001, 0x01000002, NULL, NULL); //指定机箱第一槽位上第一端口下添加一个流s1, 该流为ipv4报文， 固定长度，长度为
	// 1000字节，源MAC地址为00-00-00-01-02-03-04； 目的MAC地址为00-00-01-02-03-05; 源ipv4地址为1.0.0.1，目的IPV4地址为1.0.0.2。
    if (error != 0) {
        std::cout << "Error Code: " << error << std::endl;
        exit(error);
    }
	
    error = TraEnableStream("s1", TRUE); //使能s1流
    if (error != 0) {
        std::cout << "Error Code: " << error << std::endl;
        exit(error);
    }
	

    error = TraSetEthernetPortRate(ulChassisId, ulSlotId, ulPortId, TRA_RATE_UNIT_TYPE_FPS, 100000); //设置指定机箱第一槽位上接口卡的第一端口的流发送速率为200000FPS
    if (error != 0) {
        std::cout << "Error Code: " << error << std::endl;
        exit(error);
    }
	
    error = StaSelectStream(ulChassisId, ulSlotId, ulPortId, "s1"); //把流s1挂在指定机箱第一槽位下第一端口下进行统计
    if (error != 0) {
        std::cout << "Error Code: " << error << std::endl;
        exit(error);
    }
	
	error = StaSelectStream(ulChassisId, ulSlotId, ulPortId_v1, "s1"); //把流s1挂在指定机箱第一槽位下第二端口下进行统计
	if (error != 0) {
		std::cout << "Error Code: " << error << std::endl;
		exit(error);
	}

	std::cout << "StaSelect s1 Stream success" << std::endl;

    error = StaStartPort(ulChassisId, ulSlotId, ulPortId); //开始指定机箱第一槽位上接口卡的第一端口的统计
    if (error != 0) {
        std::cout << "Error Code: " << error << std::endl;
        exit(error);
    }
	printf("1\n");
	error = StaStartPort(ulChassisId, ulSlotId, ulPortId_v1); //开始指定机箱第一槽位上接口卡的第二端口的统计
	if (error != 0) {
		std::cout << "Error Code: " << error << std::endl;
		exit(error);
	}
	
    TraStart();
    Sleep(5000);
	while (true)
	{
		error = StaGetPortData(ulChassisId, ulSlotId, ulPortId, STA_MEA_TX_FPS, &SendframeRate); //获取指定机箱第一槽位上接口卡的第一端口的发送的流的帧数统计，结果在frameRate中
		if (error != 0) {
			std::cout << "Error Code: " << error << std::endl;
			exit(error);
		}
		error = StaGetPortData(ulChassisId, ulSlotId, ulPortId_v1, STA_MEA_RX_FPS, &RecvframeRate); //获取指定机箱第一槽位上接口卡的第一端口的发送的流的帧数统计，结果在frameRate中
		if (error != 0) {
			std::cout << "Error Code: " << error << std::endl;
			exit(error);
		}
		std::cout << "SendframeRate: " << SendframeRate << "  RecvframeRate: "<< RecvframeRate << std::endl;
		if(RecvframeRate < SendframeRate * ratio)
		{
			Exception->excep = 1;
			std::cout << "Exception: " << Exception->excep << std::endl;
			memcpy(sendData, Exception, needSend);
			int length = send(sClient, sendData, needSend, 0);
			if (length < 0)
			{
				printf("Server Transmit Data Failed!\n");
				return 0;
			}
			Sleep(1000);
		}
		else 
		{
			Exception->excep = 0;
			std::cout << "Exception: " << Exception->excep << std::endl;
		/*	memcpy(sendData, Exception, needSend);
			int length = send(sClient, sendData, needSend, 0);
			if (length < 0)
			{
				printf("Server Transmit Data Failed!\n");
				return 0;
			}*/
		}
		

	}

   /* for (int i = 2; i <= 10; i++) {
        error = StaGetPortData(ulChassisId, ulSlotId, ulPortId, STA_MEA_TX_FPS, &frameRate); //获取指定机箱第一槽位上接口卡的第一端口的发送的流的帧数统计，结果在frameRate中
        if (error != 0) {
            std::cout << "Error Code: " << error << std::endl;
            exit(error);
        }

        std::cout << "Frame rate is " << frameRate<< " frm/sec" << std::endl;
        last = frameRate;

        // Dynamically adjust frame rate 
        error = TraSetEthernetPortRate(ulChassisId, ulSlotId, ulPortId, TRA_RATE_UNIT_TYPE_FPS, i*200000); //设置指定机箱第一槽位接口卡的第一端口的流发送速率为i*200000
        if (error != 0) {
            std::cout << "Error Code: " << error << std::endl;
            exit(error);
        }
        Sleep(1000);
    }*/
    TraStop(); //停止流发送
    StaStopPort(ulChassisId, ulSlotId, ulPortId); //停止指定端口的统计

    // remember to release the resources
    TraRemoveStream("s1"); //删除指定的流
    ResPortRelease(ulChassisId, ulSlotId, ulPortId); //释放指定的接口卡的端口
	DeleteAllModules();//释放所有资源
    return 0;
}
