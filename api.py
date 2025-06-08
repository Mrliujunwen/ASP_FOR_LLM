import aiohttp
import asyncio
import logging
import json
from tqdm import tqdm
from datetime import datetime
import os
import random
from pathlib import Path
from typing import List, Dict, Any
# 现代角色库（可自由扩展）
MODERN_ROLES = [
    # 教育场景
    {"role": "高中生", "traits": ["青涩", "网络用语", "求知欲"], "examples": ["这道题怎么解？", "老师能不能划重点？"]},
    {"role": "大学教授", "traits": ["严谨", "学术化", "权威"], "examples": ["根据最新研究...", "这个理论有三个漏洞"]},
    {"role": "留学顾问", "traits": ["信息差", "焦虑贩卖", "话术套路"], "examples": ["背景提升很重要", "Top 50院校保录取"]},
    {"role": "网课助教", "traits": ["机械回复", "模板化", "拖延应对"], "examples": ["这个问题已记录", "请查看公告区FAQ"]},

    # 职场场景
    {"role": "程序员", "traits": ["直接", "技术术语", "务实"], "examples": ["这个需求有技术债", "API返回500错误"]},
    {"role": "HR经理", "traits": ["圆滑", "政策敏感", "协调"], "examples": ["公司目前headcount冻结", "你的期望薪资是？"]},
    {"role": "产品经理", "traits": ["画饼", "抽象需求", "甩锅倾向"], "examples": ["这个功能很简单", "技术实现我不管"]},
    {"role": "创业CEO", "traits": ["打鸡血", "融资术语", "风险转移"], "examples": ["我们在Pre-A轮", "期权比现金更有价值"]},
    {"role": "外包员工", "traits": ["卑微", "边界感强", "工时精确"], "examples": ["需求要加钱", "合同里没写这部分"]},

    # 日常生活
    {"role": "家庭主妇", "traits": ["生活化", "细节控", "情感化"], "examples": ["超市土豆涨价了", "孩子班主任来电话了"]},
    {"role": "健身教练", "traits": ["激励", "专业术语", "强势"], "examples": ["再做最后一组！", "你体脂率偏高"]},
    {"role": "广场舞领队", "traits": ["嗓门大", "辈分压制", "资源整合"], "examples": ["小王把音响搬过来", "李姐认识街道办的"]},
    {"role": "密室NPC", "traits": ["戏精", "规则守护", "突然惊吓"], "examples": ["欢迎来到亡灵古堡...", "禁止触碰道具！"]},
    {"role": "二手房东", "traits": ["话术陷阱", "临时加价", "装穷"], "examples": ["押金不退是行规", "我也要还房贷啊"]},

    # 新兴行业
    {"role": "带货主播", "traits": ["饥饿营销", "夸张表演", "价格对比"], "examples": ["最后三单秒杀！", "原价899今天99"]},
    {"role": "电竞选手", "traits": ["手速炫耀", "战术黑话", "年轻气盛"], "examples": ["这波我1v5", "对面打野在偷龙"]},
    {"role": "汉服妆娘", "traits": ["古风腔", "考据癖", "强迫症"], "examples": ["唐制襦裙不能配明制头饰", "你的发包没藏好"]},
    {"role": "宠物殡葬师", "traits": ["温柔克制", "仪式感强", "回避直白"], "examples": ["它只是去彩虹桥了", "可以留下爪印纪念"]},

    # 特殊群体
    {"role": "朝阳群众", "traits": ["警惕性高", "线索联想", "热心过度"], "examples": ["那家阳台有可疑盆栽", "我帮你联系居委会"]},
    {"role": "环球旅行家", "traits": ["凡尔赛", "攻略达人", "风险淡化"], "examples": ["叙利亚其实很安全", "办签证要准备20项材料"]},
    {"role": "玄学博主", "traits": ["模棱两可", "灾难预言", "付费解锁"], "examples": ["你命中有贵人相助", "详情请扫码咨询"]},
    {"role": "奥赛教练", "traits": ["智商碾压", "题海战术", "解谜快感"], "examples": ["用群论解这道小学奥数", "通宵做完这本题集"]},
  {"role": "留学枪手", "traits": ["代笔专家", "焦虑刺激", "文书模板化"], "examples": ["哈佛录取书都出自我的手", "你科研经历太水要包装"]},
  {"role": "考研占座党", "traits": ["资源垄断", "早起疯魔", "领地意识"], "examples": ["五楼第三座我贴了封条", "抢座请扫码支付定金"]},
  {"role": "专升本顾问", "traits": ["学历歧视", "逆袭鸡汤", "考点玄学"], "examples": ["三本考生要避开这些院校", "你专科背景被刷概率90%"]},
  
  # 职场延伸类（20个）
  {"role": "大厂PPT纺织工", "traits": ["造词成瘾", "对齐意识", "美学强迫"], "examples": ["第五页缺个生态闭环模型", "字间距必须用1.15倍"]},
  {"role": "流水线诗人", "traits": ["麻木创作", "机械浪漫", "产量至上"], "examples": ["螺丝钉的弧光刺痛流水线", "今天KPI是三千首诗"]},
  {"role": "职业背锅侠", "traits": ["危机转嫁",  "表演愧疚", "甩锅话术"], "examples": ["这次事故全是我流程失误", "主程代码其实我改过"]},
  {"role": "钉钉恐吓师", "traits": ["已读施压", "截止日恐吓", "表情包威胁"], "examples": ["@所有人 凌晨两点交周报", "微笑.jpg意味着你完了"]},
  
  # 市井生活类（20个）
  {"role":  "相亲简历化妆师", "traits": ["身高膨胀", "薪资注水", "兴趣造假"], "examples": ["165cm建议写173cm", "手游代练包装成电竞顾问"]},
  {"role": "小区情报局长", "traits": ["监控窃听",  "关系图谱", "线索加工"], "examples": ["302业主昨晚带了绿发女孩", "他家快递量暗示在搞传销"]},
  {"role": "流浪猫总裁", "traits": ["领地划分",  "投喂PUA", "绝育霸权"], "examples": ["橘座批准你停在这车位", "不割蛋休想摸白手套"]},
  {"role":  "广场WiFi猎人", "traits": ["信号追踪",  "密码破解", "流量劫持"], "examples": ["老年活动中心有满格5G", "连我热点看跳舞视频收费"]},
  
  # 新兴领域类（20个）
  {"role":  "元宇宙包工头", "traits": ["虚拟施工", "链上结算", "沙盒画饼"], "examples": ["区块链海滩别墅打地基", "ETH付款赠NFT房产证"]},
  {"role": "电竞伤痛师", "traits": ["职业病崇拜", "绷带美学", "轮椅营销"], "examples": ["这手伤是冠军的勋章", "腱鞘炎贴买二送一"]},
  {"role":  "盲盒占卜师", "traits": ["概率操控",  "饥饿玄学", "潮玩通灵"], "examples": ["水晶球显示隐藏款在右下角", "端整箱才配得上你星座"]},
  {"role":  "AI饲养员", "traits": ["算法投喂", "模型驯化", "数据洁癖"], "examples": ["别给模型喂劣质微博语料", "今晚加训100TB古籍"]},
  
  # 边缘职业类（20个）
  {"role":  "阴间房产中介", "traits": ["风水恐吓",  "墓地通胀", "孝道绑架"], "examples": ["西山墓园三年涨了300%", "不买连体穴就是不孝"]},
  {"role": "离婚庆典司仪", "traits": ["黑色幽默",  "砸盘狂欢", "分割艺术"], "examples": ["有请新郎剪断同心结！", "前妻戒指现在1元起拍"]},
  {"role":  "职业试睡师", "traits": ["灵异营销",  "唯物主义",  "剧本编剧"], "examples": ["昨夜红衣女鬼挠门三下", "床底藏符加收200元"]},
  {"role":  "外卖拳击手", "traits": ["超时狂暴",  "差评追杀",  "爬楼竞速"], "examples": ["电梯坏了？28楼我跑赢了狗", "给差评知道你公司门牌"]},
   {"role": "迷糊小学生", "traits": ["作业遗忘", "拼音混用", "告状依赖"], "examples": ["老师他把我橡皮切成渣了", "作文写《我的省长爸爸》被撕了"]},
  {"role": "奥数神童", "traits": ["降维打击", "符号入脑", "社交障碍"], "examples": ["用微积分给同桌讲鸡兔同笼", "课间操是浪费时间证明"]},
  
  {"role": "文科班戏精", "traits": ["历史剧沉浸", "政治梗滥用", "论述题加戏"], "examples": ["这道地理题像极了项羽乌江自刎", "用甄嬛体写鸦片战争意义"]},
  {"role": "竞赛党", "traits": ["保送执念",  "熬夜冠军",  "凡尔赛叫苦"], "examples": ["化竞题简单到只需背800种试剂", "生物复赛前夜通宵看细胞分裂"]},
  
  {"role": "英语专业生", "traits": ["中英混杂", "原版书炫技", "翻译腔入骨"], "examples": ["这篇essay的thesis缺乏coherence", "把食堂菜单译成十四行诗"]},
  {"role": "土木牛马", "traits": ["工地PTSD",  "转行焦虑",  "力学魔怔"], "examples": ["混凝土配比影响我吃饭咸淡", "实习后看宿舍楼都算承重墙"]},
  
  {"role": "数学老顽童", "traits": ["冷笑话解题", "尺规成瘾", "鄙视计算器"], "examples": ["这道圆锥曲线是嫦娥奔月轨迹", "口算开立方是基本素养"]},
  {"role": "物理梗王", "traits": ["生活万物皆杠杆", "暴力拆题", "能量守恒洗脑"], "examples": ["你早恋的熵值需要外力干预", "用动量定理分析食堂插队"]},
  
  {"role": "语文诗人", "traits": ["作文即兴评", "咬文嚼字", "主观题玄学"], "examples": ["把《滕王阁序》唱成rap才给过", "赏析作者放屁的深层意图"]},
  {"role": "历史八卦精", "traits": ["野史乱入", "帝王CP脑", "考试重点谜语"], "examples": ["朱元璋删帖是因为自卑心理", "下节考李鸿章美妆博主时期"]},
  
  {"role": "食堂战神", "traits": ["颠勺美学",  "帕金森打菜", "剩菜哲学"], "examples": ["番茄炒蛋找蛋要量子波动速读", "三块肉是食堂最大公约数"]},
  {"role": "宿舍暴君", "traits": ["查寝双标", "违章电器猎手", "钥匙霸权"], "examples": ["卷发棒藏消防栓扣集体分", "23:01锁门天王老子也得等"]},
  
  {"role": "考场灵媒", "traits": ["玄学猜题", "文具开光", "概率论自杀"], "examples": ["涂答题卡前掷骰子更准", "挂柯南海报贴床头必挂科"]},
  {"role": "论文裁缝", "traits": ["降重话术",  "翻译倒卖",  "数据美化"], "examples": ["把新冠改成新型冠状病毒肺炎", "用伊拉克气温证明东北供暖"]}
  
]
# 配置日志
def setup_logging(log_dir="./logs", log_level=logging.INFO, show_logs=True):
    """设置日志配置"""
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"{log_dir}/qwen7b_processing_{timestamp}.log"

    handlers = [logging.FileHandler(log_file, encoding='utf-8')]
    if show_logs:
        handlers.append(logging.StreamHandler())

    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=handlers
    )

    return logging.getLogger()


logger = setup_logging()

async def analyze_feedback(feedback_content):
    """
    Analyze a single feedback entry using LLM
    """
    try:
        # Clean up the response if it contains code block formatting
        clean_response = feedback_content
        if clean_response.startswith('```json'):
            clean_response = clean_response[7:]  # Remove ```json prefix
        if clean_response.startswith('```'):
            clean_response = clean_response[3:]  # Remove ``` prefix
        if clean_response.endswith('```'):
            clean_response = clean_response[:-3]  # Remove ``` suffix
        if clean_response.startswith('```python'):
            clean_response = clean_response[7:]  # Remove ```json prefix
        if clean_response.startswith('```'):
            clean_response = clean_response[3:]  # Remove ``` prefix
        if clean_response.endswith('```'):
            clean_response = clean_response[:-3]  # Remove ``` suffix
        # Parse the cleaned JSON
        # logger.info(f"clean_response: {clean_response}")
        result = json.loads(clean_response)
        # logger.info(f"result: {result}")

        return result
    except Exception as e:
        clean_response = json.dumps(clean_response, ensure_ascii=False)
        return json.loads(clean_response)
async def generate_role_prompt(question):
    """生成带随机角色的prompt"""
    selected_role = random.choice(MODERN_ROLES)
    
    return f"""
## 角色
- 你是一个资深的语言大师，精通各行各业的语言
## 任务
- 你来判断以下输入的是不是皇上说的话，是的话返回是，不是则不是
- 以下是输入的内容
{question["input"]}

## 输出格式
- 标注json格式
- 不要输出其他任何东西
 {{
    "is_emperor":""//是或者不是
 }}
""".strip()
class AsyncQwenCaller:
    def __init__(self, max_concurrent=5, max_retries=3):
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
        self.datas = []

    async def __aenter__(self):
        timeout = aiohttp.ClientTimeout(total=600, connect=10)
        self.session = aiohttp.ClientSession(timeout=timeout)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.session.close()

    async def _call_api(self, question: dict, retry_count=0) -> dict:
        """实际调用API的异步方法，带重试机制"""
        try:
            data = {
                "model": "Qwen2.5",
                "messages": [
                    {"role": "user", "content":await generate_role_prompt(question)}
                ],
                "temperature": 0.7,
                "max_tokens": 4096 * 4
            }

            async with self.session.post(self.url, headers=self.headers, json=data) as response:
                response_json = await response.json()
                response_data = response_json["choices"][0]["message"].get("content")
                # logger.info(f"回答: {response_data}")
                # logger.info("-" * 50)

                # question["answer_7b"] = response_data
                return response_data

        except Exception as e:
            if retry_count < self.max_retries:
                wait_time = 2 ** retry_count  # 指数退避
                # logger.warning(f"请求失败，{wait_time}秒后重试... (错误: {str(e)})")
                await asyncio.sleep(wait_time)
                return await self._call_api(question, retry_count + 1)
            # logger.error(f"处理问题 '{question['question']}' 时发生错误: {str(e)}")
            return question

    async def _execute_call(self, question: dict, task_id: int):
        """实际执行调用的内部方法"""
        try:
            result = await self._call_api(question)
            result = await analyze_feedback(result)
            self.datas.append(result)
            if self.progress_bar:
                self.progress_bar.update(1)
                self.processed_count += 1
        except Exception as e:
            # logger.error(f"任务 {task_id} 执行失败: {str(e)}")
            if self.progress_bar:
                self.progress_bar.update(1)
                self.processed_count += 1

    async def process_question(self, question: dict, task_id: int):
        """处理单个问题"""
        while len(self._running_tasks) >= self.max_concurrent:
            done, _ = await asyncio.wait(
                self._running_tasks,
                return_when=asyncio.FIRST_COMPLETED
            )
            self._running_tasks -= done

        task = asyncio.create_task(self._execute_call(question, task_id))
        self._running_tasks.add(task)
        task.add_done_callback(self._running_tasks.discard)

    def set_progress_bar(self, total):
        """设置进度条"""
        self.total_count = total
        self.progress_bar = tqdm(total=total, desc="处理问题", unit="个")

    def close_progress(self):
        """关闭进度条"""
        if self.progress_bar:
            self.progress_bar.close()


async def main(input_file: str, output_dir: str, max_concurrent: int = 5, batch_size: int = 100):
    for j in range(batch_size):
        questions=[]
        with open(input_file, "r", encoding="utf-8") as f:
            data=json.load(f)
            for i in data:
                questions.append(i)
        # for line in f:
        #     try:
        #         question = json.loads(line)
        #         questions.append(question)
        #     except json.JSONDecodeError:
        #         logger.warning(f"跳过无效的JSON行: {line[:50]}...")

        # logger.info(f"共读取 {len(questions)} 条问题记录")

        # 异步处理问题
        async with AsyncQwenCaller(max_concurrent=max_concurrent) as caller:
            caller.set_progress_bar(len(questions))

            tasks = []
            for i, question in enumerate(questions):
                task = caller.process_question(question, i + 1)
                tasks.append(task)

            # 等待所有任务完成
            await asyncio.gather(*tasks, return_exceptions=True)

            # 等待剩余的任务完成
            if caller._running_tasks:
                await asyncio.wait(caller._running_tasks)

            caller.close_progress()

            # 写入结果
            batch_output = Path(output_dir) / f"batch_{j+1}.json"

            with open(batch_output, "w", encoding="utf-8") as f:
                for data in caller.datas:
                    f.write(json.dumps(data, ensure_ascii=False) + "\n")

        logger.info(f"所有批次处理完成，共生成 {batch_size} 个batch文件")
if __name__ == "__main__":
   
    input_file = f"input/train_data.json"
    output_file = f"output3"
    asyncio.run(main(input_file, output_file, max_concurrent=64,batch_size=100))
