import subprocess
import json
import shutil

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

