# SSD Automation Test Framework (固态硬盘系统级自动化测试框架)

[![Python Version](https://shields.io)](https://python.org)
[![Test Status](https://shields.io)](https://github.com)
[![Framework](https://shields.io)](https://pytest.org)

An enterprise-grade, highly decoupled SSD system-level automation test framework designed for NVMe/SATA storage reliability and performance verification. Features FTL defect injection, SPOR (Sudden Power Off Recovery) simulation, and automated quality control reporting.

对齐大厂量产标准的 SSD 系统级自动化测试框架。采用多文件高度解耦架构，内嵌 FTL 缺陷拦截矩阵与自适应热插拔断电（SPOR）仿真时序，自动输出量产级品控评估报告。

---

## 🚀 Key Features (核心特性)

- **FIO Automation Runner**: Object-oriented encapsulation of industry-standard FIO tool, supporting 16-grid parametric performance boundary testing (Read/Write × Block Size × QD1-32).
- **FTL Defect Injection**: 5% randomized simulation of flash bad block overflow and command timeout (0x03 error).
- **SPOR Simulation**: Dual-track hardware hot-plug mechanism. Simulates standard `/sys/bus/pci/devices/.../remove` node manipulation in WSL, scalable to physical testbed power-cut fixtures.
- **Data Analytics Pipeline**: Built-in Pytest hooks with Pandas/OpenPyXL backend to automatically clean telemetry logs and output `SSD_Mass_Production_Validation_Report.xlsx`.

---

## 📂 Project Structure (项目架构)

```text
├── core/
│   ├── fio_runner.py        # FIO hardware driver & defect injection
│   └── report_generator.py  # Pandas data analytics & Excel pipeline
├── tests/
│   ├── conftest.py          # Global setup/teardown & report hooks
│   ├── test_performance.py  # 16-group performance boundary matrix
│   └── test_reliability.py  # SPOR exception and 0x04 CFS interceptor
├── pytest.ini               # Path resolution & test configurations
├── requirements.txt         # Adaptive dependency lock
└── README.md                # Project documentation
```

---

## 🛠️ Roadmap (项目后续扩展路线图)

- [ ] **scripts/**: Add `nvme-cli` parsing scripts for real-time SMART log attributes extraction (e.g., Media Errors, Available Spare).
- [ ] **firmware/**: Integrate automated firmware download (FW DL) test cases across dual slots with activation checks.
- [ ] **docs/**: Append standard NVMe specification test specification templates (relying on NVMe 2.0 State Machine).
- [ ] **ci/**: Complete Jenkinsfile optimization for distributed remote node execution on physical test execution engines.

---

## 💻 Quick Start (快速开始)

```bash
# Clone the repository
git clone https://github.com
cd ssd-automation-test-framework

# Setup environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run full validation suite
pytest -v
```

