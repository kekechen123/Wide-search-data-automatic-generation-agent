import uuid
from tools import tools_info
import argparse
import json
import os
import sys
from datetime import datetime

from get_llm import get_llm_response
from tools import get_tool_function

def load_system_prompt():
    """加载系统提示词"""
    try:
        with open('prompt.txt', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print("警告：未找到prompt.txt文件，使用默认提示词")
        return "你是一个智能表格处理助手，能够帮助用户处理CSV文件数据。"

def load_tools_description():
    """加载工具描述"""
    try:
        with open('tools.json', 'r', encoding='utf-8') as f:
            tools_data = json.load(f)
            return json.dumps(tools_data, ensure_ascii=False, indent=2)
    except FileNotFoundError:
        print("警告：未找到tools.json文件")
        return ""

def parse_function_call(response_content, response_data=None):
    """解析LLM响应中的函数调用，优先从 response_data 的结构读取（并返回可能的 tool_call id）"""
    try:
        if response_data and isinstance(response_data, dict) and "tool_calls" in response_data:
            tool_calls = response_data.get("tool_calls") or []
            if tool_calls:
                tool_call = tool_calls[0]
                func_info = tool_call.get("function", {}) or {}
                args_raw = func_info.get("arguments")
                if isinstance(args_raw, str):
                    try:
                        args = json.loads(args_raw)
                    except Exception:
                        args = args_raw
                else:
                    args = args_raw
                tool_call_id = tool_call.get("id") or tool_call.get("tool_call_id") or tool_call.get("call_id")
                return {
                    "name": func_info.get("name"),
                    "arguments": args or {},
                    "id": tool_call_id
                }

        if response_content and "{" in response_content and "}" in response_content:
            start = response_content.find("{")
            end = response_content.rfind("}") + 1
            json_str = response_content[start:end]
            function_call = json.loads(json_str)
            # 返回保证格式
            return {
                "name": function_call.get("name"),
                "arguments": function_call.get("arguments", {})
            }

        return None

    except json.JSONDecodeError:
        return None
    except Exception as e:
        print(f"解析函数调用时出错: {e}")
        return None


def execute_tool(function_name, function_args):
    """执行工具函数"""
    try:
    
        tool_func = get_tool_function(function_name)
        
        if not tool_func:
            return {
                "status": "error",
                "message": f"未找到工具函数: {function_name}"
            }
     
        result = tool_func(**function_args)
        return result
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"执行工具函数时出错: {str(e)}"
        }


def ensure_dict(obj):
    """确保 obj 是 dict；如果是 JSON 字符串尝试解析；否则返回空 dict"""
    if obj is None:
        return {}
    if isinstance(obj, dict):
        return obj
    if isinstance(obj, str):
        try:
            parsed = json.loads(obj)
            if isinstance(parsed, dict):
                return parsed
            else:
                return {}
        except Exception:
            return {}
    return {}

def run_agent(user_input, csv_file, max_rounds=10, provider=None, api_key=None, output_file=None):
    """运行agent主循环"""
    
    print(f"\n{'='*60}")
    print(f"开始处理任务")
    print(f"CSV文件: {csv_file}")
    print(f"用户需求: {user_input}")
    print(f"最大轮次: {max_rounds}")
    print(f"LLM模型: {provider}")
    print(f"{'='*60}\n")
    
    system_prompt = load_system_prompt()
    

    combined_user_input = f"{user_input}\n\nCSV_PATH: {csv_file}"
    
    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": combined_user_input
        }
    ]
    # 保存当前用户消息，便于后续 trace 使用（避免 messages[-1] 位置不稳）
    last_user_message = messages[-1]["content"]
    
    # 决定向 messages 中追加函数/工具执行结果时用哪个 role
    # OpenAI 风格使用 "function"；豆包(doubao) 等需要使用 "tool"

    function_message_role = "tool"

    
    tools_openai_format = []
    for tool in tools_info:
        tools_openai_format.append({
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool.get("description"),
                "parameters": tool.get("parameters")
            }
        })
    
    work_trace = []
    
    for round_num in range(max_rounds):
        print(f"\n--- 第 {round_num + 1} 轮 ---")
        
        
        print("正在调用LLM API...")
        response = get_llm_response(messages, provider, api_key, tools=tools_openai_format)

        if not isinstance(response, dict):
            print("LLM 返回格式异常，预期 dict。")
            break

        if response.get("status") == "error":
            print(f"LLM API调用失败: {response.get('message')}")
            break

        assistant_message = response.get("content", "") or ""
        reasoning_content = response.get("reasoning_content", "") or ""

        function_call = parse_function_call(assistant_message, response)
        if function_call:
 
            assistant_msg_obj = {
                "role": "assistant",
 
                "content": "",
             
                "function_call": {
                    "name": function_call.get("name"),
                    "arguments": json.dumps(function_call.get("arguments", {}), ensure_ascii=False)
                }
            }
        else:
            assistant_msg_obj = {
                "role": "assistant",
                "content": assistant_message
            }

        messages.append(assistant_msg_obj)
        

        print(f"LLM响应: {assistant_message[:200]}...")
        if reasoning_content:
            print(f"模型思考: {reasoning_content[:200]}...")
        

        function_call = parse_function_call(assistant_message, response)
        

        model_thought = reasoning_content if reasoning_content else assistant_message
        
        trace_entry = {
            "round": round_num + 1,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "model_thought": model_thought,
            "reasoning_content": reasoning_content,
            "assistant_content": assistant_message,
            "conversation": {
                "user": last_user_message,
                "assistant": assistant_message
            }
        }
        
        if not function_call:
            print("未检测到有效的工具调用，继续对话...")
            trace_entry["type"] = "conversation_only"
            work_trace.append(trace_entry)
        
            continue
        else:
            trace_entry["type"] = "tool_call"
            function_name = function_call.get("name")
            function_args = function_call.get("arguments", {})
            tool_call_id = str(uuid.uuid4())
       
            function_args = ensure_dict(function_args)
            trace_entry["function"] = function_name
            trace_entry["arguments"] = function_args
        
        print(f"检测到工具调用: {function_name}")
        print(f"参数: {json.dumps(function_args, ensure_ascii=False, indent=2)}")
        
        
        if function_name == "write_to_csv" and output_file:
            function_args["file_path"] = output_file
        
        tool_result = execute_tool(function_name, function_args)
        
        print(f"工具执行结果: {json.dumps(tool_result, ensure_ascii=False, indent=2)}")
        

        trace_entry["result"] = tool_result
        work_trace.append(trace_entry)
        
   
        print(f"已记录轮次 {round_num + 1} 的完整信息，包括模型思考、对话内容和工具调用")
        
        # 检查是否完成任务
        if isinstance(tool_result, dict) and tool_result.get("task_finished"):
            print(f"\n✅ 任务已完成: {tool_result.get('message', '')}")
     
            call_id = function_call.get("id") if function_call else str(uuid.uuid4())
            messages.append({
                "role": function_message_role,
                "name": function_name,
                "content": json.dumps(tool_result, ensure_ascii=False, indent=2),
                "tool_call_id": call_id
            })
            break
        
        tool_msg = {
            "role": function_message_role,
            "name": function_name,
            "content": json.dumps(tool_result, ensure_ascii=False, indent=2)
        }

 
        call_id = function_call.get("id") if function_call else None
        if not call_id:
            call_id = str(uuid.uuid4())
        tool_msg["tool_call_id"] = call_id

        messages.append(tool_msg)
        
    else:
        print(f"\n⚠️  已达到最大轮次限制 ({max_rounds})，任务未完成")
    

    print(f"\n{'='*60}")
    print("完整工作轨迹总结:")
    print(f"{'='*60}")
    
    for trace in work_trace:
        print(f"\n轮次 {trace['round']}:")
        print(f"  时间: {trace.get('timestamp', 'N/A')}")
        print(f"  类型: {'工具调用' if trace.get('type') == 'tool_call' else '纯对话'}")
        
  
        if trace.get('reasoning_content'):
            print(f"  模型思考: {trace['reasoning_content'][:500]}{'...' if len(trace['reasoning_content']) > 500 else ''}")
        else:
            mt = trace.get('model_thought', '') or ''
            print(f"  模型思考: {mt[:500]}{'...' if len(mt) > 500 else ''}")
        

        ac = trace.get('assistant_content', '') or ''
        print(f"  助手回复: {ac[:150]}{'...' if len(ac) > 150 else ''}")
        
   
        if trace.get('type') == 'tool_call':
            print(f"  工具名称: {trace.get('function', 'N/A')}")
            args_preview = json.dumps(trace.get('arguments', {}), ensure_ascii=False)
            print(f"  工具参数: {args_preview[:150]}{'...' if len(args_preview) > 150 else ''}")
            print(f"  执行结果: {trace.get('result', {}).get('status', 'unknown')}")
            if 'message' in trace.get('result', {}):
                result_msg = trace['result']['message']
                print(f"  结果消息: {result_msg[:100]}{'...' if len(result_msg) > 100 else ''}")
    
    print(f"\n{'='*60}")
    print(f"总计记录了 {len(work_trace)} 个对话轮次")
    tool_calls = sum(1 for trace in work_trace if trace.get('type') == 'tool_call')
    conversations = len(work_trace) - tool_calls
    print(f"其中工具调用: {tool_calls} 次，纯对话: {conversations} 次")
    print(f"{'='*60}")
    
    return work_trace

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='CSV处理Agent')
    parser.add_argument('csv_file', help='要处理的CSV文件路径')
    parser.add_argument('user_input', help='用户需求描述')
    parser.add_argument('--output', help='输出CSV文件路径，用于指定csv_writer的写入位置')
    parser.add_argument('--max-rounds', type=int, default=10, help='最大工作轮次 (默认: 10)')
    parser.add_argument('--provider', help='LLM模型名称 ')
    parser.add_argument('--api-key', help='API密钥（也可通过环境变量设置）')
    
    args = parser.parse_args()

    if not os.path.exists(args.csv_file):
        print(f"错误: CSV文件 '{args.csv_file}' 不存在")
        sys.exit(1)
    
    if not args.provider:
        print("错误: 必须提供模型名称，请使用 --provider 参数")
        sys.exit(1)
    
    # 运行agent
    try:
        work_trace = run_agent(
            user_input=args.user_input,
            csv_file=args.csv_file,
            max_rounds=args.max_rounds,
            provider=args.provider,
            api_key=args.api_key,
            output_file=args.output
        )
        
        print(f"\n✅ Agent执行完成！")
        
    except KeyboardInterrupt:
        print(f"\n⚠️  用户中断执行")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 执行过程中发生错误: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
