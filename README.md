# 🔧 Claude Tools

Claude Code 工具集，包含工具箱和监控守护进程。

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?logo=python" />
  <img src="https://img.shields.io/badge/PowerShell-7+-purple?logo=powershell" />
  <img src="https://img.shields.io/badge/License-MIT-yellow" />
</p>

## 📁 项目结构

```
claude-tools/
├── toolkit/           # Claude工具箱
│   ├── toolkit.py     # 主程序
│   ├── modules/       # 功能模块
│   └── data/          # 数据文件
└── watchdog/          # 监控守护进程
    ├── claude-watchdog.ps1   # PowerShell监控脚本
    └── start-watchdog.cmd    # 启动脚本
```

## 🛠️ 工具箱功能

- 文件操作工具
- 系统信息查询
- 网络工具
- 编码转换
- 数据处理

## 🐕 监控守护进程

自动监控 Claude Code 进程状态，异常时自动重启。

```bash
# 启动监控
cd watchdog
start-watchdog.cmd
```

## 📦 安装

```bash
git clone https://github.com/cerqwq/claude-tools.git
cd claude-tools
pip install -r toolkit/requirements.txt
```

## 📄 许可证

MIT License
