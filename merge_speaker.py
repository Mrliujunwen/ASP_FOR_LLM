import json
import os
import logging
from typing import Dict, List, Optional
from pathlib import Path

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
    log_file = os.path.join(log_dir, "merge_speaker.log")
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def merge_sentences(sentences: List[Dict], time_threshold: int = 2000) -> List[Dict]:
    """
    合并连续的相同说话人的句子
    
    Args:
        sentences: 原始句子列表
        time_threshold: 时间间隔阈值（毫秒）
    
    Returns:
        merged_sentences: 合并后的句子列表
    """
    merged_sentences = []
    current_group = None
    
    for sentence in sentences:
        # 如果是第一句话或者说话人变了或者时间间隔过大，创建新组
        if (current_group is None or 
            current_group['speaker'] != sentence['speaker'] or
            sentence['start_ms'] - current_group['end_ms'] > time_threshold):
            
            if current_group is not None:
                merged_sentences.append(current_group)
            
            current_group = {
                'speaker': sentence['speaker'],
                'text': sentence['text'],
                'start_ms': sentence['start_ms'],
                'end_ms': sentence['end_ms'],
                'segments': [{
                    'text': sentence['text'],
                    'start_ms': sentence['start_ms'],
                    'end_ms': sentence['end_ms']
                }]
            }
        else:
            # 合并连续的对话
            current_group['text'] += ' ' + sentence['text']
            current_group['end_ms'] = sentence['end_ms']
            current_group['segments'].append({
                'text': sentence['text'],
                'start_ms': sentence['start_ms'],
                'end_ms': sentence['end_ms']
            })
    
    # 添加最后一组
    if current_group is not None:
        merged_sentences.append(current_group)
    
    return merged_sentences

def save_results(merged_results: List[Dict], output_file: str) -> None:
    """
    保存合并结果
    
    Args:
        merged_results: 合并后的结果
        output_file: 输出文件路径
    """
    # 保存JSON格式
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(merged_results, f, ensure_ascii=False, indent=2)
    
    # 保存文本格式
    text_output = output_file.rsplit('.', 1)[0] + '.txt'
    with open(text_output, 'w', encoding='utf-8') as f:
        for item in merged_results:
            f.write(f"\n=== 文件: {item['key']} ===\n\n")
            
            for sentence in item['merged_sentences']:
                f.write(f"说话人: {sentence['speaker']}\n")
                f.write(f"时间段: {sentence['start_ms']}-{sentence['end_ms']}ms\n")
                f.write(f"内容: {sentence['text']}\n\n")
            f.write("-" * 80 + "\n")

def process_file(input_file: str, output_file: str, logger: logging.Logger) -> bool:
    """
    处理单个文件
    
    Args:
        input_file: 输入文件路径
        output_file: 输出文件路径
        logger: 日志记录器
    
    Returns:
        bool: 处理是否成功
    """
    try:
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # 读取原始数据
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        merged_results = []
        for item in data:
            sentences = item.get('sentences', [])
            merged_sentences = merge_sentences(sentences)
            
            merged_item = {
                'key': item.get('key', ''),
                'text': item.get('text', ''),
                'merged_sentences': merged_sentences
            }
            merged_results.append(merged_item)
        
        save_results(merged_results, output_file)
        logger.info(f"文件处理成功: {input_file}")
        return True
        
    except Exception as e:
        logger.error(f"处理文件时发生错误: {e}")
        return False

def main():
    """主函数"""
    logger = setup_logging()
    
    success_count = 0
    failure_count = 0
    
    for i in range(1, 47):
        input_file = f"data/parsed_results/parsed_asr_result{i}.json"
        output_file = f"data/merge_results/merged_asr_result{i}.json"
        
        logger.info(f"正在处理文件: {input_file}")
        
        if process_file(input_file, output_file, logger):
            success_count += 1
        else:
            failure_count += 1
    
    logger.info(f"处理完成 - 成功: {success_count}, 失败: {failure_count}")
    if failure_count > 0:
        logger.error(f"有{failure_count}个文件处理失败")

if __name__ == "__main__":
    main() 