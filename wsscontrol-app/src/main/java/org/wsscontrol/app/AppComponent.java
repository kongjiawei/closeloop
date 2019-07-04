/*
 * Copyright 2019-present Open Networking Laboratory
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.wsscontrol.app;

import org.apache.felix.scr.annotations.*;//导入java注解模块
import org.onlab.packet.Ethernet;
import org.onlab.packet.IpPrefix;
import org.onlab.packet.MacAddress;
import org.onlab.packet.TpPort;//以上为导入数据包结构模块
import org.onosproject.core.ApplicationId;
import org.onosproject.core.CoreService;
import org.onosproject.net.*;
import org.onosproject.net.device.DeviceService;
//import org.onosproject.net.flow.*;
import org.onosproject.net.flow.*;
import org.onosproject.net.flow.criteria.Criteria;
import org.onosproject.net.flow.criteria.Criterion;
import org.onosproject.net.flowobjective.DefaultForwardingObjective;
import org.onosproject.net.flowobjective.FlowObjectiveService;
import org.onosproject.net.flowobjective.ForwardingObjective;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.*;
import java.net.InetAddress;
import java.net.ServerSocket;
import java.net.Socket;
//import com.alibaba.fastjson.JSONObject;
//import com.eclipsesource.json.JsonObject;

import com.eclipsesource.json.Json;
import com.eclipsesource.json.JsonObject;
import java.util.concurrent.TimeUnit;


import static org.slf4j.LoggerFactory.getLogger;

/**
 * Skeletal ONOS application component.
 */
@Component(immediate = true)
public class AppComponent {

    @Reference(cardinality = ReferenceCardinality.MANDATORY_UNARY)
    protected CoreService coreService;

    @Reference(cardinality = ReferenceCardinality.MANDATORY_UNARY)
    protected DeviceService deviceService;

    @Reference(cardinality = ReferenceCardinality.MANDATORY_UNARY)
    protected FlowRuleService flowRuleService;

    @Reference(cardinality = ReferenceCardinality.MANDATORY_UNARY)
    protected FlowObjectiveService flowObjectiveService;

    private ApplicationId appId;
    private DeviceId deviceId;
    private static final String APP_TEST = "org.wsscontrol.app";
    private final Logger log = LoggerFactory.getLogger(getClass());

    DeviceId wss66 = DeviceId.deviceId("of:0000000000000066"); //  对应第一个链路
    DeviceId wss64 = DeviceId.deviceId("of:0000000000000064"); // 对应第二个链路
    DeviceId wss62 = DeviceId.deviceId("of:0000000000000062");
    private int flowPriority = 60000;
    private int flowTimeout = 10000;
    Server control_server = new Server();

    @Activate
    protected void activate()  {
       // socket_control();
       // control_server.start();
        log.info("Started");
        appId = coreService.registerApplication(APP_TEST);
        log.info(appId.toString());
        opticalrule(wss66, 131, 8,1);
        opticalrule(wss64, 131,8,1);
        opticalrule(wss64,107,8,2);
        opticalrule(wss62,107,8,1);
        log.info("Wss initialize finished");
        control_server.start();

    }

    @Deactivate
    protected void deactivate() throws IOException {
        flowRuleService.removeFlowRulesById(appId);
        log.info("Stopped");
    }

    private class Server extends Thread {

        ServerSocket sever = null;

        public void run() {

            try {
                int port = 9012;
                int backlog = 10;
                InetAddress addr = InetAddress.getByName("192.168.108.225");
                ServerSocket sever = new ServerSocket(port, backlog, addr);  //绑定IP和端口，backlog表明最大连接数

                log.info("wait for connector\n");
                Socket socket = sever.accept();
                InetAddress address = socket.getInetAddress();
                log.info("IP of connector::" + address.getHostAddress() + '\n');

                InputStream inputStream = null;
                InputStreamReader inputStreamReader = null;
                BufferedReader bufferedReader = null;
                OutputStream outputStream = null;
                PrintWriter printWriter = null;

                byte buf[] =new byte[1024];
                int len=-1;

                while (true) {
                    // 建立好连接后，从socket中获取输入流，并建立缓冲区进行读取

                    inputStream = socket.getInputStream();
                    inputStreamReader = new InputStreamReader(inputStream);
                    bufferedReader = new BufferedReader(inputStreamReader);

                    while ((len = inputStream.read(buf)) > 0) {

                        String info = new String(buf,0,len);
                        log.info("info" + info);
                        JsonObject object = Json.parse(info).asObject();
                        log.info("objcet:" + object);
                        int fault_type = object.get("fault").asInt();
                        int switchid1 = object.get("switchid1").asInt();
                        int switchid2 = object.get("switchid2").asInt();
                        log.info("fault:" + fault_type);
                        log.info("switchid1:" + switchid1);
                        log.info("switchid2:" + switchid2);
                        while ((fault_type == 1) && (switchid1 == 2)) {
                            opticalrule(wss64, 107, 8, 3);
                            fault_type = 0;

                        }

                    }

                }
            } catch (IOException e) {
                e.printStackTrace();

            }

        }
    }


    public void opticalrule(DeviceId device, int start_fs, int bandwidth, int outPortNumber)
    {
        TrafficSelector.Builder selectorBuilder = DefaultTrafficSelector.builder();
        selectorBuilder.add(Criteria.matchLambda(new OchSignal(GridType.FLEXLast, ChannelSpacing.CHL_12P5GHZ, start_fs, bandwidth)));// center frequency:193.1THz
        TrafficTreatment treatment = DefaultTrafficTreatment.builder().setOutput(PortNumber.portNumber(outPortNumber)).build();
        ForwardingObjective forwardingObjective = DefaultForwardingObjective.builder()
                .withSelector(selectorBuilder.build())
                .withTreatment(treatment)
                .withPriority(flowPriority)
                .withFlag(ForwardingObjective.Flag.VERSATILE)
                .fromApp(appId)
                .makePermanent()
                .add();

        log.info("send rules"); // send rules to the devices

        flowObjectiveService.forward(device,forwardingObjective);
        log.info("send rule successfully");

    }
}

