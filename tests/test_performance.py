import pytest
import os
import yaml
from core.fio_runner import FIORunner

# 鲁棒性防御：动态获取当前文件所在目录，确保在 WSL 的任何路径下都能精准读取 yaml
current_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(current_dir, "../config/config.yaml")

with open(config_path, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

@pytest.fixture(scope="module")
def fio_instance():
    return FIORunner(target_path=config["target_drive"])

@pytest.mark.parametrize("rw_type", ["randwrite", "randread"])
@pytest.mark.parametrize("block_size", config["fio_settings"]["block_sizes"])
@pytest.mark.parametrize("qd", config["fio_settings"]["queue_depths"])
def test_ssd_io_performance(fio_instance, rw_type, block_size, qd, request):
    """用例大类 1：验证 SSD 在全队列深度、全块大小下的极限吞吐性能"""
    result = fio_instance.run_job(rw_type, block_size, qd)
    
    request.config.test_results_bucket.append({
        "Test_Suite": "Performance_Test",
        "Case_Name": f"Perf_{rw_type}_{block_size}_QD{qd}",
        "status": result["status"],
        "error_code": result["error_code"],
        "error_msg": result["error_msg"],
        "iops": result["iops"],
        "latency_ms": result["latency_ms"]
    })
    assert result["status"] == "PASS", f"触发存储底层报错: {result['error_msg']}"

