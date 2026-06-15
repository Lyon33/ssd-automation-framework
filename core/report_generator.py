import os
import pandas as pd

class ReportGenerator:
    """数据处理与量产报告生成层 - 对接江波龙品控与量产核心需求"""
    @staticmethod
    def generate_excel_report(test_records: list, output_path: str = "logs/ssd_production_qualification_report.xlsx"):
        if not test_records:
            return
            
        # 强力防御：自动创建 logs 目录，防止初学者因没有手动建文件夹而报错
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        df = pd.DataFrame(test_records)
        total_cases = len(df)
        fail_cases = len(df[df['status'] == 'FAIL'])
        pass_rate = ((total_cases - fail_cases) / total_cases) * 100
        
        print("\n" + "="*20 + " 📊 WSL 品控数据统计中心 " + "="*20)
        print(f"🔹 自动化总运行用例数: {total_cases} 道")
        print(f"🔹 捕获底层固件/硬件故障数: {fail_cases} 处")
        print(f"🔹 最终转量产合格率标准 (Pass Rate): {pass_rate:.2f}%")
        print("="*61 + "\n")
        
        # 强制指定 openpyxl 引擎，杜绝 Linux 环境下引擎缺失引发的崩溃
        df.to_excel(output_path, index=False, sheet_name="SSD_Test_Data", engine='openpyxl')
        print(f"💾 [品控成功] 报告已生成至: {os.path.abspath(output_path)}")

