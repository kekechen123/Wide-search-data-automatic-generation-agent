import pandas as pd

def calculate_csv_data(file_path, column, operation, filter_column=None, filter_value=None):
    """
    对CSV数据进行计算操作
    
    Args:
        file_path: CSV文件路径
        column: 要计算的列名
        operation: 计算操作（sum, avg, count, min, max）
        filter_column: 筛选列名（可选）
        filter_value: 筛选值（可选）
        
    Returns:
        dict: 包含计算结果的字典
    """
    try:
        # 读取CSV文件
        df = pd.read_csv(file_path)
        
        # 检查列是否存在
        if column not in df.columns:
            return {
                "status": "error",
                "message": f"列 '{column}' 不存在于文件中"
            }
        
        # 如果有筛选条件，先进行筛选
        if filter_column and filter_value:
            if filter_column not in df.columns:
                return {
                    "status": "error",
                    "message": f"筛选列 '{filter_column}' 不存在于文件中"
                }
            df = df[df[filter_column] == filter_value]
        
        # 检查数据类型是否适合数值计算
        if operation in ['sum', 'avg', 'min', 'max']:
            try:
                numeric_data = pd.to_numeric(df[column], errors='coerce')
                if numeric_data.isna().all():
                    return {
                        "status": "error",
                        "message": f"列 '{column}' 不包含有效的数值数据"
                    }
            except:
                return {
                    "status": "error",
                    "message": f"列 '{column}' 无法进行数值计算"
                }
        
        # 执行计算操作
        if operation == "sum":
            result = float(pd.to_numeric(df[column], errors='coerce').sum())
        elif operation == "avg":
            result = float(pd.to_numeric(df[column], errors='coerce').mean())
        elif operation == "count":
            result = int(len(df[column]))
        elif operation == "min":
            result = float(pd.to_numeric(df[column], errors='coerce').min())
        elif operation == "max":
            result = float(pd.to_numeric(df[column], errors='coerce').max())
        else:
            return {
                "status": "error",
                "message": f"不支持的操作: {operation}"
            }
        
        return {
            "status": "success",
            "operation": operation,
            "column": column,
            "result": result,
            "filtered_rows": int(len(df)) if filter_column else None
        }
        
    except FileNotFoundError:
        return {
            "status": "error",
            "message": f"文件未找到: {file_path}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"计算数据时发生错误: {str(e)}"
        }

# 工具信息
tool_info = {
    "name": "calculate_csv_data",
    "description": "对CSV数据进行计算操作（求和、平均值、计数等）",
    "function": calculate_csv_data,
    "parameters": {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "CSV文件路径"
            },
            "column": {
                "type": "string",
                "description": "要计算的列名"
            },
            "operation": {
                "type": "string",
                "description": "计算操作（sum, avg, count, min, max）",
                "enum": ["sum", "avg", "count", "min", "max"]
            },
            "filter_column": {
                "type": "string",
                "description": "筛选列名（可选）"
            },
            "filter_value": {
                "type": "string",
                "description": "筛选值（可选）"
            }
        },
        "required": ["file_path", "column", "operation"]
    }
}