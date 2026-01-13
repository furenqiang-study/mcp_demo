import re

try:
    import psycopg2
    from psycopg2 import OperationalError
except ImportError:
    raise ImportError("psycopg2 is required. Install with: pip install psycopg2-binary")

from typing import Optional, List, Dict, Any


def query_pg(
        sql: str,
        host: str,
        dbname: str,
        user: str,
        password: str,
        port: int,
        options: str,
        sslmode: str = 'prefer',
        connect_timeout: int = 10,
        parameters: Optional[tuple] = None,
        **kwargs
) -> Dict[str, Any]:
    """
    执行 PostgreSQL 数据库查询（支持 ```sql 包裹的 SQL 语句）

    参数:
        sql (str): 要执行的SQL语句（支持参数化查询，自动处理 ```sql 代码块）
        host (str): 数据库主机地址
        dbname (str): 数据库名称
        user (str): 数据库用户名
        password (str): 数据库密码
        port (int): 数据库端口
        sslmode (str): SSL模式，默认prefer
        connect_timeout (int): 连接超时时间（秒），默认10
        parameters (tuple): SQL参数化的参数值
        **kwargs: 其他数据库连接参数

    返回:
        {
            "success": 是否成功 (bool),
            "data": 查询结果 (List[Dict]/None),
            "row_count": 影响行数 (int),
            "error": 错误信息 (str/None)
        }
    """
    # 预处理 SQL 语句
    try:
        cleaned_sql = sql.strip()
        code_block = re.compile(r'^```sql\s*(.*?)\s*```$', re.IGNORECASE | re.DOTALL)
        if match := code_block.fullmatch(cleaned_sql):
            cleaned_sql = match.group(1).strip()
        cleaned_sql = ' '.join(cleaned_sql.split())
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
        # 建立数据库连接
        conn = psycopg2.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password,
            sslmode=sslmode,
            connect_timeout=connect_timeout,
            options=options,
            **kwargs
        )

        with conn.cursor() as cursor:
            # 执行用户SQL
            cursor.execute(sql, parameters)

            # 处理结果
            if cursor.description:
                col_names = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                data = [dict(zip(col_names, row)) for row in rows]
                row_count = len(data)
            else:
                conn.commit()
                data = None
                row_count = cursor.rowcount

            return {
                "success": True,
                "data": data,
                "row_count": row_count,
                "error": None
            }

    except OperationalError as e:
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
        if conn is not None:
            conn.close()