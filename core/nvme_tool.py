import subprocess
import json
import shutil
import random

class NVMeTool:
    """NVMe-cli 命令行工具封装，支持真实固件交互与 WSL 环境 Mock 仿真"""
    
    def __init__(self, device_path="/dev/nvme0"):
        self.device_path = device_path
        # 检查系统是否安装了 nvme-cli
        self.has_nvme_cli = shutil.which("nvme") is not None

    def get_smart_log(self) -> dict:
        """获取 SSD 的 SMART 健康日志"""
        if not self.has_nvme_cli:
            # WSL 环境或无物理盘环境：Mock 纯正的 nvme-cli json 输出
            # 故意埋入 media_errors=0 正常，或者特定用例下触发故障
            return {
                "critical_warning": 0,
                "temperature": 315,  # 开氏度 (约 42°C)
                "available_spare": 100,
                "percentage_used": 2,  # 已使用寿命 2%
                "data_units_read": 1254032,
                "data_units_written": 985421,
                "media_errors": 0,  # 媒体错误数
                "num_err_log_entries": 0
            }
        
        try:
            # 真实机台：执行底层 nvme smart-log /dev/nvme0 -o json
            cmd = ["sudo", "nvme", "smart-log", self.device_path, "-o", "json"]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            return json.loads(result.stdout)
        except Exception:
            # 降级防御
            return {"media_errors": -1, "temperature": 0, "percentage_used": -1}

    def get_telemetry_log(self) -> dict:
        """获取 NVMe Telemetry Log (Log Page 0x07)，支持真实命令 + Mock"""
        if not self.has_nvme_cli:
            # Mock 数据 - 模拟真实 Telemetry Log 关键字段
            return {
                "log_page_version": 0x0001,
                "log_page_length": 4096,
                "reason_identifier": "Host_Initiated" if random.random() > 0.5 else "Internal_Error",
                "num_telemetry_entries": random.randint(5, 25),
                "total_data_units_read": 1254032,
                "total_data_units_written": 985421,
                "host_write_commands": 456789,
                "controller_busy_time": 12345,
                "power_cycles": 42,
                "power_on_hours": 8760,
                "unsafe_shutdowns": 3,
                "media_errors": 0
            }
        
        try:
            # 真实机台执行 nvme telemetry-log
            cmd = ["sudo", "nvme", "telemetry-log", self.device_path, "-o", "json", "--rae"]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                # 提取关键字段（适配真实输出结构）
                return {
                    "log_page_version": data.get("log_page_version", 1),
                    "log_page_length": data.get("log_page_length", 4096),
                    "reason_identifier": data.get("reason_identifier", "N/A"),
                    "num_telemetry_entries": len(data.get("telemetry_entries", [])),
                    "total_data_units_read": data.get("total_data_units_read", 0),
                    "total_data_units_written": data.get("total_data_units_written", 0),
                    "host_write_commands": data.get("host_write_commands", 0),
                    "power_cycles": data.get("power_cycles", 0),
                    "power_on_hours": data.get("power_on_hours", 0),
                    "media_errors": data.get("media_errors", 0)
                }
            else:
                raise Exception(result.stderr)
                
        except Exception:
            # 降级返回 Mock 数据
            print("⚠️ [NVMeTool] telemetry-log 执行失败，回退 Mock 数据")
            return self.get_telemetry_log()  # 递归调用 Mock 分支

