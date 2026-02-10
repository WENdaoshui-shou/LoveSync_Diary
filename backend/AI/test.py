import os
from dotenv import load_dotenv
import requests

# 加载环境变量
load_dotenv()

# 获取配置信息
api_key = "sk-144ab1b657534ed9890e679ab013704c"
base_url = os.getenv('DASHSCOPE_BASE_URL')
model = os.getenv('DASHSCOPE_MODEL')

# 检查配置是否完整
if not all([api_key, base_url, model]):
    print('错误：配置信息不完整，请检查.env文件')
    exit(1)

print('配置信息：')
print(f'API Key: {api_key}')
print(f'Base URL: {base_url}')
print(f'Model: {model}')
print('-' * 50)

# 测试连接大模型
def test_model_connection():
    print('测试连接大模型...')
    
    # 构建请求数据
    data = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": "你好，我是测试用户，请问你是谁？"
            }
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    # 构建请求头
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    try:
        # 发送请求
        response = requests.post(
            base_url + "/chat/completions",
            json=data,
            headers=headers,
            timeout=30
        )
        
        # 检查响应状态
        if response.status_code == 200:
            # 解析响应
            result = response.json()
            
            # 打印响应结果
            print('\n测试成功！模型响应：')
            print(result['choices'][0]['message']['content'])
            print('\n完整响应：')
            print(result)
        else:
            print(f'\n测试失败！状态码：{response.status_code}')
            print(f'错误信息：{response.text}')
            
    except Exception as e:
        print(f'\n测试失败！发生异常：{str(e)}')

# 运行测试
if __name__ == "__main__":
    test_model_connection()
