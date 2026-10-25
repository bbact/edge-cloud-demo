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

三台模拟设备大约每 2 秒上报一次温度和湿度。一号、二号车间以正常温度为主，老化测试台更容易超过 80°C。告警只在状态发生变化时记录一次，温度回到 80°C 及以下时记录恢复。超过 3 个上报间隔没有新数据时，页面把该设备显示为离线，这不算温度告警。

## 在这台电脑上启动

本机 9092 上已有另一套 Kafka，Docker 镜像源也可能拉不到 Python 镜像。这条命令只启动已经准备好的 Kafka 3.9 和 Redis，再用本机 Python 跑模拟器、处理和页面。宿主机 Kafka 端口默认是 19092，可以用 `KAFKA_HOST_PORT` 覆盖。

```bash
./scripts/demo.sh
```

浏览器打开 http://127.0.0.1:8000 。

停掉本机的三个 Python 进程：

```bash
kill $(cat .demo/simulator.pid .demo/processor.pid .demo/api.pid)
```

## 镜像源正常时整套启动

容器内部仍连接 `kafka:29092`。宿主机端口同样默认 19092。

```bash
docker compose up --build
```

浏览器打开 http://localhost:8000 。

```bash
docker compose down
```

## 规则测试

```bash
python3 -m unittest tests/test_rules.py
```

## 目录

```text
edge/sensor_simulator.py    设备数据模拟
cloud/processor.py          消费 Kafka，按温度阈值写 Redis
cloud/rules.py              告警和离线判定
cloud/api.py                查询接口和页面
web/                        监测页面
scripts/demo.sh             本机启动 Kafka、Redis 和三个 Python 进程
docker-compose.yml          Kafka、Redis、模拟器、处理和页面
```
