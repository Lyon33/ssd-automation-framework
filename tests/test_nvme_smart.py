import pytest
from core.nvme_tool import NVMeTool

def test_nvme_smart_health_check():
    """测试用例：验证 SSD 在当前状态下的关键 SMART 指标未突破固件红线"""
    nvme = NVMeTool(device_path="/dev/nvme0")
    smart_data = nvme.get_smart_log()
    
    assert smart_data["percentage_used"] < 100, "🚨 错误：SSD 寿命已耗尽！"
    assert smart_data["available_spare"] >= 10, "🚨 错误：可用预留块（Available Spare）低于安全阈值！"
    assert smart_data["media_errors"] == 0, f"🚨 拦截到固件底层介质错误！Media Errors count: {smart_data['media_errors']}"
    
    # 温度换算过滤：开氏度转摄氏度 (315K -> ~42°C)，超过 75°C 报警
    celsius_temp = smart_data["temperature"] - 273
    assert celsius_temp < 75, f"🚨 警告：SSD 核心温度过高 ({celsius_temp}°C)！"

