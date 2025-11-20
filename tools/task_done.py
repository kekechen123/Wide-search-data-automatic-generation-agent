def task_done(message):
    """
    标记任务完成，结束agent工作流程
    
    Args:
        message: 任务完成信息
        
    Returns:
        dict: 包含完成状态的字典
    """
    return {
        "status": "completed",
        "message": message,
        "task_finished": True
    }

# 工具信息
tool_info = {
    "name": "task_done",
    "description": "标记任务完成，结束agent工作流程",
    "function": task_done,
    "parameters": {
        "type": "object",
        "properties": {
            "message": {
                "type": "string",
                "description": "任务完成信息"
            }
        },
        "required": ["message"]
    }
}