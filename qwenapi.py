import aiohttp
import asyncio
import logging
import json
from tqdm import tqdm
from datetime import datetime
import os
from typing import Dict, List, Optional, Union
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
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"qwen7b_processing_{timestamp}.log")

    handlers = [logging.FileHandler(log_file, encoding='utf-8')]
    handlers.append(logging.StreamHandler())

    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=handlers
    )
    return logging.getLogger(__name__)

async def clean_json_response(response: str) -> Dict:
    """
    清理和解析API响应
    
    Args:
        response: API返回的原始响应
        
    Returns:
        Dict: 解析后的JSON数据
    """
    clean_response = response
    
    # 移除代码块标记
    for prefix in ['```json', '```']:
        if clean_response.startswith(prefix):
            clean_response = clean_response[len(prefix):]
    if clean_response.endswith('```'):
        clean_response = clean_response[:-3]
    
    try:
        return json.loads(clean_response)
    except json.JSONDecodeError:
        # 如果解析失败，尝试将整个响应作为字符串处理
        return json.loads(json.dumps(clean_response, ensure_ascii=False))

class AsyncQwenCaller:
    """异步调用Qwen API的类"""
    
    def __init__(self, max_concurrent: int = 5, max_retries: int = 3):
        """
        初始化API调用器
        
        Args:
            max_concurrent: 最大并发请求数
            max_retries: 最大重试次数
        """
        self.max_concurrent = max_concurrent
        self.max_retries = max_retries
        self.url = "http://localhost:8001/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer YOUR_TOKEN"
        }
        self._running_tasks = set()
        self.processed_count = 0
        self.total_count = 0
        self.progress_bar = None
        self.results = []

    async def __aenter__(self):
        """异步上下文管理器入口"""
        timeout = aiohttp.ClientTimeout(total=600, connect=10)
        self.session = aiohttp.ClientSession(timeout=timeout)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        """异步上下文管理器退出"""
        await self.session.close()

    async def _call_api(self, question: Dict, retry_count: int = 0) -> Dict:
        """
        调用API的核心方法
        
        Args:
            question: 问题数据
            retry_count: 当前重试次数
            
        Returns:
            Dict: API响应数据
        """
        try:
            data = {
                "model": "Qwen2.5",
                "messages": [
                    {"role": "user", "content": f"""
                     你现在来看一下这个内容，这个是orther说的{question["orther"]}，这是huang说的{question["huang"]}，
                    ，理论上这是一个对话，
                    ## 可能存在的错误
                    - 可能有错别字，如果有错别字就给我修改，但是原意不要修改
                    - 可能会有标点符号的错误，如果有，修改标点符号为正确的
                    ## 返回结果
                    - 这俩如果不是一个人和皇上的对话逻辑，那么就返回否
                    - 返回标准的json格式，不要给出其他任何数据
                     
                     {{
                     "result":"是"或者"否"//是否是皇上和orther的对话
                     "input":"修改后的内容"//如果是的话，而且有错别字就修改，如果不是的话就是原话，这是orther说的，里边只能放说的话，不要放其他内容
                     "output":"修改后的内容"//如果是的话，而且有错别字就修改，如果不是的话就是原话，这是huang说的，里边只能放说的话，不要放其他内容
                     }}
                     """}
                ],
                "temperature": 0.7,
                "max_tokens": 4096 * 4
            }

            async with self.session.post(self.url, headers=self.headers, json=data) as response:
                response_json = await response.json()
                response_data = response_json["choices"][0]["message"].get("content")
                logging.info(f"API响应: {response_data}")
                return response_data

        except Exception as e:
            if retry_count < self.max_retries:
                wait_time = 2 ** retry_count  # 指数退避
                logging.warning(f"请求失败，{wait_time}秒后重试... (错误: {str(e)})")
                await asyncio.sleep(wait_time)
                return await self._call_api(question, retry_count + 1)
            logging.error(f"处理问题时发生错误: {str(e)}")
            return question

    async def _execute_call(self, question: Dict, task_id: int) -> None:
        """
        执行单个API调用
        
        Args:
            question: 问题数据
            task_id: 任务ID
        """
        try:
            result = await self._call_api(question)
            result = await clean_json_response(result)
            self.results.append(result)
            if self.progress_bar:
                self.progress_bar.update(1)
                self.processed_count += 1
        except Exception as e:
            logging.error(f"任务 {task_id} 执行失败: {str(e)}")
            if self.progress_bar:
                self.progress_bar.update(1)
                self.processed_count += 1

    async def process_question(self, question: Dict, task_id: int) -> None:
        """
        处理单个问题
        
        Args:
            question: 问题数据
            task_id: 任务ID
        """
        while len(self._running_tasks) >= self.max_concurrent:
            done, _ = await asyncio.wait(
                self._running_tasks,
                return_when=asyncio.FIRST_COMPLETED
            )
            self._running_tasks -= done

        task = asyncio.create_task(self._execute_call(question, task_id))
        self._running_tasks.add(task)
        task.add_done_callback(self._running_tasks.discard)

    def set_progress_bar(self, total: int) -> None:
        """
        设置进度条
        
        Args:
            total: 总任务数
        """
        self.total_count = total
        self.progress_bar = tqdm(total=total, desc="处理问题", unit="个")

    def close_progress(self) -> None:
        """关闭进度条"""
        if self.progress_bar:
            self.progress_bar.close()

async def process_file(input_file: str, output_file: str, max_concurrent: int = 5) -> None:
    """
    处理单个文件
    
    Args:
        input_file: 输入文件路径
        output_file: 输出文件路径
        max_concurrent: 最大并发数
    """
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # 读取输入文件
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        questions = list(data)

    logging.info(f"共读取 {len(questions)} 条问题记录")

    # 异步处理问题
    async with AsyncQwenCaller(max_concurrent=max_concurrent) as caller:
        caller.set_progress_bar(len(questions))

        tasks = []
        for i, question in enumerate(questions):
            task = caller.process_question(question, i + 1)
            tasks.append(task)

        # 等待所有任务完成
        await asyncio.gather(*tasks, return_exceptions=True)
        if caller._running_tasks:
            await asyncio.wait(caller._running_tasks)

        caller.close_progress()

        # 保存结果
        with open(output_file, "w", encoding="utf-8") as f:
            for result in caller.results:
                f.write(json.dumps(result, ensure_ascii=False) + "\n")

        logging.info(f"结果已保存到: {output_file}")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='使用Qwen API处理对话数据')
    parser.add_argument('input_file', help='输入文件路径')
    parser.add_argument('output_file', help='输出文件路径')
    parser.add_argument('--max-concurrent', type=int, default=5, help='最大并发请求数')
    args = parser.parse_args()

    # 设置日志
    logger = setup_logging()
    
    # 运行异步处理
    asyncio.run(process_file(args.input_file, args.output_file, args.max_concurrent))

if __name__ == "__main__":
    main()
