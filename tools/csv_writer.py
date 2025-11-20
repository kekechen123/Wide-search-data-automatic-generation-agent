import pandas as pd
import os
from datetime import datetime

def write_to_csv(file_path, query, answer):
    """
    将问题和答案写入CSV文件的query和answer两列（仅支持追加写入）
    
    Args:
        file_path: 目标CSV文件路径
        query: 问题字符串
        answer: 答案字符串
        
    Returns:
        dict: 包含写入结果的字典
    """
    try:
        # 定义固定的列标题
        headers = ['query', 'answer']
        
        # 检查文件是否存在
        file_exists = os.path.exists(file_path)
        
        # 准备数据
        data = [[query, answer]]
        
        if file_exists:
            # 读取现有文件
            existing_df = pd.read_csv(file_path)
            
            # 创建新的数据框
            new_df = pd.DataFrame(data, columns=headers)
            
            # 追加数据
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            
            # 保存文件
            combined_df.to_csv(file_path, index=False)
            
            return {
                "status": "success",
                "message": f"成功追加1行问答数据到文件",
                "total_rows": len(combined_df),
                "file_path": file_path
            }
        else:
            # 创建新文件
            new_df = pd.DataFrame(data, columns=headers)
            
            # 保存文件
            new_df.to_csv(file_path, index=False)
            
            return {
                "status": "success",
                "message": f"成功创建新文件并写入1行问答数据",
                "total_rows": len(new_df),
                "file_path": file_path
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"写入数据时发生错误: {str(e)}"
        }

# 工具信息
tool_info = {
    "name": "write_to_csv",
    "description": "将问题和答案写入CSV文件的query和answer两列",
    "function": write_to_csv,
    "parameters": {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "目标CSV文件路径"
            },
            "query": {
                "type": "string",
                "description": "问题文本"
            },
            "answer": {
                "type": "string",
                "description": "答案文本"
            }
        },
        "required": ["file_path", "query", "answer"]
    }
}