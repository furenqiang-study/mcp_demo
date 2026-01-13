import ast


def convert_str_to_array(input_str: str) -> list:
    """
    将字符串类型的数组转换为Python列表

    参数:
    input_str (str): 表示数组的字符串（如"[1, 2, 3]"或"['a','b','c']"）

    返回:
    list: 转换后的Python列表

    示例:
    >>> convert_str_to_array("[1, 2, 3]")
    [1, 2, 3]
    >>> convert_str_to_array("['apple', 'banana']")
    ['apple', 'banana']
    """
    try:
        # 安全地计算表达式并返回Python对象
        result = ast.literal_eval(input_str)
        if isinstance(result, (list, tuple)):
            return list(result)
        else:
            # 如果不是列表/元组，作为单个元素返回
            return [result]
    except (SyntaxError, ValueError):
        # 处理无效格式：尝试分割逗号分隔的字符串
        if ',' in input_str:
            return [item.strip() for item in input_str.split(',')]
        else:
            # 纯字符串作为单元素列表返回
            return [input_str]