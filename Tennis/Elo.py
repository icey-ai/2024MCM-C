import csv

elo = float
prob = int  # 概率数据均为以万分之1为单位的整数


def get_elo(elo_type: str) -> dict[str, elo]:
    first_server = set()
    second_server = set()
    grass_elo = {}
    clay_elo = {}
    hard_elo = {}
    all_elo = {}

    with open("Wimbledon_featured_matches.csv") as csv_file:
        reader = csv.reader(csv_file)
        next(reader)  # skip the header row
        for row in reader:
            if len(row) > 2:
                first_server.add(row[1])
                second_server.add(row[2])

    with open("elo.txt") as elo_file:
        reader = elo_file.readlines()
        for row in reader[1:]:
            cached_row = row.strip().split("  ")
            if cached_row != []:
                player = cached_row[1]
                all_elo[player] = float(cached_row[3])
                hard_elo[player] = float(cached_row[7])
                clay_elo[player] = float(cached_row[8])
                grass_elo[player] = float(cached_row[9])

    for player in first_server:
        if not (player in all_elo):
            all_elo[player] = 1500
            hard_elo[player] = 1500
            clay_elo[player] = 1500
            grass_elo[player] = 1500
            print(player)

    # print(grass_elo)
    match elo_type:
        case "gELO":
            return grass_elo
        case "cELO":
            return clay_elo
        case "hELO":
            return hard_elo


# 输入两个球员的Elo评分，返回双方球员的胜率
def win_probability(R1: elo, R2: elo) -> tuple[prob, prob]:
    # 计算10的指数
    exponent = (R2 - R1) / 400
    # 计算分母
    denominator = 1 + 10**exponent
    # 计算并返回胜率
    return (int(10000 / denominator), int((1 - (1 / denominator)) * 10000))
