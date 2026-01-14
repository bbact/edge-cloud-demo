# Edge to Cloud Real-time Monitoring Demo

## 项目背景
嵌入式设备在工业和物联网场景中会持续产生传感器数据，
本项目模拟设备在边缘侧采集数据，并在云端进行实时分析和告警。

## 技术栈
- Python（模拟嵌入式设备）
- Kafka
- Flink
- Redis
- Docker Compose

## 系统架构
设备 → Kafka → Flink → Redis → 告警展示

## 项目功能
- 模拟设备周期性上报传感器数据
- 实时检测温度异常
- 对异常设备进行告警标记

## 运行方式
```bash
docker-compose up
