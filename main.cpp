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

//ע�����.lib��
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

//����ˣ�������socket
	//��ʼ��WSA
	WORD sockVersion = MAKEWORD(2, 2);
	WSADATA wsaData;
	if (WSAStartup(sockVersion, &wsaData) != 0)
	{
		return 0;
	}

	//�����׽���
	SOCKET slisten = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP); //TCP
	if (slisten == INVALID_SOCKET)
	{
		printf("socket error");
		return 0;
	}

	//��IP�Ͷ˿�
	sockaddr_in sin;
	sin.sin_family = AF_INET;
	sin.sin_port = htons(MYPORT);
	sin.sin_addr.S_un.S_addr = inet_addr(MYIP);
	if (bind(slisten, (LPSOCKADDR)&sin, sizeof(sin)) == SOCKET_ERROR)
	{
		printf("bind error");
		return 0;
	}

	//��ʼ����
	if (listen(slisten, MAX_CONNECT_NUM) == SOCKET_ERROR)
	{
		printf("listen error");
		return 0;
	}

	//ȷ������
	SOCKET sClient; //�ͻ��˾��
	sockaddr_in remoteAddr; //���ӵĿͻ���IP��ַ
	int nAddrlen = sizeof(remoteAddr);
	printf("�ȴ�����...\n");

	sClient = accept(slisten, (SOCKADDR *)&remoteAddr, &nAddrlen);
	if (sClient == INVALID_SOCKET)
	{
		printf("accept error");
		return 0;
	}

	printf("���յ�һ�����ӣ�%s \r\n", inet_ntoa(remoteAddr.sin_addr));
	StrExcep *Exception = (StrExcep*)malloc(sizeof(StrExcep)); //Exception �ṹ��

	int needSend = sizeof(StrExcep); //�ṹ�峤��
	char *sendData = (char*)malloc(needSend); //������������char����
	std::cout << "Exception_length: " << sizeof(Exception) << std::endl;
    /*Regular Operation srart*/
    InitAllModules();  //��ʼ������ģ�飬��Ҫ�ڳ������ڴ����øú���
    error = ResChassisAdd(RES_CHASSIS_TYPE_220, 0xC0A86CB4, &ulChassisId); //���һ���ͺ�δRES_CHASSIS_TYPE_220, ����IP��ַΪ192.168.108.180�Ļ���
    if (error != 0) {
        std::cout << "Error Code: " << error << std::endl;
        exit(error);
    }
    error = ResCardAdd(ulChassisId, ulSlotId, RES_CARD_TYPE_V8002F); //�ڻ���ĵ�һ����λ���һ��RES_CARD_TYPE_V8002F�Ľӿڿ�
    if (error != 0) {
        std::cout << "Error Code: " << error << std::endl;
        exit(error);
    }
    std::cout << "Card Added \n" << std::endl;


    error = ResChassisConnect(ulChassisId); //��ָ�����佨��TCP����
    if (error != 0) {
        std::cout << "Error Code: " << error << std::endl;
        exit(error);
    }
    std::cout << "Chassis connected \n" << std::endl;


    error = ResPortReserve(ulChassisId, ulSlotId, ulPortId); //ԤԼָ�������һ��λ�ϵĵ�һ���˿�
    if (error != 0) {
        std::cout << "Error Code: " << error << std::endl;
        exit(error);
    }
	error = ResPortReserve(ulChassisId, ulSlotId, ulPortId_v1); //ԤԼָ�������һ��λ�ϵĵڶ����˿�
	if (error != 0) {
		std::cout << "Error Code: " << error << std::endl;
		exit(error);
	}
    std::cout << "Port Reserved \n" << std::endl;

    error = TraEnablePort(ulChassisId, ulSlotId, ulPortId, TRUE); //ʹ��ָ�������һ��λ�ϵ�һ���˿ڵ������͹���
    if (error != 0) {
        std::cout << "Error Code: " << error << std::endl;
        exit(error);
    }
    std::cout << "Stream send enabled \n" << std::endl;
    /*Regular Operation end*/

    /*Setup start*/
    error = TraSetPortTransmitMode(ulChassisId, ulSlotId, ulPortId, TRA_TX_MODE_CONTINUOUS, 0, 0, 0); //��ָֻ�������һ��λ�Ͻӿڿ��ĵ�һ�˿ڵķ���ģʽΪ�������ͣ�������������������������Ч��
    /*
    mode to be select :
    TRA_TX_MODE_CONTINUOUS��ʾ�������ͣ�
    TRA_TX_MODE_SINGLE_BURST��ʾ����ͻ����
    TRA_TX_MODE_MULTI_BURST��ʾ���ͻ��
    TRA_TX_MODE_TIME_BURST��ʾ��ʱ�䷢��
    */ 
    if (error != 0) {
        std::cout << "Error Code: " << error << std::endl;
        exit(error);
    }
    std::cout << "Transmit Mode set \n" << std::endl;

    error = TraSetPortScheduleMode(ulChassisId, ulSlotId, ulPortId, TRA_SCHEDULE_MODE_IFG); //����ָ�������һ��λ�Ͻӿڿ��ĵ�һ�˿ڵ������ȷ�ʽ
    /*
    TRA_SCHEDULE_MODE_IFG�����ڶ˿ڵ��٣�
    TRA_SCHEDULE_MODE_FPS�����������٣�
    */
    if (error != 0) {
        std::cout << "Error Code: " << error << std::endl;
        exit(error);
    }
    std::cout << "Schedule Mode set \n" << std::endl;

	
    error = TraAddStream(ulChassisId, ulSlotId, ulPortId, "s1", TRA_PRO_TYPE_UDP, 1, TRA_LEN_TYPE_FIXED, 1000, 1000, FALSE, TRA_PAY_TYPE_CYCLE, 0x5a,
        0, 0x000001020304, 0x000001020305, 0x01000001, 0x01000002, NULL, NULL); //ָ�������һ��λ�ϵ�һ�˿������һ����s1, ����Ϊipv4���ģ� �̶����ȣ�����Ϊ
	// 1000�ֽڣ�ԴMAC��ַΪ00-00-00-01-02-03-04�� Ŀ��MAC��ַΪ00-00-01-02-03-05; Դipv4��ַΪ1.0.0.1��Ŀ��IPV4��ַΪ1.0.0.2��
    if (error != 0) {
        std::cout << "Error Code: " << error << std::endl;
        exit(error);
    }
	
    error = TraEnableStream("s1", TRUE); //ʹ��s1��
    if (error != 0) {
        std::cout << "Error Code: " << error << std::endl;
        exit(error);
    }
	

    error = TraSetEthernetPortRate(ulChassisId, ulSlotId, ulPortId, TRA_RATE_UNIT_TYPE_FPS, 100000); //����ָ�������һ��λ�Ͻӿڿ��ĵ�һ�˿ڵ�����������Ϊ200000FPS
    if (error != 0) {
        std::cout << "Error Code: " << error << std::endl;
        exit(error);
    }
	
    error = StaSelectStream(ulChassisId, ulSlotId, ulPortId, "s1"); //����s1����ָ�������һ��λ�µ�һ�˿��½���ͳ��
    if (error != 0) {
        std::cout << "Error Code: " << error << std::endl;
        exit(error);
    }
	
	error = StaSelectStream(ulChassisId, ulSlotId, ulPortId_v1, "s1"); //����s1����ָ�������һ��λ�µڶ��˿��½���ͳ��
	if (error != 0) {
		std::cout << "Error Code: " << error << std::endl;
		exit(error);
	}

	std::cout << "StaSelect s1 Stream success" << std::endl;

    error = StaStartPort(ulChassisId, ulSlotId, ulPortId); //��ʼָ�������һ��λ�Ͻӿڿ��ĵ�һ�˿ڵ�ͳ��
    if (error != 0) {
        std::cout << "Error Code: " << error << std::endl;
        exit(error);
    }
	printf("1\n");
	error = StaStartPort(ulChassisId, ulSlotId, ulPortId_v1); //��ʼָ�������һ��λ�Ͻӿڿ��ĵڶ��˿ڵ�ͳ��
	if (error != 0) {
		std::cout << "Error Code: " << error << std::endl;
		exit(error);
	}
	
    TraStart();
    Sleep(5000);
	while (true)
	{
		error = StaGetPortData(ulChassisId, ulSlotId, ulPortId, STA_MEA_TX_FPS, &SendframeRate); //��ȡָ�������һ��λ�Ͻӿڿ��ĵ�һ�˿ڵķ��͵�����֡��ͳ�ƣ������frameRate��
		if (error != 0) {
			std::cout << "Error Code: " << error << std::endl;
			exit(error);
		}
		error = StaGetPortData(ulChassisId, ulSlotId, ulPortId_v1, STA_MEA_RX_FPS, &RecvframeRate); //��ȡָ�������һ��λ�Ͻӿڿ��ĵ�һ�˿ڵķ��͵�����֡��ͳ�ƣ������frameRate��
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
        error = StaGetPortData(ulChassisId, ulSlotId, ulPortId, STA_MEA_TX_FPS, &frameRate); //��ȡָ�������һ��λ�Ͻӿڿ��ĵ�һ�˿ڵķ��͵�����֡��ͳ�ƣ������frameRate��
        if (error != 0) {
            std::cout << "Error Code: " << error << std::endl;
            exit(error);
        }

        std::cout << "Frame rate is " << frameRate<< " frm/sec" << std::endl;
        last = frameRate;

        // Dynamically adjust frame rate 
        error = TraSetEthernetPortRate(ulChassisId, ulSlotId, ulPortId, TRA_RATE_UNIT_TYPE_FPS, i*200000); //����ָ�������һ��λ�ӿڿ��ĵ�һ�˿ڵ�����������Ϊi*200000
        if (error != 0) {
            std::cout << "Error Code: " << error << std::endl;
            exit(error);
        }
        Sleep(1000);
    }*/
    TraStop(); //ֹͣ������
    StaStopPort(ulChassisId, ulSlotId, ulPortId); //ָֹͣ���˿ڵ�ͳ��

    // remember to release the resources
    TraRemoveStream("s1"); //ɾ��ָ������
    ResPortRelease(ulChassisId, ulSlotId, ulPortId); //�ͷ�ָ���Ľӿڿ��Ķ˿�
	DeleteAllModules();//�ͷ�������Դ
    return 0;
}
