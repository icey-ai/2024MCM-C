import Elo
import csv
import numpy as np


prob = int  # 概率数据均为以万分之1为单位的整数


class Player(object):
    def __init__(self, name: str) -> None:
        self.name = name
        self.elo_wining_prob = 0
        self.actual_wining_prob = 0
        self.score = 0
        self.score_adder = 0


def solve_markov_chain(uncached_prob: float, score: tuple) -> tuple[prob, prob]:
    # 定义状态集
    S = [(i, j) for i in range(4) for j in range(4)] + ["W", "L", "NW", "NL", "T"]

    # 定义转移概率矩阵
    P = np.zeros((21, 21))  # 初始化为零矩阵
    p = uncached_prob  # A得分的概率
    q = 1 - p  # B得分的概率
    for i in range(4):
        for j in range(4):
            if i < 3 and j < 3:  # 比赛进行中
                P[S.index((i, j)), S.index((i + 1, j))] = p  # A得分
                P[S.index((i, j)), S.index((i, j + 1))] = q  # B得分
            elif i == 3 and j < 3:  # A有机会赢
                P[S.index((i, j)), S.index("W")] = p  # A赢
                P[S.index((i, j)), S.index((i, j + 1))] = q  # B得分
            elif i < 3 and j == 3:  # B有机会赢
                P[S.index((i, j)), S.index("L")] = q  # B赢
                P[S.index((i, j)), S.index((i + 1, j))] = p  # A得分
            elif i == 3 and j == 3:  # 平局
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
    ID = np.eye(Q.shape[0])  # 单位矩阵
    N = np.linalg.inv(ID - Q)  # (Q-I)^(-1)
    B = N @ R  # 落入吸收态的概率矩阵

    # 计算球员A和B的获胜概率
    if score in S:  # 如果是有效的状态
        p_A_win = B[S.index(score), A.index("W")]  # A的胜率
        p_B_win = B[S.index(score), A.index("L")]  # B的胜率
        return (int(p_A_win * 10000), int(p_B_win * 10000))
    else:
        print(score)
        raise IndexError


# 输出int形式的分数
def score_to_int(p1: Player, p2: Player, p1_score: str, p2_score: str) -> None:
    match p1_score:
        case "0":
            p1.score = 0
            p1.score_adder = 0
        case "15":
            p1.score = 1
            p1.score_adder = 0
        case "30":
            p1.score = 2
            p1.score_adder = 0
        case "40":
            p1.score = 3 + p1.score_adder
        case "AD":
            p1.score_adder += 1
            p1.score = 3 + p1.score_adder

    match p2_score:
        case "0":
            p2.score = 0
            p2.score_adder = 0
        case "15":
            p2.score = 1
            p2.score_adder = 0
        case "30":
            p2.score = 2
            p2.score_adder = 0
        case "40":
            p2.score = 3 + p2.score_adder
        case "AD":
            p2.score_adder += 1
            p2.score = 3 + p2.score_adder

    if p1.score_adder != p2.score_adder:
        p1.score_adder = max(p1.score_adder, p2.score_adder)
        p2.score_adder = max(p1.score_adder, p2.score_adder)


def time_to_seconds(time_str: str) -> int:
    hours, minutes, seconds = map(int, time_str.strip().split(":"))
    total_seconds = hours * 3600 + minutes * 60 + seconds
    return total_seconds


def main() -> int:
    ELO = Elo.get_elo("gELO")
    with open("Wimbledon_featured_matches.csv") as csv_file:
        reader = csv.reader(csv_file)
        next(reader, None)  # skip the header row

        # initalize
        row = next(reader, None)
        match_id = row[0]
        p1_name = row[1]
        p2_name = row[2]
        p1 = Player(p1_name)
        p2 = Player(p2_name)
        p1.elo_wining_prob, p2.elo_wining_prob = Elo.win_probability(
            ELO[p1_name], ELO[p2_name]
        )
        new_match = True
        seconds = time_to_seconds(row[3])
        prev_seconds = seconds

        while row is not None:
            if match_id == row[0]:  # we are in the same match
                while True:

                    if (
                        (p1.score != 0 or p2.score != 0)
                        and (row[11] == "0" and row[12] == "0")
                        and not new_match
                    ):
                        new_match = True
                        prev_seconds = seconds
                        seconds = time_to_seconds(row[3])
                        # print("-------Match Ends-------")
                        break  # last set ends, new set begins

                    if new_match:
                        server = row[int(row[13])]
                        p1_elo_prob = p1.elo_wining_prob * (
                            1 + 0.10 * int(server == p1.name)
                        )
                        p2_elo_prob = p2.elo_wining_prob * (
                            1 + 0.10 * int(server == p2.name)
                        )
                        # print(p1_elo_prob / 10000, f" {p1.name}")
                        # print(p2_elo_prob / 10000, f" {p2.name}")
                        new_match = False

                    score_to_int(p1, p2, row[11], row[12])
                    seconds = time_to_seconds(row[3])

                    if p1.score != 0 or p2.score != 0:
                        factor = (seconds - prev_seconds + 0.01) / 600
                        uncached_prob = p1.score * factor / (
                            p1.score + p2.score
                        ) + p1_elo_prob / 10000 * (1 - factor)
                        if p1.score > 3 or p2.score > 3:
                            if p1.score - p2.score < 0:
                                cached_score = (2, 3)
                            elif p1.score - p2.score > 0:
                                cached_score = (3, 2)
                            elif p1.score - p2.score == 0:
                                cached_score = (3, 3)
                        else:
                            cached_score = (p1.score, p2.score)
                        win_prob = solve_markov_chain(uncached_prob, cached_score)
                        p1.actual_wining_prob = win_prob[0]
                        p2.actual_wining_prob = win_prob[1]
                        # if (
                        #     p1.actual_wining_prob
                        #     > 1.1 * p1.elo_wining_prob
                        # ):
                        #     print("p1 goodgood!")
                        # elif (
                        #     p2.actual_wining_prob
                        #     > 1.1 * p2.elo_wining_prob
                        # ):
                        #     print("p2 goodgood!")
                        print(
                            f"(({(p1.actual_wining_prob/p1_elo_prob)*100 - 100}, {time_to_seconds(row[3])}), ",
                            f"({(p2.actual_wining_prob/p2_elo_prob)*100 - 100}, {time_to_seconds(row[3])})), ",
                        )
                        # print(
                        #     # f"({(p1.actual_wining_prob/p1_elo_prob)*100 - 100}, {time_to_seconds(row[3])}), ",
                        #     f"{p2.actual_wining_prob}, ",
                        # )
                    row = next(reader, None)  # next line
                    if row is None:
                        break
            else:
                if row is None:
                    break
                match_id = row[0]
                p1_name = row[1]
                p2_name = row[2]
                print(p2_name)
                p1 = Player(p1_name)
                p2 = Player(p2_name)
                p1.elo_wining_prob, p2.elo_wining_prob = Elo.win_probability(
                    ELO[p1_name], ELO[p2_name]
                )
                print("-------Set Ends-------")
    return 0


main()
