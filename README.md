# SSD Automation Test Framework (固态硬盘系统级自动化测试框架)

[![Python Version](https://shields.io)](https://python.org)
[![Test Status](https://shields.io)](https://github.com)
[![CI/CD Pipeline](https://shields.io)](https://jenkins.io)

An enterprise-grade, highly decoupled SSD system-level automation test framework designed for NVMe/SATA storage reliability and performance verification. Features FTL defect injection, SPOR (Sudden Power Off Recovery) simulation, and automated quality control reporting.

**企业级 NVMe SSD 自动化验证框架**，专为固件开发、可靠性验证与量产品控设计。采用多文件高度解耦架构，支持真实 FIO 压测、nvme-cli SMART 健康监控、SPOR 异常断电模拟，并通过后置 Pandas 管道全自动生成量产级品控评估报告。

---

## 🚀 Key Features (核心特性)

- **FIO Automation Runner**: Object-oriented encapsulation with real `fio` job specification priority + enhanced Mock fallback. Supports 16-grid parametric performance boundary testing (Read/Write × Block Size × QD 1-32).
- **FTL Defect Injection**: Simulation of flash bad block overflow and command timeout (0x03 error) to demonstrate framework robustness and dynamic log telemetry capture.
- **SPOR Simulation**: Dual-track hardware hot-plug mechanism. Simulates standard `/sys/bus/pci/devices/.../remove` node manipulation in WSL, scalable to physical testbed power-cut fixtures via sudo permissions.
- **Data Analytics Pipeline**: Built-in Pytest hooks with Pandas/OpenPyXL backend to automatically clean telemetry logs, resolve concurrency row gaps, and generate styled `SSD_Mass_Production_Validation_Report.xlsx`.
- **CI/CD Ready**: Professional Jenkins pipeline integration with JUnit parsing, catchError stage isolation, and automatic artifact archiving.

---

## 📋 Use Cases (适用场景）

- NVMe SSD Firmware Mass Production Validation
- System-level Reliability Boundary Testing
- Advanced Enterprise Automation CI/CD Infrastructure

---

## 📂 Project Structure (项目架构)

```text
ssd-automation-framework/
├── config/
│   └── config.yaml                 # Test configuration parameters
├── core/
│   ├── __init__.py
│   ├── fio_runner.py               # FIO driver (real + mock) & defect injection
│   ├── nvme_tool.py                # nvme-cli SMART log data collector
│   └── report_generator.py         # Production-grade Excel report engine
├── tests/
│   ├── __init__.py
│   ├── conftest.py                 # Global Pytest hooks & atomic user_properties bucket
│   ├── test_nvme_smart.py          # SMART health registers validation
│   ├── test_performance.py         # 16-group performance boundary matrix testing
│   └── test_reliability.py         # SPOR hardware power-failure reliability testing
├── logs/                           # Test report output directory (.gitignore)
├── Jenkinsfile                     # Production-grade Jenkins CI/CD pipeline
├── pytest.ini                      # Path resolution & test configurations
├── requirements.txt                # Adaptive dependency lock
└── README.md                       # Project documentation
```

---

## 🛠️ Roadmap (项目后续扩展路线图)

- [ ] **scripts/**: Add `nvme-cli` parsing scripts for real-time SMART log attributes extraction (e.g., Media Errors, Available Spare).
- [ ] **firmware/**: Integrate automated firmware download (FW DL) test cases across dual slots with activation checks.
- [ ] **docs/**: Append standard NVMe specification test specification templates (based on NVMe 2.0 State Machine).
- [ ] **ci/**: Further Jenkins/Github Actions optimization for distributed physical test nodes.

---

## 💻 Quick Start (快速开始)

```bash
# Clone the repository
git clone https://github.com/Lyon33/ssd-automation-framework.git
cd ssd-automation-framework

# Setup environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run full validation suite
pytest -v
```
