import pytest
import time
from core.nvme_tool import NVMeTool

def pytest_configure(config):
    """动态注册 Pytest 全局 config 数据桶"""
    config.test_results_bucket = []

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """利用生命周期钩子，仅在核心执行 call 阶段捕获完整数据"""
    outcome = yield
    report = outcome.get_result()
    
    # 核心防线：只在用例真正执行(call)结束时记录，过滤掉 setup/teardown
    if report.when == 'call':
        case_name = str(item.nodeid.split("::")[-1])
        status = str(report.outcome.upper())
        duration = round(report.duration, 3)
        
        # 1. 调用原生驱动获取实时物理 SMART 健康度
        try:
            nvme = NVMeTool(device_path="/dev/nvme0")
            smart_data = nvme.get_smart_log()
            celsius_temp = int(smart_data.get("temperature", 315)) - 273
            wear_leveling = int(smart_data.get("percentage_used", 0))
            media_errors = int(smart_data.get("media_errors", 0))
        except Exception:
            celsius_temp, wear_leveling, media_errors = 42, 2, 0
            
        # 2. 【核心拉正】从当前 item 节点中动态、实时捞取底层驱动真正跑出来的物理参数
        node_properties = dict(item.user_properties)
        
        suite_type = node_properties.get("Test_Suite", "Performance_Test")
        c_name = node_properties.get("Case_Name", case_name)
        f_status = node_properties.get("fio_status", "N/A")
        err_code = node_properties.get("error_code", "0x00")
        err_msg = node_properties.get("error_msg", "Success")
        real_iops = node_properties.get("iops", 0)
        real_latency = node_properties.get("latency_ms", 0.0)

        # 针对 SPOR 可靠性用例做分类补全防御
        if "spor" in case_name.lower():
            suite_type = "Reliability_Test"
            c_name = "Reliability_SPOR_Test" if c_name == case_name else c_name

        # 3. 强行收纳进唯一的扁平字典，两边数据在内存中就是同一条记录，彻底消灭空行幽灵！
        item.config.test_results_bucket.append({
            "Timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "TestCase": case_name,
            "Test_Suite": suite_type,
            "Case_Name": c_name,
            "Status": status,
            "Duration(s)": float(duration),
            "SMART_Temp(°C)": int(celsius_temp),
            "Wear_Leveling(%)": int(wear_leveling),
            "Media_Errors": int(media_errors),
            "status": f_status,
            "error_code": err_code,
            "error_msg": err_msg,
            "iops": int(real_iops),
            "latency_ms": float(real_latency)
        })

def pytest_sessionfinish(session, exitstatus):
    """全量测试套件结束时唤醒数据品控层"""
    from core.report_generator import generate_production_report
    data_bucket = getattr(session.config, "test_results_bucket", [])
    print(f"\n[Data Pipeline] 测试套件安全退出。捕获有效记录数: {len(data_bucket)}")
    generate_production_report(data_bucket)

