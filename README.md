# 对话处理工具

这是一个用于处理和分析对话数据的工具集。主要功能包括语音识别（ASR）结果的解析、说话人合并，以及使用 Qwen API 进行对话分析。

## 功能特点

- 🎯 ASR结果解析：将原始ASR结果转换为结构化数据
- 👥 说话人合并：智能合并连续的相同说话人的对话内容
- 🤖 智能分析：使用 Qwen API 进行对话内容分析和纠错
- 📊 日志记录：详细的处理过程日志，方便追踪和调试

## 项目结构

```
project/
├── data/                # 数据目录
│   ├── asr_result/     # ASR原始结果
│   ├── parsed_results/ # 解析后的结果
│   ├── merge_results/  # 合并后的结果
│   └── qwenapi_result/ # API分析结果
├── logs/               # 日志文件目录
├── absdata.py         # ASR数据解析模块
├── merge_speaker.py   # 说话人合并模块
├── qwenapi.py        # Qwen API 交互模块
└── requirements.txt   # 项目依赖
```

## 使用方法

### 1. ASR结果解析

```bash
python absdata.py --input-prefix data/asr_result --output data/parsed_results --start 1 --end 46
```

参数说明：
- `--input-prefix`: 输入文件前缀
- `--output`: 输出目录
- `--start`: 起始文件编号
- `--end`: 结束文件编号

### 2. 说话人合并

```bash
python merge_speaker.py
```

此命令会自动处理 `data/parsed_results` 目录下的所有文件，并将结果保存到 `data/merge_results` 目录。

### 3. Qwen API 分析

```bash
python qwenapi.py <input_file> <output_file>
```

## 环境要求

- Python 3.7+
- aiohttp
- tqdm
- logging

## 安装依赖

```bash
pip install -r requirements.txt
```

## 日志说明

所有处理过程的日志都会保存在 `logs` 目录下，格式为：
- ASR处理日志：`asr_processing_YYYYMMDD_HHMMSS.log`
- Qwen API处理日志：`qwen7b_processing_YYYYMMDD_HHMMSS.log`

## 注意事项

1. 确保在运行前已经正确配置 Qwen API 的访问令牌
2. 处理大量文件时，建议先小批量测试
3. 注意检查日志文件，及时发现和处理可能的错误

## 开发规范

- 使用函数式编程，避免创建不必要的类
- 使用日志输出代替 print 语句
- 函数设计时优先使用参数传递

## 版本控制

本项目使用 Git 进行版本控制，GitHub 仓库地址：

```
git@github.com:Mrliujunwen/personal.git
```

### 克隆仓库

```bash
git clone git@github.com:Mrliujunwen/personal.git
cd personal
```

### 提交更改

```bash
git add .
git commit -m "描述你的更改"
git push origin main
```

### 获取最新代码

```bash
git pull origin main
```

## 贡献指南

1. Fork 本仓库
2. 创建你的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交你的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建一个 Pull Request