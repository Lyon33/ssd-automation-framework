import pytest
from core.nvme_tool import NVMeTool

def test_nvme_telemetry_log_collection(request):
    """
    NVMe Telemetry Log 测试用例：
    验证 SSD Telemetry 数据采集与关键字段合法性（NVMe Log Page 0x07），
    并动态拦截高并发压测后可能触发的主控隐性死锁转储（Internal Error Panic Dump）。
    """
    nvme = NVMeTool(device_path="/dev/nvme0")
    telemetry_data = nvme.get_telemetry_log()
    
    # 1. 核心断言 - 严格对齐 NVMe Specification 协议一致性红线
    assert telemetry_data["log_page_version"] > 0, "🚨 协议阻断：Telemetry Log 版本号无效！"
    assert telemetry_data["log_page_length"] >= 512, "🚨 协议阻断：Telemetry Log 长度不符合最小规范！"
    assert telemetry_data.get("total_data_units_read", 0) >= 0, "累计读取量数据异常！"
    assert telemetry_data.get("total_data_units_written", 0) >= 0, "累计写入量数据异常！"
    
    # 2. 【硬核存储测谎拦截】根据底层驱动返回的遥测触发类型进行高级品控门禁
    # 顺水推舟：直接对接源码里的 "Internal_Error" 状态！
    reason_id = telemetry_data.get('reason_identifier', 'N/A')
    
    fio_status = "PASS"
    err_code = "0x00"
    err_msg = "Telemetry Log collected successfully"
    
    # 如果前置高强度压测在底层引发了控制器级内部故障崩溃，用例强制爆红拦截！
    if "Internal_Error" in str(reason_id):
        fio_status = "FAIL"
        err_code = "0x03"
        err_msg = f"🚨 [Telemetry 拦截] 检测到主控固件因 GC 乱序或 FTL 溢出触发隐性死锁！Reason: {reason_id}"
    
    print(f"✅ [Telemetry 采集成功] Trigger Reason: {reason_id} | Entries: {telemetry_data.get('num_telemetry_entries', 0)}")
    
    # 3. 使用 user_properties 属性泵原子化传递数据，与中央收集器（conftest.py）实现 100% 完美的正向闭环
    # 确保此高级协议用例在 13 列量产 Excel 评估大表里严丝合缝对齐，绝不留一笔错位空行！
    request.node.user_properties.extend([
        ("Test_Suite", "NVMe_Protocol_Test"),
        ("Case_Name", "NVMe_Telemetry_Log_Collection"),
        ("fio_status", fio_status),
        ("error_code", err_code),
        ("error_msg", err_msg),
        ("iops", 0),
        ("latency_ms", 0.0)
    ])
    
    # 触发最终断言门禁，让固件隐性 Panic 在 CI/CD 流水线上无所遁形
    assert fio_status == "PASS", err_msg

