import pandas as pd

def filter_csv_data(file_path, conditions=None, column=None, operator=None, value=None):
    """
    根据条件筛选CSV数据（支持单条件或多条件）
    
    Args:
        file_path: CSV文件路径
        conditions: 多条件列表，每个条件为字典{"column":列名, "operator":操作符, "value":值}
        column: 单个筛选的列名（向后兼容）
        operator: 单个筛选的操作符（向后兼容）
        value: 单个筛选的值（向后兼容）
        
    Returns:
        dict: 包含筛选结果的字典
    """
    try:
        # 读取CSV文件
        df = pd.read_csv(file_path)
        
        # 构建条件列表（支持向后兼容）
        if conditions:
            # 多条件模式
            if not isinstance(conditions, list):
                return {
                    "status": "error",
                    "message": "conditions参数必须是列表格式"
                }
            
            # 检查所有列是否存在
            for cond in conditions:
                if not isinstance(cond, dict) or "column" not in cond:
                    return {
                        "status": "error",
                        "message": "每个条件必须是包含'column'、'operator'和'value'的字典"
                    }
                if cond["column"] not in df.columns:
                    return {
                        "status": "error",
                        "message": f"列 '{cond['column']}' 不存在于文件中"
                    }
        elif column is not None:
            # 单条件模式（向后兼容）
            if column not in df.columns:
                return {
                    "status": "error",
                    "message": f"列 '{column}' 不存在于文件中"
                }
            conditions = [{"column": column, "operator": operator, "value": value}]
        else:
            return {
                "status": "error",
                "message": "必须提供conditions参数或column/operator/value参数组合"
            }
        
        # 应用所有条件进行筛选
        filtered_df = df.copy()
        
        for cond in conditions:
            col = cond["column"]
            op = cond["operator"]
            val = cond["value"]
            
            if op == "=":
                filtered_df = filtered_df[filtered_df[col] == val]
            elif op == "!=":
                filtered_df = filtered_df[filtered_df[col] != val]
            elif op == ">":
                try:
                    filtered_df = filtered_df[filtered_df[col] > float(val)]
                except ValueError:
                    return {
                        "status": "error",
                        "message": f"无法将值 '{val}' 转换为浮点数进行比较"
                    }
            elif op == "<":
                try:
                    filtered_df = filtered_df[filtered_df[col] < float(val)]
                except ValueError:
                    return {
                        "status": "error",
                        "message": f"无法将值 '{val}' 转换为浮点数进行比较"
                    }
            elif op == ">=":
                try:
                    filtered_df = filtered_df[filtered_df[col] >= float(val)]
                except ValueError:
                    return {
                        "status": "error",
                        "message": f"无法将值 '{val}' 转换为浮点数进行比较"
                    }
            elif op == "<=":
                try:
                    filtered_df = filtered_df[filtered_df[col] <= float(val)]
                except ValueError:
                    return {
                        "status": "error",
                        "message": f"无法将值 '{val}' 转换为浮点数进行比较"
                    }
            elif op == "contains":
                filtered_df = filtered_df[filtered_df[col].astype(str).str.contains(val, case=False, na=False)]
            else:
                return {
                    "status": "error",
                    "message": f"不支持的操作符: {op}"
                }
        
        # 返回筛选结果
        result = {
            "status": "success",
            "original_rows": len(df),
            "filtered_rows": len(filtered_df),
            "filtered_data": filtered_df.to_dict('records')
        }
        
        return result
        
    except FileNotFoundError:
        return {
            "status": "error",
            "message": f"文件未找到: {file_path}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"筛选数据时发生错误: {str(e)}"
        }

# 工具信息
tool_info = {
    "name": "filter_csv_data",
    "description": "根据条件筛选CSV数据，支持单条件或多条件筛选",
    "function": filter_csv_data,
    "parameters": {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "CSV文件路径",
                "required": True
            },
            "conditions": {
                "type": "array",
                "description": "多条件列表，每个条件为字典格式",
                "items": {
                    "type": "object",
                    "properties": {
                        "column": {
                            "type": "string",
                            "description": "要筛选的列名"
                        },
                        "operator": {
                            "type": "string",
                            "description": "操作符（=, !=, >, <, >=, <=, contains）",
                            "enum": ["=", "!=", ">", "<", ">=", "<=", "contains"]
                        },
                        "value": {
                            "type": "string",
                            "description": "筛选值"
                        }
                    },
                    "required": ["column", "operator", "value"]
                }
            },
            "column": {
                "type": "string",
                "description": "单个筛选的列名（向后兼容）"
            },
            "operator": {
                "type": "string",
                "description": "单个筛选的操作符（向后兼容）",
                "enum": ["=", "!=", ">", "<", ">=", "<=", "contains"]
            },
            "value": {
                "type": "string",
                "description": "单个筛选的值（向后兼容）"
            }
        },
        "required": ["file_path"],
        "anyOf": [
            {"required": ["conditions"]},
            {"required": ["column", "operator", "value"]}
        ]
    }
}