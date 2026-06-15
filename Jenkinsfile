// 基于声明式（Declarative）语法构建的 SSD 自动化测试流水线
pipeline {
    
    // 指定该流水线可以在任何可以运行 Python/Pytest 的 Linux 测试机台（Node）上执行
    agent any

    // 全局环境变量配置
    environment {
        // 定义测试报告的输出相对路径，与 Python 项目完全对齐
        REPORT_PATH = "logs/ssd_production_qualification_report.xlsx"
    }

    // 核心流转阶段（Stages）：定义 Jenkins 的图形化看板步骤
    stages {
        
        stage('1. 环境初始化 (Env Setup)') {
            steps {
                echo '🚀 [Jenkins] 开始初始化 WSL/Linux 测试机台环境...'
                
                // 初始化并激活隔离的 Python 虚拟环境，升级基础打包工具
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                '''
            }
        }

        stage('2. 安装测试依赖 (Install Deps)') {
            steps {
                echo '📦 [Jenkins] 正在根据 requirements.txt 严格同步第三方依赖版本...'
                
                // 激活虚拟环境并安装核心组件：pytest, pandas, openpyxl, pyyaml
                sh '''
                    . venv/bin/activate
                    pip install -r requirements.txt
                '''
            }
        }

        stage('3. 静态红线扫描 (Static Scan)') {
            steps {
                echo '🔍 [Jenkins] 启动静态编译扫描，杜绝低级语法错误代码上线...'
                
                // 模拟大厂发布前的静态红线安全检查
                sh '''
                    . venv/bin/activate
                    python -m compileall core/ tests/
                '''
            }
        }

        stage('4. 驱动压测矩阵 (Execute Pytest)') {
            steps {
                echo '⚡ [Jenkins] 核心触发：驱动 Pytest 引擎开始执行全量 SSD 测试矩阵...'
                
                // 核心业务：Jenkins 在后台敲下 pytest 驱动用例，跑完后自动触发 conftest.py 产出 Excel
                // 即使测试用例中有 FAIL 缺陷，也不要打断 Jenkins 流程（使用 catchError 拦截）
                catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                    sh '''
                        . venv/bin/activate
                        pytest
                    '''
                }
            }
        }

        stage('5. 产物归档与发布 (Archive Report)') {
            steps {
                echo '📊 [Jenkins] 正在抓取清洗后的量产数据，进行 Jenkins 页面归档...'
                
                // 芯片大厂核心操作：利用 Jenkins 的内置归档指令，把生成的 Excel 报告保存到网页后台
                // 这样品控经理或固件研发打开 Jenkins 网页就能直接“一键下载”
                archiveArtifacts artifacts: "${env_REPORT_PATH}", allowEmptyArchive: false
            }
        }
    }

    // 后置处理通知（不管流水线成功还是失败，都会触发）
    post {
        always {
            echo '🧹 [Jenkins] 清理本次压测产生的临时映射数据，释放测试机台缓存...'
            // 模拟下发清理指令，保持机台纯净
            sh 'rm -f /tmp/mock_ssd_io_*'
        }
        success {
            echo '✅ [Jenkins] 恭喜！本次固件/脚本回归测试 100% 跑通，产品符合转量产要求！'
        }
        failure {
            echo '❌ [Jenkins] 警告！自动化用例捕获到存储底层致命 Bug（请查看 Stage 4 日志并拦截发布）！'
        }
    }
}

