from typing import Any, Dict, List, Union
import time
import datetime
import httpx
from mcp.server.fastmcp import FastMCP

# 初始化FastMCP服务器
mcp = FastMCP("mcp-server")

# 常量定义
API_BASE_URL = "http://uds-index-platform.test.fnwintranet.com/index/result/update"
USER = "test"  # 固定值

# 时间类型映射，用于生成合适的时间戳
PERIOD_TYPE_MAPPING = {
    "REAL_TIME": {"format": "%Y-%m-%d %H:%M:%S", "delta": datetime.timedelta(seconds=1)},
    "MINUTE": {"format": "%Y-%m-%d %H:%M", "delta": datetime.timedelta(minutes=1)},
    "HOUR": {"format": "%Y-%m-%d %H", "delta": datetime.timedelta(hours=1)},
    "DAY": {"format": "%Y-%m-%d", "delta": datetime.timedelta(days=1)},
    "MONTH": {"format": "%Y-%m", "delta": datetime.timedelta(days=30)},  # 近似值
    "YEAR": {"format": "%Y", "delta": datetime.timedelta(days=365)}  # 近似值
}

# 完整时间格式，用于解析用户输入
FULL_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

def format_datetime_by_period_type(dt: datetime.datetime, period_type: str) -> str:
    """
    根据时间类型格式化日期时间对象
    
    Args:
        dt: 日期时间对象
        period_type: 时间类型
        
    Returns:
        格式化后的日期时间字符串
    """
    time_format = PERIOD_TYPE_MAPPING.get(period_type, {}).get("format")
    if not time_format:
        raise ValueError(f"不支持的时间类型: {period_type}")
    
    return dt.strftime(time_format)

def generate_timestamps(time_period: str, period_type: str) -> Dict[str, float]:
    """
    根据时间周期和时间类型生成对应的时间戳数据
    
    Args:
        time_period: 时间周期，格式为完整年月日时分秒: "2023-01-01 00:00:00"
        period_type: 时间类型 (REAL_TIME, MINUTE, HOUR, DAY, MONTH, YEAR)
    
    Returns:
        包含时间戳的字典，格式为 {"timestamp": value}
    """
    timestamps = {}
    
    # 获取时间间隔
    time_delta = PERIOD_TYPE_MAPPING.get(period_type, {}).get("delta")
    
    if not time_delta:
        raise ValueError(f"不支持的时间类型: {period_type}")
    
    # 解析时间周期
    start_date = None
    end_date = None
    
    # 处理不同格式的时间周期
    if "~" in time_period:
        # 处理范围格式 "2023-01-01 00:00:00~2023-01-10 00:00:00"
        start_str, end_str = time_period.split("~")
        try:
            # 先解析完整格式的日期时间
            start_date = datetime.datetime.strptime(start_str.strip(), FULL_DATETIME_FORMAT)
            end_date = datetime.datetime.strptime(end_str.strip(), FULL_DATETIME_FORMAT)
        except ValueError:
            raise ValueError(f"无法解析时间周期: {time_period}，请使用格式 {FULL_DATETIME_FORMAT}")
    elif "," in time_period:
        # 处理列表格式 "2023-01-01 00:00:00, 2023-01-02 00:00:00, 2023-01-03 00:00:00"
        date_strings = [date_str.strip() for date_str in time_period.split(",")]
        for date_str in date_strings:
            try:
                # 解析完整格式的日期时间
                date = datetime.datetime.strptime(date_str, FULL_DATETIME_FORMAT)
                
                # 根据时间类型截取相应部分并重新生成日期时间对象
                formatted_date_str = format_datetime_by_period_type(date, period_type)
                truncated_date = datetime.datetime.strptime(
                    formatted_date_str, 
                    PERIOD_TYPE_MAPPING[period_type]["format"]
                )
                
                # 生成时间戳 (Unix时间戳，单位为秒)
                timestamp = int(truncated_date.timestamp())
                timestamps[str(timestamp)] = None  # 值暂时为空
            except ValueError:
                raise ValueError(f"无法解析日期: {date_str}，请使用格式 {FULL_DATETIME_FORMAT}")
        return timestamps
    else:
        # 处理单个日期 "2023-01-01 00:00:00"
        try:
            # 解析完整格式的日期时间
            date = datetime.datetime.strptime(time_period.strip(), FULL_DATETIME_FORMAT)
            
            # 根据时间类型截取相应部分并重新生成日期时间对象
            formatted_date_str = format_datetime_by_period_type(date, period_type)
            truncated_date = datetime.datetime.strptime(
                formatted_date_str, 
                PERIOD_TYPE_MAPPING[period_type]["format"]
            )
            
            # 生成时间戳 (Unix时间戳，单位为秒)
            timestamp = int(truncated_date.timestamp())
            timestamps[str(timestamp)] = None  # 值暂时为空
            return timestamps
        except ValueError:
            raise ValueError(f"无法解析时间周期: {time_period}，请使用格式 {FULL_DATETIME_FORMAT}")
    
    # 如果是范围，根据时间类型截取相应部分
    formatted_start_str = format_datetime_by_period_type(start_date, period_type)
    formatted_end_str = format_datetime_by_period_type(end_date, period_type)
    
    # 根据时间类型截取相应部分并重新生成日期时间对象
    start_date = datetime.datetime.strptime(
        formatted_start_str, 
        PERIOD_TYPE_MAPPING[period_type]["format"]
    )
    end_date = datetime.datetime.strptime(
        formatted_end_str, 
        PERIOD_TYPE_MAPPING[period_type]["format"]
    )
    
    # 生成时间范围内的所有时间戳
    current_date = start_date
    while current_date <= end_date:
        # 生成时间戳 (Unix时间戳，单位为秒)
        timestamp = int(current_date.timestamp())
        timestamps[str(timestamp)] = None  # 值暂时为空
        current_date += time_delta
    
    return timestamps


async def send_data_to_api(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    向API发送数据
    
    Args:
        payload: 要发送的数据负载
    
    Returns:
        API响应结果
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(API_BASE_URL, json=payload, timeout=50.0)
            response.raise_for_status()
            result = response.json()
            
            # 检查API返回的success字段
            if not result.get("success", False):
                return {
                    "error": result.get("message", "未知错误"),
                    "code": result.get("code", ""),
                    "details": result.get("data")
                }
            return result
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP错误: {e.response.status_code}", "details": e.response.text}
        except Exception as e:
            return {"error": f"请求错误: {str(e)}"}


async def batch_send_data(
    dps: Dict[str, float],
    device_code: str,
    index_code: str,
    period_type: str,
    system_code: str,
    batch_size: int = 20
) -> Dict[str, Any]:
    """
    批量发送数据，每批不超过指定数量
    
    Args:
        dps: 要发送的数据点
        device_code: 设备编码
        index_code: 测点编码
        period_type: 时间类型
        system_code: 系统编码
        batch_size: 每批发送的最大数据点数量
        
    Returns:
        操作结果
    """
    # 将数据分批
    timestamp_keys = list(dps.keys())
    batches = [timestamp_keys[i:i + batch_size] for i in range(0, len(timestamp_keys), batch_size)]
    
    total_success = 0
    errors = []
    
    for i, batch in enumerate(batches):
        # 为当前批次创建数据负载
        batch_dps = {k: dps[k] for k in batch}
        payload = {
            "dps": batch_dps,
            "extTags": {},  # 为空
            "indexResultKey": {
                "deviceCode": device_code,
                "indexCode": index_code,
                "periodType": period_type,
                "systemCode": system_code
            },
            "user": USER
        }
        
        # 发送数据到API
        result = await send_data_to_api(payload)
        
        # 处理结果
        if "error" in result:
            batch_info = f"批次{i+1}/{len(batches)}"
            error_message = f"{batch_info}: {result['error']}"
            if "code" in result:
                error_message += f" (代码: {result['code']})"
            errors.append(error_message)
        else:
            total_success += len(batch)
    
    return {
        "success_count": total_success,
        "errors": errors
    }


@mcp.tool()
async def add_index_data(
    system_code: str,
    device_code: str, 
    index_code: str,
    period_type: str,
    time_period: str,
    data_value: float
) -> str:
    """
    向大数据平台添加测点数据
    
    Args:
        system_code: 系统编码，例如 "PARK3853_EMS01"
        device_code: 设备编码，例如 "CEC_CEC01" 
        index_code: 测点编码，例如 "FfuelIntD"
        period_type: 时间类型，可选值: "REAL_TIME"(实时), "MINUTE"(分钟), "HOUR"(小时), "DAY"(日), "MONTH"(月), "YEAR"(年)
        time_period: 时间周期，使用完整的年月日时分秒格式，可以是单个时间、时间列表或时间范围
                     例如: "2023-01-01 00:00:00"、"2023-01-01 00:00:00,2023-01-02 00:00:00"、"2023-01-01 00:00:00~2023-01-10 00:00:00"
        data_value: 数据值，浮点数
    
    Returns:
        操作结果信息
    """
    # 验证时间类型
    if period_type not in PERIOD_TYPE_MAPPING:
        return f"错误: 不支持的时间类型 '{period_type}'。支持的类型包括: REAL_TIME, MINUTE, HOUR, DAY, MONTH, YEAR"
    
    try:
        # 生成时间戳数据
        dps = generate_timestamps(time_period, period_type)
        
        # 检查数据点数量
        data_points_count = len(dps)
        if data_points_count > 100:
            return f"错误: 数据点数量({data_points_count})超过最大限制(100)。请缩小时间范围或使用较粗粒度的时间类型。"
        
        # 填充数据值
        for timestamp in dps:
            dps[timestamp] = data_value
        
        # 检查是否需要分批发送
        if data_points_count <= 20:
            # 单批发送
            payload = {
                "dps": dps,
                "extTags": {},  # 为空
                "indexResultKey": {
                    "deviceCode": device_code,
                    "indexCode": index_code,
                    "periodType": period_type,
                    "systemCode": system_code
                },
                "user": USER
            }
            
            # 发送数据到API
            result = await send_data_to_api(payload)
            
            # 处理结果
            if "error" in result:
                error_msg = f"添加数据失败: {result['error']}"
                if "code" in result:
                    error_msg += f"\n错误代码: {result['code']}"
                if "details" in result and result["details"]:
                    error_msg += f"\n详情: {result['details']}"
                return error_msg
        else:
            # 分批发送
            result = await batch_send_data(
                dps, 
                device_code, 
                index_code, 
                period_type, 
                system_code
            )
            
            if result["errors"]:
                return f"添加数据部分失败，成功: {result['success_count']}/{data_points_count}\n错误: {', '.join(result['errors'])}"
            
            if result["success_count"] != data_points_count:
                return f"添加数据部分成功: {result['success_count']}/{data_points_count}"
        
        # 提取时间点信息以便展示
        time_points = list(dps.keys())
        time_count = len(time_points)
        time_sample = time_points[:3] if time_count > 3 else time_points
        batch_info = "" if time_count <= 20 else f"\n分批发送: {(time_count + 19) // 20}批，每批最多20条"
        
        return f"""
数据添加成功!
系统编码: {system_code}
设备编码: {device_code}
测点编码: {index_code}
时间类型: {period_type}
数据值: {data_value}
添加的时间点数量: {time_count}{batch_info}
时间点样例: {', '.join(time_sample)}{' ...' if time_count > 3 else ''}
"""
    except ValueError as e:
        return f"错误: {str(e)}"
    except Exception as e:
        return f"添加数据时发生意外错误: {str(e)}"

# # 使用测试函数来添加数据
import asyncio
async def main():
    print("开始添加测点数据...")
    # 添加2025年1月的天级数据
    result = await add_index_data(
        "PARK3853_EMS01",  # 系统编码
        "CEC_CEC01",       # 设备编码
        "FfuelIntD",       # 测点编码
        "DAY",             # 时间类型：天级
        "2025-01-01 00:00:00~2025-01-31 00:00:00",  # 时间周期：2025年1月
        29.32              # 数据值
    )
    print(result)

if __name__ == "__main__":
    asyncio.run(main()) 


# if __name__ == "__main__":
#     # 初始化并运行服务器
#     print("启动MCP服务器...")
#     mcp.run(transport='stdio')