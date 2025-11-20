# 工具模块整合文件

from .csv_reader import read_csv_info, tool_info as reader_info
from .csv_filter import filter_csv_data, tool_info as filter_info
from .csv_calculator import calculate_csv_data, tool_info as calculator_info
from .csv_writer import write_to_csv, tool_info as writer_info
from .task_done import task_done, tool_info as task_info

# 所有工具的映射
tools_map = {
    "read_csv_info": read_csv_info,
    "filter_csv_data": filter_csv_data,
    "calculate_csv_data": calculate_csv_data,
    "write_to_csv": write_to_csv,
    "task_done": task_done
}

# 工具信息列表
tools_info = [
    reader_info,
    filter_info,
    calculator_info,
    writer_info,
    task_info
]

def get_tool_function(tool_name):
    """
    根据工具名称获取对应的函数
    
    Args:
        tool_name: 工具名称
        
    Returns:
        function: 工具函数
    """
    return tools_map.get(tool_name)

def list_all_tools():
    """
    获取所有可用工具的信息
    
    Returns:
        list: 工具信息列表
    """
    return tools_info

__all__ = [
    'read_csv_info',
    'filter_csv_data', 
    'write_to_csv',
    'calculate_csv_data',
    'task_done',
    'get_tool_function',
    'list_all_tools'
]