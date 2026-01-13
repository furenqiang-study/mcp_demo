import pandas as pd
from sqlalchemy import create_engine

# 水库水位库容互查
def lagrange_3point(H, H_list, V_list):
    """
    三点拉格朗日插值计算库容
    :param H: 目标水位
    :param H_list: 已知水位列表 [H0, H1, H2]
    :param V_list: 已知库容列表 [V0, V1, V2]
    :return: 目标库容V
    """
    print(H, H_list, V_list)
    H0, H1, H2 = H_list
    V0, V1, V2 = V_list
    term0 = V0 * (H - H1) * (H - H2) / ((H0 - H1) * (H0 - H2))
    term1 = V1 * (H - H0) * (H - H2) / ((H1 - H0) * (H1 - H2))
    term2 = V2 * (H - H0) * (H - H1) / ((H2 - H0) * (H2 - H1))
    return term0 + term1 + term2

    # 示例：已知水位(100m, 105m, 110m)对应库容(500, 1500, 3200万m³)，求107m库容
    # V = lagrange_3point(107, [100, 105, 110], [500, 1500, 3200])
    # print(f"水位107m时库容：{V:.1f}万m³")  # 输出：2325.0万m³


def rz_to_w(parm):
    result = {
        'success': False,
        'data': None,
    }
    try:
        if not isinstance(parm, float):
            result['error'] = "输入参数parm必须是浮点型数值"
        else:
            h = parm
            # 创建数据库连接（格式：mysql+driver://user:password@host/database）
            # engine = create_engine("mysql+pymysql://root:0NdcL03EpMeCX9qe@t1.zjsophon.com:63305/tchdc")
            engine = create_engine("mysql+pymysql://root:0NdcL03EpMeCX9qe@192.168.110.137:63305/tchdc")
            # 编写 SQL 查询
            query = "SELECT RZ,W FROM b_st_zvarl_b  WHERE STCD=%(STCD)s ORDER BY ABS(RZ - %(H)s)  LIMIT 3"
            # 使用 pandas 读取 SQL 查询结果
            df = pd.read_sql(query, engine, params={"STCD": 70302500, "H": h})  # 横山水库的站点编码
            # 显示结果
            h_list = df['RZ'].tolist()
            v_list = df['W'].tolist()
            v = lagrange_3point(h, h_list, v_list)
            result['success'] = "true"
            result['data'] = round(v, 2)  # 保留两位小鼠
    except Exception as e:
        result['error'] = f"服务器错误: {str(e)}"
    return result


def w_to_rz(parm):
    result = {
        'success': False,
        'data': None,
    }
    try:
        if not isinstance(parm, float):
            result['error'] = "输入参数parm必须是浮点型数值"
        else:
            v = parm
            # 创建数据库连接（格式：mysql+driver://user:password@host/database）
            # engine = create_engine("mysql+pymysql://root:0NdcL03EpMeCX9qe@t1.zjsophon.com:63305/tchdc")
            engine = create_engine("mysql+pymysql://root:0NdcL03EpMeCX9qe@192.168.110.137:63305/tchdc")
            # 编写 SQL 查询
            query = "SELECT RZ,W FROM b_st_zvarl_b  WHERE STCD=%(STCD)s ORDER BY ABS(W - %(V)s)  LIMIT 3"
            # 使用 pandas 读取 SQL 查询结果
            df = pd.read_sql(query, engine, params={"STCD": 70302500, "V": v})  # 横山水库的站点编码
            # 显示结果
            h_list = df['RZ'].tolist()
            v_list = df['W'].tolist()
            h = lagrange_3point(v, v_list, h_list)
            result['success'] = "true"
            result['data'] = round(h, 2)  # 保留两位小鼠
    except Exception as e:
        result['error'] = f"服务器错误: {str(e)}"
    return result


def water_caculate(mode, parm):
    result = {
        'success': False,
        'data': None,
    }
    try:
        if not isinstance(parm, float):
            result['error'] = "输入参数parm必须是浮点型数值"
        else:
            match mode:
                case 0:
                    res = rz_to_w(parm)  # 根据水位查询库容
                case 1:
                    res = w_to_rz(parm)  # 根据库容查询水位
            result['success'] = "true"
            result['data'] = res
    except Exception as e:
        result['error'] = f"服务器错误: {str(e)}"
    return result
