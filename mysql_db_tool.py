import re
from typing import Optional, List, Dict, Any

try:
    import pymysql
    from pymysql import Error
    import pymysql.cursors
except ImportError:
    raise ImportError("pymysql is required. Install with: pip install pymysql")


def query_mysql_pymysql(
        sql: str,
        host: str,
        dbname: str,
        user: str,
        password: str,
        port: int,
        sslmode: str = 'prefer',
        connect_timeout: int = 10,
        parameters: Optional[tuple] = None,
        **kwargs
) -> Dict[str, Any]:
    """
    执行 MySQL 数据库查询（支持 Markdown 包裹的 SQL 语句）
    """
    # --- 1. 预处理 SQL (已修复) ---
    try:
        cleaned_sql = sql.strip()

        # 修复后的正则：
        # ^\s* -> 允许开头有空白
        # ```[a-zA-Z0-9]* -> 匹配 ``` 加上可选的语言标识 (如 sql, mysql, text)
        # \s+            -> 匹配标识后的换行
        # (.*?)          -> 捕获 SQL 内容
        # \s*```\s*$     -> 匹配结尾的 ```
        pattern = r"^\s*```[a-zA-Z0-9]*\s+(.*?)\s*```\s*$"

        match = re.fullmatch(pattern, cleaned_sql, flags=re.IGNORECASE | re.DOTALL)
        if match:
            cleaned_sql = match.group(1).strip()

        # 【重要】绝对不要使用 ' '.join(split())，它会破坏字符串常量和注释
        sql = cleaned_sql

    except Exception as e:
        return {
            "success": False,
            "data": None,
            "row_count": 0,
            "error": f"SQL预处理错误: {str(e)}"
        }

    conn = None
    try:
        # 处理 SSL 配置
        # pymysql 的 ssl 参数通常需要一个字典（如 {'ca': '...'}）或者 Context
        # 这里做一个简单的兼容处理
        ssl_config = None
        if sslmode.lower() != 'disable':
            # 如果传入了具体的 ssl 配置在 kwargs 里，就用 kwargs 的，否则给个默认空字典让驱动尝试连接
            # 注意：如果服务器强制 SSL 且没有提供证书，这里可能需要根据实际情况调整
            ssl_config = kwargs.pop('ssl', {}) or {'check_hostname': False}

        # 建立数据库连接
        conn = pymysql.connect(
            host=host,
            port=port,
            database=dbname,
            user=user,
            password=password,
            connect_timeout=connect_timeout,
            ssl=ssl_config,
            cursorclass=pymysql.cursors.DictCursor,  # 直接在这里指定 Cursor 类型
            **kwargs
        )

        # 不需要再手动 with conn.cursor(...) as cursor，因为上面指定了 cursorclass
        # 但为了保持逻辑兼容，继续使用 cursor() 方法也可以
        with conn.cursor() as cursor:
            # 执行用户SQL
            cursor.execute(sql, parameters)

            # 处理结果
            if cursor.description:  # SELECT 等查询语句
                data = cursor.fetchall()
                row_count = len(data)
            else:  # INSERT/UPDATE/DELETE 等操作
                conn.commit()
                data = None
                row_count = cursor.rowcount

            return {
                "success": True,
                "data": data,
                "row_count": row_count,
                "error": None
            }

    except Error as e:
        return {
            "success": False,
            "data": None,
            "row_count": 0,
            "error": f"数据库错误: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "row_count": 0,
            "error": f"未知错误: {str(e)}"
        }
    finally:
        # PyMySQL 的连接检查通常比较简单，直接 close 即可，close 内部会处理状态
        if conn:
            try:
                conn.close()
            except:
                pass