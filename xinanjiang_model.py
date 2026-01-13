import numpy as np
import pandas as pd

import json


def count(params, p, em):
    # 待优化参数
    K = params['K']
    WUM = params['WUM']
    WLM = params['WLM']
    SM = params['SM']
    KG = params['KG']
    KI = params['KI']
    CS = params['CS']
    CI = params['CI']
    CG = params['CG']
    x = params['x']

    # 常量参数
    WU = 3
    WL = 15
    WD = 20
    WDM = 20
    C = 0.15
    WM = 120
    IM = 0.01
    EX = 1.5  # 自由水蓄水容量曲线指数
    B = 0.2
    WMM = (1 + B) * WM / (1 - IM)

    W = WU + WL + WD  # 就是今天的初始土壤含水量（昨天结束的土壤含水量）
    lst1 = []  # 存储R
    lst2 = []  # EU
    lst3 = []  # EL
    lst4 = []  # ED
    lst5 = []  # E
    lst6 = []  # WU
    lst7 = []  # WL
    lst8 = []  # WD
    lst9 = []  # W

    for i in range(len(p)):
        P = p[i]
        EM = em[i]

        def safe_power(base, exp):
            if base < 0 and exp != int(exp):
                return np.nan  # 避免负数开方产生复杂数
            return np.power(base, exp)

        a = WMM * (1 - safe_power(1 - W / WM, 1 / (B + 1)))
        if P - K * EM <= 0:
            R = 0
        elif P - K * EM + a < WMM:
            R = P - K * EM + W - WM + WM * (1 - (P - K * EM + a) / WMM) ** (1 + B)
        else:
            R = P - K * EM - (WM - W)
        # 计算R的W都是前一天结束时的W
        if P + WU >= K * EM:
            EU = K * EM
            EL = 0
            ED = 0
            if P <= K * EM:
                WU = WU - (K * EM - P)
            elif P + WU - K * EM - R < WUM:
                WU = P + WU - K * EM - R
            elif WL + P + WU - K * EM - R - WUM < WLM:
                WL = WL + P + WU - K * EM - R - WUM
                WU = WUM
            elif WL + WD + P + WU - K * EM - R - WUM - WLM < WDM:
                # （所以要保证本行和下一行计算的公式一致，这样就不会错）
                WD = WL + WD + P + WU - K * EM - R - WUM - WLM
                WL = WLM
                WU = WUM
            else:
                WU = WUM
                WL = WLM
                WD = WDM
        else:
            EU = P + WU
            WU = 0
            if WL / WLM >= C:
                EL = (K * EM - EU) * WL / WLM
                ED = 0
                WL -= EL
            else:
                if WL >= C * (K * EM - EU):
                    EL = C * (K * EM - EU)
                    ED = 0
                    WL -= EL
                else:
                    EL = WL
                    ED = C * (K * EM - EU) - WL
                    WL = 0
                    if WD > ED:
                        WD -= ED
                    else:
                        WD = 0
        E = EU + EL + ED  # 蒸散发量

        W = WU + WL + WD  # 今天结束的土壤含水量（明天的初始土壤含水量）

        lst1.append(R)
        lst2.append(EU)
        lst3.append(EL)
        lst4.append(ED)
        lst5.append(E)
        lst6.append(WU)
        lst7.append(WL)
        lst8.append(WD)
        lst9.append(W)

    # -------------------分水源（三水源） ------------------------

    MS = SM * (1 + EX)

    # 以下两参数初次运行可以使用，之后将其放入相应列表
    S0 = 0  # 本时段初的自由水蓄量
    FR0 = 0.05  # 上时段产流面积比例

    lst_FR = [FR0]  # 存储FR
    lst_Si = []  # Si=S0*FRO/FR
    lst_AU = []  # AU
    lst_RS = []  # RS
    lst_S = []  # S
    lst_RI = []  # RI
    lst_RG = []  # RG
    lst_S1 = [S0]  # 存放下一阶段S0，即S1
    for i in range(len(p)):
        P = p[i]
        EM = em[i]
        R = lst1[i]  # 产流：由上一步得到
        S0 = lst_S1[i]
        FR0 = lst_FR[i]
        if P - K * EM <= 0:
            FR = FR0
        else:
            FR = (R - IM * (P - K * EM)) / (P - K * EM)

        Si = S0 * FR0 / FR
        MS = SM * (1 + EX)
        AU = MS * (1 - safe_power(1 - (S0 * FR0 / FR) / SM, 1 / (EX + 1)))
        if AU + P - K * EM <= MS:
            RS = FR * (P - K * EM + S0 * FR0 / FR - SM + SM * (1 - (P - K * EM + AU) / MS) ** (EX + 1))
        else:
            RS = FR * (P - K * EM + S0 * FR0 / FR - SM)
        if R == 0:
            RS = 0
        S = S0 * FR0 / FR + (R - RS) / FR
        RI = KI * S * FR
        RG = KG * S * FR
        S1 = S * (1 - KI - KG)

        lst_FR.append(FR)
        lst_AU.append(AU)
        lst_RS.append(RS)
        lst_S.append(S)
        lst_RI.append(RI)
        lst_RG.append(RG)
        lst_S1.append(S1)
    lst_S1.pop(0)

    # # ------------------------------汇流阶段-------------------------------------------
    # ----------（单元面积河网总入流：线性水库法+单元面积以下河道汇流：马斯京根法）------------------
    rs = lst_RS
    ri = lst_RI
    rg = lst_RG
    # 以下为初始参数设定：
    U = 150.53 / 3.6  # 单位转换系数=流域面积(km2)/(3.6*时间间隔)（小时）
    # 以下三个参数初次运行可以使用，之后将其放入相应列表
    QRS0 = 0
    QRI0 = 0
    QRG0 = 0
    QT0 = QRS0 + QRI0 + QRG0
    lst_QRS = [QRS0]
    lst_QRI = [QRI0]
    lst_QRG = [QRG0]
    lst_QT = [QT0]

    # 线性水库法
    for i in range(len(rs)):
        RS = rs[i]
        RI = ri[i]
        RG = rg[i]
        QRS0 = lst_QRS[i]
        QRI0 = lst_QRI[i]
        QRG0 = lst_QRG[i]
        QRS = QRS0 * CS + RS * (1 - CS) * U  # 滞后演算法
        QRI = QRI0 * CI + RI * (1 - CI) * U
        QRG = QRG0 * CG + RG * (1 - CG) * U
        QT = QRS + QRI + QRG  # 单元面积河网总入流
        lst_QRS.append(QRS)
        lst_QRI.append(QRI)
        lst_QRG.append(QRG)
        lst_QT.append(QT)
    dt = 1  # 演算时段长度
    K_m = 1  # 槽蓄曲线坡度
    n = len(lst_QT)
    O2 = np.zeros((n, 1))
    c0 = (0.5 * dt - K_m * x) / (0.5 * dt + K_m - K_m * x)
    c1 = (0.5 * dt + K_m * x) / (0.5 * dt + K_m - K_m * x)
    c2 = (-0.5 * dt + K_m - K_m * x) / (0.5 * dt + K_m - K_m * x)

    # 马斯京根法
    for i in range(1, n):
        I1 = lst_QT[i - 1]
        I2 = lst_QT[i]
        Q1 = O2[i - 1]
        O2[i] = c0 * I2 + c1 * I1 + c2 * Q1
    O2 = O2[1:]  # 去掉第1个元素，第1个元素是为了用于流量演算，实际中不存在。
    Qout = np.array(O2)  # 汇流后的流量，转化为数组形式
    np.set_printoptions(suppress=True, precision=4)  # 将演算流量按照四位小数显示，不以科学计数法显示

    return Qout


def XAJ_model(parm):
    """
    横山水库新安江模型，通过给定的降雨数据，计算水库入库径流

    参数:
        P (array): 降雨数据，数组，单位是mm
        TM (int):降雨时长，整型，如果降雨时长与降雨数据的数组长度需一致

    返回:
       Qout(array) : 水库入库流量，单位m³/s
    """
    result = {
        'success': False,
        'data': None,
        'error': None
    }

    # json转换为 Python 对象（dict）
    # print(f"hanshurucan:{parm}")
    # print(f"hanshurucan type:{type(parm)}")
    # python_dict = json.loads(parm)
    try:
        python_dict = json.loads(parm)
        # result['data'] = python_dict
        # result['error'] = type(python_dict)
        p = python_dict.get('P')
        tm = python_dict.get('TM')
        if not isinstance(p, list):
            result['error'] = "输入参数P必须是数组"
        elif not isinstance(tm, int):
            result['error'] = "输入参数TM必须是整数"
        elif len(p) != tm:
            result['error'] = "输入参数P的数组长度必须与参数TM相等"
        else:
            try:
                em = [0] * tm
                # 使用最优参数 global_best_position 生成预测值 Qout
                global_best_position = {'K': 0.8,
                                        'WUM': 10,
                                        'WLM': 87.62629834,
                                        'SM': 10.09551377,
                                        'KG': 0.1,
                                        'KI': 0.1,
                                        'CS': 0.736362691,
                                        'CI': 0.783772077,
                                        'CG': 0.95,
                                        'x': 0.381507631
                                        }
                Qout = count(global_best_position, p, em)  # 传递额外的参数
                # 将预测值添加到数据中
                result['data'] = Qout.tolist()
                result['success'] = 'true'
            except Exception as e:
                result['error'] = f"服务器错误: {str(e)}"
    except json.JSONDecodeError as e:
        result['error'] = "JSON 解码失败:" + e
    return result
