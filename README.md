# 对话处理工具集

## 📝 项目简介

这是一个专门用于处理和分析对话数据的工具集合。主要用于处理语音识别（ASR）结果，进行说话人合并，并利用 Qwen API 进行智能分析。

## ✨ 核心功能

- ASR结果解析：将ASR原始输出转换为结构化JSON数据
- 说话人合并：基于时间戳智能合并同一说话人的连续对话
- 智能分析：接入Qwen API实现对话内容的智能分析和错别字纠正
- 特殊处理：支持提取特定说话人（如"皇上"）的对话内容
- 数据泛化：通过api.py进行数据泛化和动态采样，生成高质量数据集
- 日志追踪：完整的处理过程日志记录

## 📁 目录结构

```
project/
├── data/                # 数据存储目录
│   ├── asr_result/     # ASR原始结果
│   ├── parsed_results/ # 解析后的数据
│   ├── merge_results/  # 合并后的数据
│   └── qwenapi_result/ # API分析结果
├── logs/               # 日志文件目录
├── absdata.py         # ASR数据解析模块
├── merge_speaker.py   # 说话人合并模块
├── qwenapi.py        # Qwen API交互模块
├── api.py            # 数据泛化与采样模块
└── requirements.txt   # 项目依赖文件
```

## 🚀 使用指南

### 1. 环境配置

```bash
# 安装依赖
pip install -r requirements.txt
```

### 2. 数据提取

```bash
# 从原始数据中提取对话内容
python ext_data.py --input <input_directory> --output <output_directory>
```

主要参数说明：
- `--input`: 原始数据目录
- `--output`: 提取结果保存目录

### 3. ASR结果解析

```bash
python to_json.py --input-prefix data/asr_result --output data/parsed_results --start 1 --end n
```

### 4. 说话人合并处理

```bash
python merge_speaker.py
```

### 5. 提取特定说话人对话

```bash
python find_huang.py
```

### 6. Qwen API分析

```bash
python qwenapi.py <input_file> <output_file>
```

使用Qwen API进行两项重要任务：
- 验证第5步提取的对话内容准确性
- 自动识别并纠正原始对话中的错别字和语法错误

Qwen API处理后的结果将保存在指定的输出文件中，便于后续分析和使用。

### 7. 数据泛化与动态采样

```bash
python api.py <input_data> <output_dataset>
```

api.py的核心功能：
- 对提取的对话数据进行泛化处理
- 通过动态采样算法生成更丰富的数据集
- 提高数据多样性，增强模型训练效果

这是整个处理流程的最后一步，生成的数据集可直接用于后续模型训练。

## 📋 环境要求

- Python 3.10
- iic/speech_paraformer-large-vad-punc-spk_asr_nat-zh-cn
- 依赖包：
  - aiohttp
  - tqdm
  - logging

## 📝 日志说明

系统会自动在`logs`目录下生成处理日志：
- ASR处理日志：`asr_processing_YYYYMMDD_HHMMSS.log`
- Qwen API日志：`qwen7b_processing_YYYYMMDD_HHMMSS.log`

## ⚠️ 注意事项

1. 运行前请确保已配置Qwen API访问令牌
2. 首次处理大量文件时，建议先用小数据集测试
3. 定期检查日志文件，及时处理异常情况

## 🔧 开发规范

- 优先使用函数式编程
- 使用日志模块记录信息，避免print
- 通过参数传递数据，减少全局变量

## 📦 版本控制

```bash
# 克隆仓库
git clone git@github.com:Mrliujunwen/ASP_FOR_LLM.git
cd ASP_FOR_LLM
```
