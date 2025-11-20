import os
import openai

def call_doubao_api(messages, api_key=None, model=None, tools=None, reasoning_effort="low"):
    """
    Args:
        messages: 消息列表
        api_key: API密钥（可选，如果未提供会从环境变量读取）
        model: 模型名称(ep名字)
        tools: 工具描述列表（用于函数调用）
        reasoning_effort: 推理努力程度（"low", "medium", "high"）
        
    Returns:
        dict: API响应结果
    """
    if not api_key:
        api_key = os.getenv("DOUBAO_API_KEY")
    
    if not api_key:
        return {
            "status": "error",
            "message": "未提供豆包API密钥"
        }
    
    try:
        client = openai.OpenAI(
            base_url="https://ark.cn-beijing.volces.com/api/v3",
            api_key=api_key
        )
        
        request_params = {
            "model": model,
            "messages": messages,
            "temperature": 0.7,
            "reasoning_effort": reasoning_effort
        }
        
   
        if tools:
            request_params["tools"] = tools
            request_params["tool_choice"] = "auto"  
        
   
        completion = client.chat.completions.create(**request_params)
        
    
        message = completion.choices[0].message
        
     
        reasoning_content = ""
        
   
        if hasattr(message, 'reasoning_content'):
            reasoning_content = message.reasoning_content
        elif hasattr(completion, 'model_extra') and isinstance(completion.model_extra, dict):
            reasoning_content = completion.model_extra.get('reasoning_content', '')
        elif hasattr(completion, 'choices') and completion.choices and len(completion.choices) > 0:
            if hasattr(completion.choices[0], 'model_extra') and isinstance(completion.choices[0].model_extra, dict):
                reasoning_content = completion.choices[0].model_extra.get('reasoning_content', '')
        
        response_data = {
            "status": "success",
            "content": message.content or '',
            "reasoning_content": reasoning_content,
            "model": model,
            "usage": completion.usage if hasattr(completion, 'usage') else {}
        }
        
      
        if hasattr(message, 'tool_calls') and message.tool_calls:
            response_data["tool_calls"] = [
                {
                    "id": tool_call.id,
                    "type": "function",
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments
                    }
                }
                for tool_call in message.tool_calls
            ]
        
        return response_data
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"豆包API调用失败: {str(e)}"
        }

def get_llm_response(messages, provider=None, api_key=None, tools=None, reasoning_effort="low"):
    """
    获取豆包模型响应的接口
    
    Args:
        messages: 消息列表
        provider: 豆包模型的ep名字（必填）
        api_key: API密钥
        tools: 工具描述列表（用于函数调用）
        reasoning_effort: 推理努力程度（"low", "medium", "high"）
        
    Returns:
        dict: LLM响应结果
    """
    # provider直接作为模型名称(ep名字)使用
    if not provider:
        return {
            "status": "error",
            "message": "provider参数为必填，需要提供豆包模型的ep名字"
        }
    
    # 直接调用豆包API
    return call_doubao_api(messages, api_key, provider, tools, reasoning_effort)

# 工具信息
tool_info = {
    "name": "get_llm_response",
    "description": "豆包模型API调用接口，provider参数需要传入具体的ep名字",
    "function": get_llm_response
}