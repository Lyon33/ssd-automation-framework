import pytest
import os
from core.report_generator import ReportGenerator

def pytest_configure(config):
    """在测试会话（Session）启动时，初始化全局数据桶"""
    config.test_results_bucket = []

@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    """生命周期钩子：当所有用例跑完后自动触发，清洗数据并打包 Excel"""
    bucket = getattr(session.config, "test_results_bucket", [])
    if bucket:
        ReportGenerator.generate_excel_report(bucket)
