import pytest
import os
import time
import yaml
from core.fio_runner import FIORunner
from core.nvme_tool import NVMeTool

# 鲁棒性防御：动态获取当前文件所在目录，确保在 WSL 的任何路径下都能精准读取 yaml 统一参数
current_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(current_dir, "../config/config.yaml")

with open(config_path, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

@pytest.fixture(scope="module")
def fio_instance():
    """复用 FIO Runner 驱动"""
    return FIORunner(target_path=config["target_drive"])

def test_ssd_endurance_stress(request, fio_instance):
    """
    Endurance 长时耐久性测试
    模拟长时间高负载写入，验证 Wear Leveling、Media Errors、寿命衰减是否在合理范围内
    """
    print("\n🔄 [Endurance Test] 开始执行耐久性压力测试（10 个循环）...")
    
    nvme = NVMeTool(device_path="/dev/nvme0")
    initial_smart = nvme.get_smart_log()
    initial_wear = initial_smart.get("percentage_used", 0)
    initial_media_errors = initial_smart.get("media_errors", 0)
    
    total_iops = 0
    cycles = 10  # 压测循环次数
    
    for cycle in range(1, cycles + 1):
        print(f"  → Cycle {cycle}/{cycles} 执行中...")
        
        # 每个循环执行一次高负载随机写入
        result = fio_instance.run_job(rw_type="randwrite", block_size="4k", qd=32)
        
        total_iops += result["iops"]
        
        # 每3个循环采集一次 SMART
        if cycle % 3 == 0 or cycle == cycles:
            smart = nvme.get_smart_log()
            current_wear = smart.get("percentage_used", 0)
            current_errors = smart.get("media_errors", 0)
            print(f"    Wear Leveling: {current_wear}% | Media Errors: {current_errors}")
        
        time.sleep(0.5)  # 控制演示速度
    
    final_smart = nvme.get_smart_log()
    final_wear = final_smart.get("percentage_used", 0)
    wear_increase = final_wear - initial_wear
    
    avg_iops = total_iops // cycles
    
    # 传递数据到报告系统（100% 对齐 13 列 Excel 引擎管道）
    request.node.user_properties.extend([
        ("Test_Suite", "Endurance_Test"),
        ("Case_Name", "SSD_Endurance_Long_Run_Stress"),
        ("fio_status", result["status"]),
        ("error_code", result["error_code"]),
        ("error_msg", f"Endurance completed. Wear increase: {wear_increase}%"),
        ("iops", avg_iops),
        ("latency_ms", result["latency_ms"])
    ])
    
    # 核心断言
    assert wear_increase < 5, f"❌ 寿命衰减过快！Wear Leveling 增加 {wear_increase}%"
    assert final_smart.get("media_errors", 0) <= initial_media_errors + 10, "❌ Media Errors 显著增加，存在潜在坏块风险"
    
    print(f"✅ [Endurance] 测试完成！平均 IOPS: {avg_iops} | Wear 增加: {wear_increase}%")

