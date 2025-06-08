import json
import ast
import os
import argparse
import logging
from typing import Dict, List, Optional, Union

def setup_logging(log_dir: str = "./logs", log_level: int = logging.INFO) -> logging.Logger:
    """
    设置日志配置
    
    Args:
        log_dir: 日志目录
        log_level: 日志级别
    
    Returns:
        logger: 日志记录器
    """
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "asr_processing.log")
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def parse_asr_data(data: Dict) -> List[Dict]:
    """
    解析ASR数据
    
    Args:
        data: 原始ASR数据
        
    Returns:
        results: 解析后的数据列表
    """
    text_data = ast.literal_eval(data['text'])
    results = []
    
    for item in text_data:
        item_result = {
            'key': item['key'],
            'text': item['text'],
            'sentences': []
        }
        
        for sentence in item['sentence_info']:
            item_result['sentences'].append({
                'speaker': f"Speaker_{sentence['spk']}",
                'text': sentence['text'],
                'start_ms': sentence['start'],
                'end_ms': sentence['end']
            })
        
        results.append(item_result)
    
    return results

def save_results(results: List[Dict], output_dir: str, json_filename: str, txt_filename: str) -> None:
    """
    保存解析结果
    
    Args:
        results: 解析后的数据
        output_dir: 输出目录
        json_filename: JSON文件名
        txt_filename: 文本文件名
    """
    # 保存JSON格式
    output_file = os.path.join(output_dir, json_filename)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # 保存文本格式
    text_output_file = os.path.join(output_dir, txt_filename)
    with open(text_output_file, 'w', encoding='utf-8') as f:
        for result in results:
            f.write(f"\n=== 文件: {result['key']} ===\n")
            f.write(f"完整文本: {result['text'][:100]}...\n\n")
            
            for sent in result['sentences'][:5]:
                f.write(f"说话人: {sent['speaker']}\n")
                f.write(f"时间段: {sent['start_ms']}-{sent['end_ms']}ms\n")
                f.write(f"内容: {sent['text']}\n\n")

def process_asr_file(input_file: str, output_dir: str, json_filename: str, txt_filename: str, logger: logging.Logger) -> bool:
    """
    处理单个ASR文件
    
    Args:
        input_file: 输入文件路径
        output_dir: 输出目录
        json_filename: JSON文件名
        txt_filename: 文本文件名
        logger: 日志记录器
        
    Returns:
        bool: 处理是否成功
    """
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        results = parse_asr_data(data)
        save_results(results, output_dir, json_filename, txt_filename)
        
        logger.info(f"文件处理成功: {input_file}")
        return True
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON解析错误: {e}")
    except (SyntaxError, ValueError) as e:
        logger.error(f"AST解析错误: {e}")
    except Exception as e:
        logger.error(f"处理文件时发生错误: {e}")
    
    return False

def parse_arguments() -> argparse.Namespace:
    """
    解析命令行参数
    
    Returns:
        args: 解析后的参数
    """
    parser = argparse.ArgumentParser(description='解析ASR结果并保存到指定目录')
    parser.add_argument('--input-prefix', '-i', type=str, default="data/asr_result",
                      help='输入的JSON文件前缀 (默认: data/asr_result)')
    parser.add_argument('--output', '-o', type=str, default="data/parsed_results",
                      help='输出目录路径 (默认: data/parsed_results)')
    parser.add_argument('--start', '-s', type=int, default=1,
                      help='起始文件编号 (默认: 1)')
    parser.add_argument('--end', '-e', type=int, default=46,
                      help='结束文件编号 (默认: 46)')
    parser.add_argument('--json-suffix', '-j', type=str, default=".json",
                      help='输出的JSON文件后缀 (默认: .json)')
    parser.add_argument('--txt-suffix', '-t', type=str, default=".txt",
                      help='输出的文本文件后缀 (默认: .txt)')
    return parser.parse_args()

def main():
    """主函数"""
    args = parse_arguments()
    logger = setup_logging()
    
    success_count = 0
    failure_count = 0
    
    for i in range(args.start, args.end + 1):
        input_file = f"{args.input_prefix}{i}.json"
        json_filename = f"parsed_asr_result{i}{args.json_suffix}"
        txt_filename = f"parsed_asr_result{i}{args.txt_suffix}"
        
        logger.info(f"正在处理文件: {input_file}")
        
        if process_asr_file(input_file, args.output, json_filename, txt_filename, logger):
            success_count += 1
        else:
            failure_count += 1
    
    logger.info(f"处理完成 - 成功: {success_count}, 失败: {failure_count}")
    if failure_count > 0:
        logger.error(f"有{failure_count}个文件处理失败")

if __name__ == "__main__":
    main()