#-*- coding = utf-8 -*-
#@Time : 2021/5/8 10:08
#@Author : ZXREAPER zhangxu
#@File : get_seat_dist.py
#@Software : PyCharm

# 获取各展厅的座位映射表
"""
一楼观众席（标号：1）座位映射表：


#座位号列号  1  2  3  4  5  6  7  8  9  10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27
#第一排
[     0，    31,32,30,33,29,34,28,35,27,36,26,46,17,47,16,48,15,49,14,50,13,51,12,52,11,53,10]
#第二排
...
...

    映射规则：
            输入：在电影院中的第几排，第几列
            返回：在表格中的行、列下标


最终将模板转成numpy格式保存起来

"""
import math
import numpy as np
import pandas as pd


def generate_seat_distribution(file_path):
    exhibition_hall = file_path
    No_1_seat = pd.read_excel(exhibition_hall, engine='openpyxl', header=None)

    No_1_seat_distribution = []

    for index, rows in No_1_seat.iterrows():
        row_distribution = []
        for k, v in enumerate(rows):
            if math.isnan(v):
                continue
            else:
                row_distribution.append([int(v), index, k])
        row_distribution.sort(key=lambda x: x[0])
        No_1_seat_distribution.append(row_distribution)

    No_1_seat_distribution_map = [[]]
    for haoma in No_1_seat_distribution:
        temp = [[]]
        for t in haoma:
            #             temp.append([t[1],t[2]])
            while len(temp) != t[0]:
                temp.append([])
            temp.append([t[1], t[2]])

        No_1_seat_distribution_map.append(temp)

    m = np.array(No_1_seat_distribution_map)
    save_name = exhibition_hall[0:-4] + 'npy'
    np.save(save_name, m)