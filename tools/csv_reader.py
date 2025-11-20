import pandas as pd
import json

def read_csv_info(file_path):
    """
    读取CSV文件的基本信息，包括行列数、列名等
    
    Args:
        file_path: CSV文件路径
        
    Returns:
        dict: 包含文件信息的字典
    """
    try:
        # 读取CSV文件
        df = pd.read_csv(file_path)
        
        # 获取基本信息
        info = {
            "status": "success",
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": list(df.columns),
            "data_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "sample_data": df.head(3).to_dict('records')
        }
        
        return info
        
    except FileNotFoundError:
        return {
            "status": "error",
            "message": f"文件未找到: {file_path}"
        }
    except Exception as e:
        return {
            "status": "error", 
            "message": f"读取文件时发生错误: {str(e)}"
        }

# 工具信息
tool_info = {
    "name": "read_csv_info",
    "description": "读取CSV文件的基本信息，包括行列数、列名等",
    "function": read_csv_info,
    "parameters": {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "CSV文件路径"
            }
        },
        "required": ["file_path"]
    }
}