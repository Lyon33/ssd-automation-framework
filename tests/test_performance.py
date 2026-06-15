import pytest
import os
import yaml
from core.fio_runner import FIORunner

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
    
    # 【正向重构：拒绝跨行污染】利用 user_properties 将真实的物理测试跑分动态绑定到当前节点
    # 彻底废除落后的 request.config.test_results_bucket[-1] 盲猜修改机制
    request.node.user_properties.append(("Test_Suite", "Performance_Test"))
    request.node.user_properties.append(("Case_Name", f"Perf_{rw_type}_{block_size}_QD{qd}"))
    request.node.user_properties.append(("fio_status", result.get("status", "FAIL")))
    request.node.user_properties.append(("error_code", result.get("error_code", "0x00")))
    request.node.user_properties.append(("error_msg", result.get("error_msg", "Success")))
    request.node.user_properties.append(("iops", result.get("iops", 0)))
    request.node.user_properties.append(("latency_ms", result.get("latency_ms", 0.0)))
    
    assert result["status"] == "PASS", f"触发存储底层报错: {result['error_msg']}"
