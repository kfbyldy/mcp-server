# MCP服务器项目

## 项目介绍
这是一个基于MCP (Model Control Protocol) 的服务器项目，用于与大数据平台交互。项目主要提供以下功能：

1. **天气数据查询服务**：获取天气预报和天气警报信息
2. **大数据指标上传服务**：向大数据平台上传指标数据

## 功能说明

### 1. 天气数据查询服务 (weather.py)
- `get_alerts`: 获取美国各州的天气警报信息
- `get_forecast`: 获取指定坐标位置的天气预报

### 2. 大数据指标上传服务 (bigdata.py)
- 与大数据平台进行交互，上传各类指标数据

### 3. 大数据测点数据添加服务 (mcp_server.py)
- 向大数据平台添加测点数据，支持不同时间周期类型的数据上传
- 自动根据用户提供的参数生成对应格式的数据

## 使用说明

### 大数据测点数据添加服务
`add_index_data` 功能用于向大数据平台添加测点数据，支持以下参数：

- `system_code`: 系统编码，例如 "PARK3853_EMS01"
- `device_code`: 设备编码，例如 "CEC_CEC01"
- `index_code`: 测点编码，例如 "FfuelIntD"
- `period_type`: 时间类型，可选值包括:
  - "REAL_TIME": 实时数据
  - "MINUTE": 分钟级数据
  - "HOUR": 小时级数据 
  - "DAY": 日级数据
  - "MONTH": 月级数据
  - "YEAR": 年级数据
- `time_period`: 时间周期，格式根据period_type不同而变化:
  - 单个日期: "2023-01-01"
  - 多个日期: "2023-01-01,2023-01-02,2023-01-03"
  - 日期范围: "2023-01-01~2023-01-10"
- `data_value`: 数据值，浮点数类型

### 时间类型与格式对应表

| 时间类型 | 格式 | 示例 |
|----------|------|------|
| REAL_TIME | 年-月-日 时:分:秒 | 2023-01-01 12:30:45 |
| MINUTE | 年-月-日 时:分 | 2023-01-01 12:30 |
| HOUR | 年-月-日 时 | 2023-01-01 12 |
| DAY | 年-月-日 | 2023-01-01 |
| MONTH | 年-月 | 2023-01 |
| YEAR | 年 | 2023 |

### 使用示例

以下是几个调用示例：

#### 1. 添加单个日期的数据
```
add_index_data(
    system_code="PARK3853_EMS01",
    device_code="CEC_CEC01",
    index_code="FfuelIntD",
    period_type="DAY",
    time_period="2023-01-01",
    data_value=188.8
)
```

#### 2. 添加多个日期的数据
```
add_index_data(
    system_code="PARK3853_EMS01",
    device_code="CEC_CEC01",
    index_code="FfuelIntD",
    period_type="DAY",
    time_period="2023-01-01,2023-01-02,2023-01-03",
    data_value=188.8
)
```

#### 3. 添加日期范围的数据
```
add_index_data(
    system_code="PARK3853_EMS01",
    device_code="CEC_CEC01",
    index_code="FfuelIntD",
    period_type="DAY",
    time_period="2023-01-01~2023-01-10",
    data_value=188.8
)
```

#### 4. 添加小时级别数据
```
add_index_data(
    system_code="PARK3853_EMS01",
    device_code="CEC_CEC01",
    index_code="FfuelIntH",
    period_type="HOUR",
    time_period="2023-01-01 00~2023-01-01 23",
    data_value=45.6
)
```

## 调用结果示例

成功调用后，服务将返回类似以下格式的结果：

```
数据添加成功!
系统编码: PARK3853_EMS01
设备编码: CEC_CEC01
测点编码: FfuelIntD
时间类型: DAY
数据值: 188.8
添加的时间点数量: 3
时间点样例: 1672531200, 1672617600, 1672704000
```

## 开发与部署
1. 安装依赖：`pip install -r requirements.txt`
2. 运行服务器：`python mcp_server.py`

## 环境要求
- Python 3.9+
- 依赖包：httpx, mcp

## 注意事项
- 时间戳是以Unix时间戳(秒级)的形式发送给API的
- 建议先测试少量数据，确认无误后再添加大量数据
- 对于长时间范围的数据添加，系统会自动按照对应时间类型生成所有时间点
