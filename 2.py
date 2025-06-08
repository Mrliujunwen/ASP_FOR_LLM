from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
import json
if __name__ == '__main__':
    audio_in = '/mnt/g/download/02.4K.H265.AAC-YYDS.mp4'
    output_dir = "/mnt/g/download/results2"
    inference_pipeline = pipeline(
        task=Tasks.auto_speech_recognition,
        model='iic/speech_paraformer-large-vad-punc-spk_asr_nat-zh-cn',
        model_revision='v2.0.4',
        vad_model='iic/speech_fsmn_vad_zh-cn-16k-common-pytorch', vad_model_revision="v2.0.4",
        punc_model='iic/punc_ct-transformer_cn-en-common-vocab471067-large', punc_model_revision="v2.0.4",
        output_dir=output_dir,
    )
    for i in range(10,49):
        audio_in = f'/mnt/g/download/mv/{str(i).zfill(2)}.4K.H265.AAC-YYDS.mp4'
        print(audio_in)
        rec_result = inference_pipeline(audio_in, batch_size_s=300, batch_size_token_threshold_s=40)
        print(rec_result)
        json_output_path = f"{output_dir}/asr_result{i}.json"
        with open(json_output_path, 'w', encoding='utf-8') as f:
            if isinstance(rec_result, dict):
                print("rec_result",rec_result)
                json.dump(rec_result, f, ensure_ascii=False, indent=2)
            elif isinstance(rec_result, str):
                # 如果结果是纯文本，将其转换为简单的字典格式
                json.dump({"text": rec_result}, f, ensure_ascii=False, indent=2)
            else:
                json.dump({"text": str(rec_result)}, f, ensure_ascii=False, indent=2)
        
        print(f"识别结果已保存到: {json_output_path}")