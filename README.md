# 边缘到云端实时监测

嵌入式设备持续上报运行数据。这条演示链路把数据送到云端，温度超过 80°C 时写入告警，并在页面上查看当前状态。

## 链路

```text
设备模拟器
    ↓  sensor-data
Kafka
    ↓
实时处理
    ↓  device:{设备号}、alert:{设备号}、告警记录
Redis
    ↓
监测页面  http://localhost:8000
```

三台模拟设备大约每 2 秒上报一次温度和湿度。一号、二号车间以正常温度为主，老化测试台更容易超过 80°C。告警只在状态发生变化时记录一次，温度回到 80°C 及以下时记录恢复。

## 启动

需要 Docker Desktop。

```bash
docker compose up --build
```

浏览器打开 http://localhost:8000 。

停止：

```bash
docker compose down
```

## 本地只启动消息队列

Kafka 对容器内使用 `kafka:29092`，对宿主机使用 `localhost:9092`。

```bash
docker compose up -d kafka redis
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python edge/sensor_simulator.py
.venv/bin/python -m cloud.processor
.venv/bin/uvicorn cloud.api:app --host 127.0.0.1 --port 8000
```

## 规则测试

```bash
python3 -m unittest tests/test_rules.py
```

## 目录

```text
edge/sensor_simulator.py    设备数据模拟
cloud/processor.py          消费 Kafka，按温度阈值写 Redis
cloud/rules.py              告警判定
cloud/api.py                查询接口和页面
web/                        监测页面
docker-compose.yml          Kafka、Redis、模拟器、处理和页面
```
