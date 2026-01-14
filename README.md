# Edge to Cloud Real-time Monitoring Demo

## 1. 项目简介
本项目模拟嵌入式设备在边缘侧采集传感器数据，
通过 Kafka 将数据发送到云端，并使用 Flink 进行实时异常检测，
用于展示边缘计算与云端实时处理的完整数据链路。

## 2. 技术栈
- Python：模拟嵌入式设备数据采集
- Kafka：设备数据消息队列
- Flink（PyFlink）：实时流处理与异常检测
- Docker Compose：组件统一部署

## 3. 系统架构
设备模拟程序
↓
Kafka（sensor-data topic）
↓
Flink 实时计算
↓
异常数据输出 / 告警（可扩展）

## 4. 功能说明
- 模拟设备周期性上报温度数据
- 通过 Kafka 解耦设备与计算模块
- 实时检测温度异常（阈值 > 80）
- 输出异常设备数据
- 实时异常设备数据会写入 Redis，用于告警状态存储

## 5. 项目结构
edge-cloud-demo/
├── edge/ # 边缘侧设备模拟
│ └── sensor_simulator.py
├── flink/ # 实时计算任务
│ └── temperature_alert_job.py
├── docker-compose.yml # Kafka 环境部署
└── README.md

## 6. 运行方式（可选）
```bash
docker-compose up
pip install kafka-python
python edge/sensor_simulator.py


7. 可扩展方向

-接入真实嵌入式设备或 MCU
-使用 Redis / 数据库保存告警状态
-接入可视化监控系统（如 Grafana）
-增加设备故障预测模型
