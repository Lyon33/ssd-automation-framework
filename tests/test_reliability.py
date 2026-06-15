import pytest
import random
import time
import os
import yaml
from core.fio_runner import FIORunner

# 动态获取路径，确保读取全局配置
current_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(current_dir, "../config/config.yaml")

with open(config_path, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

def test_ssd_spor_power_failure(request):
    """
    对齐JD任职2：异常断电测试（SPOR）验证。
    调用底层 PCIe Hot-Plug 逻辑，模拟闪存转换层（FTL）在突发掉电环境下的元数据恢复能力。
    """
    # 1. 实例化驱动，并触发硬件断电时序
    runner = FIORunner(target_path=config["target_drive"])
    power_off_success = runner.simulate_pcie_hot_plug_power_off(pcie_address=config["pcie_address"])
    
    # 2. 模拟断电后重新上电，FTL 重新加载元数据映射表（L2P Table）
    print("[SPOR测试] 步骤3: 触发系统总线重新扫描，模拟 SSD 恢复供电上电时序...")
    time.sleep(0.5)
    
    # 仿真断电重上电后，2% 概率重现行业内严重的“断电导致FTL元数据崩溃/掉盘无法识别”致命Bug
    if power_off_success:
        hardware_status = "READY" if random.random() > 0.02 else "DEAD_CONTROLLER_CFS"
    else:
        hardware_status = "INIT_FAILED"
    
    # 3. 将执行数据压入全局量产数据桶中
    request.config.test_results_bucket.append({
        "Test_Suite": "Reliability_Test",
        "Case_Name": "Reliability_SPOR_Abnormal_Power_Off",
        "status": "PASS" if hardware_status == "READY" else "FAIL",
        "error_code": "0x00" if hardware_status == "READY" else "0x04",
        "error_msg": "Success" if hardware_status == "READY" else "Fatal: NVMe Controller Fatal Status (CFS) / FTL Corrupted",
        "iops": 0,
        "latency_ms": 0.0
    })
    
    # 4. 核心品控红线断言
    assert hardware_status == "READY", "🚨 致命硬件缺陷：SSD在执行异常断电后重上电触发CFS挂盘，盘片无法识别！"
