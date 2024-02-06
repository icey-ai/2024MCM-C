# 导入numpy库
import numpy as np

# 定义状态集
S = [(i, j) for i in range(11) for j in range(11)] + ["W", "L", "NW", "NL", "T"]

# 定义转移概率矩阵
P = np.zeros((126, 126))  # 初始化为零矩阵
p = 0.6  # A得分的概率
q = 1 - p  # B得分的概率
for i in range(11):
    for j in range(11):
        if i < 10 and j < 10:  # 比赛进行中
            P[S.index((i, j)), S.index((i + 1, j))] = p  # A得分
            P[S.index((i, j)), S.index((i, j + 1))] = q  # B得分
        elif i == 10 and j < 10:  # A有机会赢
            P[S.index((i, j)), S.index("W")] = p  # A赢
            P[S.index((i, j)), S.index((i, j + 1))] = q  # B得分
        elif i < 10 and j == 10:  # B有机会赢
            P[S.index((i, j)), S.index("L")] = q  # B赢
            P[S.index((i, j)), S.index((i + 1, j))] = p  # A得分
        elif i == 10 and j == 10:  # 平局
            P[S.index((i, j)), S.index("NW")] = p  # A领先
            P[S.index((i, j)), S.index("NL")] = q  # B领先
P[S.index("NW"), S.index("W")] = p  # A赢
P[S.index("NW"), S.index("T")] = q  # 平局
P[S.index("NL"), S.index("L")] = q  # B赢
P[S.index("NL"), S.index("T")] = p  # 平局
P[S.index("T"), S.index("NW")] = p  # A领先
P[S.index("T"), S.index("NL")] = q  # B领先
P[S.index("W"), S.index("W")] = 1  # A赢
P[S.index("L"), S.index("L")] = 1  # B赢

# 定义吸收态
A = ["W", "L"]  # 吸收态集合
is_absorbing = np.array([s in A for s in S])  # 布尔向量，表示各个状态是否是吸收态

# 求解落入吸收态的概率
Q = P[~is_absorbing, :][:, ~is_absorbing]  # 非吸收态到非吸收态的转移概率子矩阵
R = P[~is_absorbing, :][:, is_absorbing]  # 非吸收态到吸收态的转移概率子矩阵
I = np.eye(Q.shape[0])  # 单位矩阵
N = np.linalg.inv(I - Q)  # (Q-I)^(-1)
B = N @ R  # 落入吸收态的概率矩阵

# 计算球员A和B的获胜概率
# 遍历所有可能的比分
for i in range(11):
    for j in range(11):
        if (i, j) in S:  # 如果是有效的状态
            p_A_win = B[S.index((i, j)), A.index("W")]  # A的胜率
            p_B_win = B[S.index((i, j)), A.index("L")]  # B的胜率
            print(
                f"当比分为({i},{j})时，A的胜率是{p_A_win:.4f}，B的胜率是{p_B_win:.4f}"
            )
