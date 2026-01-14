# Edge to Cloud Real-time Monitoring System

## 1. 项目背景
在物联网和工业场景中，嵌入式设备会持续产生运行数据。
如果缺乏实时分析与告警机制，设备异常往往无法被及时发现。
本项目通过模拟边缘设备数据采集，构建了一条从设备侧到云端的实时处理与告警链路。

## 2. 项目目标
- 模拟嵌入式设备周期性上报传感器数据
- 构建设备数据到云端的实时传输链路
- 对设备异常状态进行实时检测与告警存储
- 展示边缘计算与云端实时处理的协同方式

## 3. 技术栈
- Python：嵌入式设备数据模拟
- Kafka：设备数据消息队列，解耦数据生产与消费
- Flink（PyFlink）：实时流处理与异常检测
- Redis：异常设备告警状态存储
- Docker Compose：组件统一部署与管理

## 4. 系统架构
边缘设备模拟
↓
Kafka（sensor-data）
↓
Flink 实时处理
↓
Redis 告警存储

## 5. 核心实现说明
- 边缘侧通过 Python 程序模拟设备持续上报温度数据
- Kafka 作为消息队列，缓冲设备数据并解耦上下游模块
- Flink 实时消费 Kafka 数据，对温度超过阈值（>80）的设备判定为异常
- 异常设备数据会以 `alert:{device_id}` 的形式写入 Redis，用于后续告警或查询

## 6. 项目结构
edge-cloud-demo/
├── edge/ # 边缘侧设备数据模拟
│ └── sensor_simulator.py
├── flink/ # 实时计算与告警逻辑
│ └── temperature_alert_job.py
├── docker-compose.yml # Kafka / Redis 环境部署
└── README.md

## 7. 运行方式（可选）
```bash
docker-compose up
pip install kafka-python redis pyflink
python edge/sensor_simulator.py

8. 可扩展方向

接入真实嵌入式设备或 MCU

引入设备状态持久化数据库

增加可视化监控与告警推送

引入机器学习模型进行设备故障预测
