#-*- coding = utf-8 -*-
#@Time : 2021/5/8 10:03
#@Author : ZXREAPER zhangxu
#@File : BackendLogic.py
#@Software : PyCharm

import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import functools
import xlwt
import os
import seaborn as sns
from dateutil.parser import parse
from matplotlib.colors import LinearSegmentedColormap

plt.switch_backend('pdf')



class Solve:
    def __init__(self,filepath = None,previous_filepath = None,changci = 1, changciname = "《巴黎圣母院》",heatmaptheme = "rainbow",WorkThread = None):
        """
        初始化。
        :param filepath: 列表。文件名
        :param changci: 总的场次数
        """
        # 将当前线程对象传进来
        self.WorkThread = WorkThread

        # 多文件的路径集合。列表。
        self.files_name = filepath

        # 预留表文件路径集合
        self.previous_files_name = previous_filepath

        # 设置场次数量
        self.movie_cnt = changci

        # 设置每个场次的时间名称
        self.changci_time_name = []

        # 本场的名称
        self.theater_name = changciname[1:-1]

        # 设置热力图显示的主题
        self.heatmap_theme = heatmaptheme

        # 设置对整体热力图非座位的地方进行mask的值
        self.ensemble_mask = 0

        # 设置座位表所在的路径。
        self.cwd_2 = os.path.dirname(__file__)
        '''
            各区域编号：
                一楼观众厅:      1
                二楼单号包厢:    2
                二楼双号包厢:    3
                二楼贵宾席V1:    4
                二楼贵宾席V2:    5
                二楼贵宾席V3:    6
                二楼贵宾席V4:    7
                二楼贵宾席V5:    8
                二楼贵宾席V6:    9
                二楼贵宾席V7:    10
                三楼单号包厢:    11
                三楼双号包厢:    12
                三楼观众厅:      13
            '''
        self.seat_number = {"一楼观众厅": 1, "观众厅一楼": 1,"二楼单号包厢": 2, "二楼双号包厢": 3, "二楼贵宾席V1": 4, "二楼贵宾席V2": 5,
                       "二楼贵宾席V3": 6, "二楼贵宾席V4": 7, "二楼贵宾席V5": 8, "二楼贵宾席V6": 9, "二楼贵宾席V7": 10,
                       "三楼单号包厢": 11, "三楼双号包厢": 12, "三楼观众厅": 13,"观众厅三楼": 13}
        self.ni_seat_number = {1: "一楼观众厅", 2: "二楼单号包厢", 3: "二楼双号包厢", 4: "二楼贵宾席V1", 5: "二楼贵宾席V2",
                          6: "二楼贵宾席V3", 7: "二楼贵宾席V4", 8: "二楼贵宾席V5", 9: "二楼贵宾席V6", 10: "二楼贵宾席V7",
                          11: "三楼单号包厢", 12: "三楼双号包厢", 13: "三楼观众厅"}

        # 用来标记是否已经计算过self.seat_count和self.perchase_speed_of_seat了
        # 若速度已经计算过了那么就不需要再重复计算了
        self.flag = False

        # 若频率已经计算过了那么就不需要再重复计算了
        self.frequence_flag = False

        # 最长购买时间
        self.maxv = 0

        # 用来记录散客表中每个位置被购买的次数
        self.seat_count = [0 for _ in range(999999)]

        # 用来记录预留票中出现的座位的被购买次数
        # 字典：例如：{'8月10日 1930':{对应位置：1}，'8月10日 1400':{对应位置：1}，……}
        self.previous_seat_count = {}

        # 用来记录每个场次的最长购票时间
        self.longest_perchase_time = {}

        # 用来记录在这些场次中每个位置最终的购票票耗时
        self.perchase_speed_of_seat = [0 for _ in range(999999)]

        # 用来记录在这些场次中每个位置最终的购票票频次
        self.perchase_frequence_of_seat = [0 for _ in range(999999)]

        # 用来记录在这些场次中每个座位最终结合购票速度和购票频次的值
        self.perchase_frequence_and_perchase_speed_of_seat = [0 for _ in range(999999)]

        # 将符合条件的每个座位的耗时存储起来
        self.every_seat_cost_time = [[] for _ in range(999999)]

        # 记录每个座位每个场次在散客表中的购票耗时
        # 字典：例如：{'8月10日 1930':{对应位置：耗时}，'8月10日 1400':{对应位置：耗时}，……}
        self.every_seat_every_changci_cost_time = {}

    # 计算预售表中的固定场次固定位置的被购买情况，最后这些位置需要排除在我们的分析范围之内。
    def cal_previous_seat_count(self):
        """
        计算self.previous_seat_count
        :param files: 预售表的文件列表，因为可能包含多个预售表文件
        :return: void。
        """
        for file_name in self.previous_files_name:
            info = pd.read_excel(file_name, engine='openpyxl', sheet_name=None)
            # 标记所有在预售表中出现过的位置，在最终的计算上，不能考虑这些位置
            for k, v in info.items():
                v = v.dropna(axis=0, how='all')
                # if k[-2:] == '晚场':
                #     k = k[:-2] + '1930'
                # else:
                #     k = k[:-2] + '1400'
                self.previous_seat_count[k] = {}
                for index, rows in v.iterrows():
                    region = int(self.seat_number[v['区'][index]])
                    if isinstance(v['排'][index], str):
                        row_num = int("".join(filter(str.isdigit, v['排'][index])))
                    else:
                        row_num = int(v['排'][index])
                    seat_num = int(v['座'][index])
                    self.previous_seat_count[k][int(region * 10000 + row_num * 100 + seat_num)] = 1

    # 读取单张数据表（散客表）并处理.
    def process_data(self, file_name):
        """
        读取单张数据表并处理。
        :param file_name: 处理的单个文件的文件路径。
        :return: 场次的名称 str类型, DataFrame。
        """
        i = -1
        while file_name[i] != '》':
            i -= 1
        changci_name = file_name[i + 1:-5]
        self.changci_time_name.append(changci_name)
        temp_table = pd.read_excel(file_name, usecols=[0, 1, 3, 4, 5, 6, 8, 9, 10], engine='openpyxl')
        temp_table = temp_table.dropna(axis=0, how='all')
        for index, rows in temp_table.iterrows():
            try:
                temp_table['区域名称'][index] = self.seat_number[rows[6]]
            except KeyError:
                print(changci_name,index)
                continue
        temp_table['时间间隔'] = 0
        temp_table['场次名称'] = changci_name
        self.longest_perchase_time[changci_name] = (parse(str(temp_table["场次时间"][0]))-parse(str(temp_table["开票时间"][0]))).total_seconds()

        # 数据类型转换为float64
        temp_table['时间间隔'] = temp_table['时间间隔'].astype('float64')
        for index, rows in temp_table.iterrows():
            a = parse(str(temp_table["创建日期"][index]))
            b = parse(str(temp_table["开票时间"][index]))
            diff = (a - b).total_seconds()
            # diff = (a - b).days   采用天数作为计算速度的单位的话会有许多情况是0，因为很多票是在第一天就被购买了
            if diff < 0:
                # 如果存在创建日期早于开票日期的情况那么购买的折后价格一定是333元或444元，否则就有问题，下面就是判断有没有这样的数据存在
                if temp_table["折后价格"][index] != 333 and temp_table["折后价格"][index] != 444:
                    print(file_name, temp_table["区域名称"][index],temp_table["排"][index],temp_table["座"][index])
            if diff <= 1:
                diff = 2
            temp_table["时间间隔"][index] = diff

        return temp_table

    # 读取各区域的座位映射表
    def read_distribution_map(self) -> dict:
        """
        读取各区域的座位映射表。
        :return: 字典。输入第几个区域、第几排、第几座，返回该位置应该在表格中的行列坐标。
        """
        # 加载各区域的映射表
        def read_distribution(file_path) -> list:  # 迷惑行为：不加返回值注释竟然在经过return后list类型变为了NoneType
            a = np.load(file_path, allow_pickle=True)
            res = a.tolist()
            return res

        seat_distribution_map = {}
        for i in range(1, 14):
            # print(self.cwd_2)
            file_name = self.cwd_2+'\seat_distribution\\NO_' + str(i) + '_seat_distribution.npy'
            temp = read_distribution(file_name)
            seat_distribution_map[i] = temp

        return seat_distribution_map


    def cmp(self,a,b):
        """
        排序方式：
                第一关键字：区域号。递增关系。
                第二关键字：排。递增关系。
                第三关键字：座位号。递增关系。
                第四关键字：数量。退票(-1)在后，买票(1)在前。
                第五关键字：时间间隔。递减关系。

        :param a: first list
        :param b: second list
        :return: 1 or -1
        """
        if a[2] == b[2]:
            if a[3] == b[3]:
                if a[4] == b[4]:
                    if a[1] == b[1]:
                        if a[5] < b[5]:
                            return 1
                        else:
                            return -1
                    else:
                        if a[1] < b[1]:
                            return 1
                        else:
                            return -1
                else:
                    if a[4] > b[4]:
                        return 1
                    else:
                        return -1
            else:
                if a[3] > b[3]:
                    return 1
                else:
                    return -1
        else:
            if a[2] > b[2]:
                return 1
            else:
                return -1

    # 解决数据中有退票的情况
    def process_refund(self,table) -> list:
        """
        解决数据中有退票的情况。
        :param table: 类型是DataFrame。原始处理过的表，含有退票记录。
        :return: 列表。处理过后，不含退票的记录。
        """
        cur_table = table[['场次名称','数量','区域名称', '排', '座', '时间间隔']]
        cur_table = cur_table.values.tolist()
        cur_table.sort(key=functools.cmp_to_key(self.cmp))

        processed_table = []

        last = cur_table[0]
        length = len(cur_table)

        for i in range(1, length):
            if cur_table[i][2] == last[2] and cur_table[i][3] == last[3] and cur_table[i][4] == last[4]:
                if cur_table[i][1] == 1:
                    last.append(cur_table[i][5])
                else:
                    last.pop()
            else:
                processed_table.append(last)
                last = cur_table[i]
        processed_table.append(last)
        return processed_table

    # 计算散客表中每个座位出现的次数
    def cal_seat_count(self, processed_table_list):
        """
        用来计算每个座位出现的次数
        :param processed_table_list: 列表。有多少个文件该列表就有多少个元素，每个元素是处理过退票后的表格。
        :return: void。结果回填入self.seat_count列表中。
        """
        # 所有场次最长的购买时间
        self.maxv = self.longest_perchase_time[max(self.longest_perchase_time)]

        # 统计所有场次中每个位置的出现次数。注意应该删除在预售表中出现的位置
        for processed_table in processed_table_list:
            # 场次名称 例如：“5月12日 1930”
            names = processed_table[0][0]
            self.every_seat_every_changci_cost_time[names] = {}
            for item in processed_table:
                region = int(item[2])
                if isinstance(item[3], str):
                    row_num = int("".join(filter(str.isdigit,  item[3])))
                else:
                    row_num = int(item[3])
                seat_num = int(item[4])

                # 该位置的时间间隔
                time_len = 0
                if len(item) == 6:
                    time_len = item[5]
                else:
                    time_len = self.maxv

                # 如果在预售票中发现了当前的位置，那么应该舍弃这个位置
                if names in self.previous_seat_count:
                    if region*10000+row_num*100+seat_num in self.previous_seat_count[names]:
                        print("{}区域，{}排，{}座,这个位置在预售票和散客表中都被购买了！".format(region,row_num,seat_num))
                    else:
                        if len(item) == 6:
                            self.seat_count[int(region * 10000 + row_num * 100 + seat_num)] += 1
                            self.every_seat_cost_time[int(region*10000+row_num*100+seat_num)].append(item[5])
                            self.every_seat_every_changci_cost_time[names][int(region * 10000 + row_num * 100 + seat_num)] = time_len
                else:
                    if len(item) == 6:
                        self.every_seat_every_changci_cost_time[names][int(region * 10000 + row_num * 100 + seat_num)] = time_len
                        self.seat_count[int(region * 10000 + row_num * 100 + seat_num)] += 1
                        self.every_seat_cost_time[int(region * 10000 + row_num * 100 + seat_num)].append(item[5])

    # 《巴黎圣母院》
    def balishengmu_transformation_equation1(self, x):
        """
        对《巴黎圣母院》的数据分布的数据进行转换
        :param x: 类型是float
        :return: float
        """
        maxvv = self.maxv
        unit = 3600
        if x <= unit:
            x = 6 / unit * x
        elif unit < x and x <= 12 * unit:
            x = 6 / 11 / 3600 * x + 6 - 6 / 11
        else:
            x = (2 / (maxvv - 12 * 3600)) * x + (12 - (24 * 3600) / (maxvv - 12 * 3600))

        return x

    # 《德国音乐剧明星音乐会》
    def germanytheater_transformation_equation(self, x):
        """
        对《德国音乐剧明星音乐会》的数据分布的数据进行转换
        :param x: 类型是float
        :return: float
        """
        maxvv = self.maxv
        unit = 3600
        if x <= unit:
            x = 6 / unit * x
        elif unit < x and x <= 12 * unit:
            x = 6 / 11 / 3600 * x + 6 - 6 / 11
        else:
            x = (2 / (maxvv - 12 * 3600)) * x + (12 - (24 * 3600) / (maxvv - 12 * 3600))

        return x

    # 《泰坦尼克号》
    def titanic_transformation_equation(self, x):
        """
        对《泰坦尼克号》的数据分布的数据进行转换
        :param x: 类型是float
        :return: float
        """
        maxvv = self.maxv
        unit = 3600
        if x <= unit:
            x = 6 / unit * x
        elif unit < x and x <= 12 * unit:
            x = 3 / 11 / 3600 * x + 6 - 3 / 11
        else:
            x = (5 / (maxvv - 12 * 3600)) * x + (14 - (5 * maxvv)/(maxvv - 12 * 3600))

        return x

    # 《悲惨世界》
    def world_transformation_equation(self, x):
        """
        对《悲惨世界》的数据分布的数据进行转换
        :param x: float
        :return: float
        """
        maxvv = self.maxv
        unit = 3600
        if x <= unit:
            x = 3 / 3600 * x
        elif unit < x and x <= 24 * unit:
            x = 4 / 23 / 3600 * x + 3 - 4 / 23
        elif 24 * unit < x and x <= 48 * unit:
            x = 2 / 24 / 3600 * x + 5
        elif 48 * unit < x and x <= 7 * 24 * 3600:
            x = 3 / 120 / 3600 * x + 9 - 48 / 40
        else:
            x = 2 * x / (maxvv - 7 * 24 * 3600) + 14 - (2 * maxvv / (maxvv - 7 * 24 * 3600))

        return x

    # 《叶普盖尼奥涅金》
    def gold_transformation_equation(self, x):
        """
        对《悲惨世界》的数据分布的数据进行转换
        :param x: float
        :return: float
        """
        maxvv = self.maxv
        unit = 3600
        if x <= unit:
            x = 6 / 3600 * x
        elif unit < x and x <= 8 * 3600:
            x = 6 / 7 / 3600 * x + 6 - 6 / 7
        else:
            x = 2 / (maxvv - 8 * 3600) * x + 14 - 2 * maxvv / (maxvv - 8 * 3600)

        return x

    # 《马修伯恩天鹅湖》
    def goose_transformation_equation(self, x):
        """
        对《马修伯恩天鹅湖》的数据分布的数据进行转换
        :param x: float
        :return: float
        """
        maxvv = self.maxv
        unit = 3600
        if x <= unit:
            x = 6 / 3600 * x
        else:
            x = 8 / (maxvv - 3600) * x + 6 - 8 * 3600 / (maxvv - 3600)

        return x

    # 《歌舞线上》
    def song_transformation_equation(self, x):
        """
        对《歌舞线上》的数据分布的数据进行转换
        :param x: float
        :return: float
        """
        maxvv = self.maxv
        unit = 3600
        if x <= unit:
            x = 6 / 3600 * x
        elif unit < x and x <= 1440 * 3600:
            x = 2 / 1439 / 3600 * x + 6 - 2 / 1439
        else:
            x = 6 / (maxvv - 1440 * 3600) * x + 14 - 6 * maxvv / (maxvv - 1440 * 3600)

        return x

    # 《深夜小狗离奇事件》
    def dog_transformation_equation(self, x):
        """
        对《歌舞线上》的数据分布的数据进行转换
        :param x: float
        :return: float
        """
        maxvv = self.maxv
        unit = 3600
        if x <= unit:
            x = 5 / 24 / 3600 * x
        elif unit < x and x <= 24 * 3600 * 60:
            x = 5 / 59 / 24 / 3600 * x + 5 - 5 / 59
        else:
            x = 4 / (maxvv - 1440 * 3600) * x + 14 - 4 * maxvv / (maxvv - 1440 * 3600)

        return x

    # 计算购票速度的热力图，获取13张座位分布的numpy矩阵并将值填入矩阵，最终对所有场次取平均。
    def get_distribution_numpy_matrix(self,processed_table_list,seat) -> np.ndarray:
        """
        获取13张座位分布的numpy矩阵并将值填入矩阵。最终对所有场次取平均。
        :param processed_table_list: 列表。有多少个文件该列表就有多少个元素，每个元素是处理过退票后的表格。
        :param seat: 座位的映射表。由read_distribution_map()函数产生
        :return: 填入数值的热力图列表。
        """
        heat_maps = []
        heat_maps.append(np.zeros([1,1]))

        # 这一步生成座位表格
        for num in range(1, 14):
            file_name = self.cwd_2+'\seat_distribution\\NO_' + str(num) + '_seat_distribution.npy'
            a = np.load(file_name, allow_pickle=True)
            res = a.tolist()
            # 列数
            mx_col = 0
            # 行数
            mx_row = 0
            for i in res:
                for j in i:
                    if len(j):
                        mx_col = max(mx_col, j[1])
                        mx_row = max(mx_row, j[0])
            temp = np.zeros([mx_row + 1, mx_col + 1])
            # exec("heat_map_%s=np.zeros([mx_row+1,mx_col+1],dtype=int)"%num)

            # 所有场次最长的购买时间
            self.maxv = self.longest_perchase_time[max(self.longest_perchase_time)]

            if self.theater_name == "巴黎圣母院":
                transfer_maxv = self.balishengmu_transformation_equation1(self.maxv)
            elif self.theater_name == "马修伯恩 天鹅湖":
                transfer_maxv = self.goose_transformation_equation(self.maxv)
            elif self.theater_name == "悲惨世界":
                transfer_maxv = self.world_transformation_equation(self.maxv)
            elif self.theater_name == "歌舞线上":
                transfer_maxv = self.song_transformation_equation(self.maxv)
            elif self.theater_name == "深夜小狗离奇事件":
                transfer_maxv = self.dog_transformation_equation(self.maxv)
            elif self.theater_name == "泰坦尼克号":
                transfer_maxv = self.titanic_transformation_equation(self.maxv)
            elif self.theater_name == "叶普盖尼奥涅金":
                transfer_maxv = self.gold_transformation_equation(self.maxv)
            elif self.theater_name == "德语音乐剧明星音乐会":
                transfer_maxv = self.germanytheater_transformation_equation(self.maxv)

            # 初始化所有的位置
            for i in res:
                for j in i:
                    if len(j):
                        temp[j[0]][j[1]] = transfer_maxv
            heat_maps.append(temp)

        # heat_maps_backup = heat_maps

        if self.flag is False:
            if self.frequence_flag is False:
                self.cal_seat_count(processed_table_list)
            # 这一步将单个表的结果填入上面生成的座位表格
            cnt = 0
            for processed_table in processed_table_list:
                cnt += 1
                for item in processed_table:
                    region = int(item[2])
                    if isinstance(item[3], str):
                        row_num = int("".join(filter(str.isdigit, item[3])))
                    else:
                        row_num = int(item[3])
                    seat_num = int(item[4])
                    try:
                        row = seat[region][row_num][seat_num][0]
                        col = seat[region][row_num][seat_num][1]
                    except IndexError:
                        print("第{}张表，{}区域，{}排，{}座，不存在这个位置！".format(cnt, region, row_num, seat_num))
                    else:
                        """ 将这个位置中的所有耗时取出来，求平均"""
                        cur_array = []
                        nums = 0
                        for k,v in self.previous_seat_count.items():
                            if region * 10000 + row_num * 100 + seat_num in v:
                                nums += 1
                        # remain_num指的是：总场次数 - 预售的场次数 - 散客买的数目
                        # remain >= 0，表示有多少场没有被买，应该添加remain个self.maxv
                        remain_num = self.movie_cnt - nums - len(self.every_seat_cost_time[int(region*10000+row_num*100+seat_num)])
                        for i in range(remain_num):
                            cur_array.append(self.maxv)
                        # 加入散客在该位置的购买耗时
                        for i in self.every_seat_cost_time[int(region*10000+row_num*100+seat_num)]:
                            cur_array.append(i)
                        if len(cur_array) == 0:
                            continue
                        valu = 0
                        for i in cur_array:
                            valu += i
                        # print(valu / len(cur_array))

                        finish_value = valu / len(cur_array)
                        if self.theater_name == "巴黎圣母院":
                            finish_value = self.balishengmu_transformation_equation1(finish_value)
                        elif self.theater_name == "马修伯恩 天鹅湖":
                            finish_value = self.goose_transformation_equation(finish_value)
                        elif self.theater_name == "悲惨世界":
                            finish_value = self.world_transformation_equation(finish_value)
                        elif self.theater_name == "歌舞线上":
                            finish_value = self.song_transformation_equation(finish_value)
                        elif self.theater_name == "深夜小狗离奇事件":
                            finish_value = self.dog_transformation_equation(finish_value)
                        elif self.theater_name == "泰坦尼克号":
                            finish_value = self.titanic_transformation_equation(finish_value)
                        elif self.theater_name == "叶普盖尼奥涅金":
                            finish_value = self.gold_transformation_equation(finish_value)
                        elif self.theater_name == "德语音乐剧明星音乐会":
                            finish_value = self.germanytheater_transformation_equation(finish_value)
                        heat_maps[region][row][col] = finish_value
                        self.perchase_speed_of_seat[int(region * 10000 + row_num * 100 + seat_num)] = heat_maps[region][row][col]
            self.flag = True

        else:
            cnt = 0
            for processed_table in processed_table_list:
                cnt += 1
                for item in processed_table:
                    region = int(item[2])
                    if isinstance(item[3], str):
                        row_num = int("".join(filter(str.isdigit, item[3])))
                    else:
                        row_num = int(item[3])
                    seat_num = int(item[4])
                    try:
                        row = seat[region][row_num][seat_num][0]
                        col = seat[region][row_num][seat_num][1]
                    except IndexError:
                        print("第{}张表，{}区域，{}排，{}座，不存在这个位置！".format(cnt, region, row_num, seat_num))
                    else:
                        # exec("heat_map_%s[row][col] = time_len" % region)
                        heat_maps[region][row][col] = self.perchase_speed_of_seat[int(region * 10000 + row_num * 100 + seat_num)]

        return heat_maps

    # 计算购票频次的热力图，获取13张座位分布的numpy矩阵并将值填入矩阵，最终对所有场次取平均。
    def get_frequency_distribution_numpy_matrix(self, processed_table_list, seat) -> np.ndarray:
        """
        获取13张座位分布的numpy矩阵并将值填入矩阵。最终对所有场次取平均。
        :param processed_table_list: 列表。有多少个文件该列表就有多少个元素，每个元素是处理过退票后的表格。
        :param seat: 座位的映射表。由read_distribution_map()函数产生
        :return: 填入数值的热力图列表。
        """
        heat_maps = []
        heat_maps.append(np.zeros([1, 1]))

        # 这一步生成座位表格
        for num in range(1, 14):
            file_name = self.cwd_2 + '\seat_distribution\\NO_' + str(num) + '_seat_distribution.npy'
            a = np.load(file_name, allow_pickle=True)
            res = a.tolist()
            # 列数
            mx_col = 0
            # 行数
            mx_row = 0
            for i in res:
                for j in i:
                    if len(j):
                        mx_col = max(mx_col, j[1])
                        mx_row = max(mx_row, j[0])
            temp = np.zeros([mx_row + 1, mx_col + 1])
            # exec("heat_map_%s=np.zeros([mx_row+1,mx_col+1],dtype=int)"%num)

            # 先把所有的位置置为self.movie_cnt + 10，之后再将是座位的地方变为0
            for i in range(len(temp)):
                for j in range(len(temp[i])):
                    temp[i][j] = self.movie_cnt + 1

            # 将是座位的地方变为0
            for i in res:
                for j in i:
                    if len(j):
                        temp[j[0]][j[1]] = 0
            heat_maps.append(temp)

        # heat_maps_backup = heat_maps

        if self.frequence_flag is False:
            if self.flag is False:  # 防止重复计算，如果计算过购票速度则不需要再进行一次cal_seat_count()
                self.cal_seat_count(processed_table_list)
            # 这一步将单个表的结果填入上面生成的座位表格
            cnt = 0
            for processed_table in processed_table_list:
                cnt += 1
                for item in processed_table:
                    region = int(item[2])
                    if isinstance(item[3], str):
                        row_num = int("".join(filter(str.isdigit, item[3])))
                    else:
                        row_num = int(item[3])
                    seat_num = int(item[4])
                    try:
                        row = seat[region][row_num][seat_num][0]
                        col = seat[region][row_num][seat_num][1]
                    except IndexError:
                        print("第{}张表，{}区域，{}排，{}座，不存在这个位置！".format(cnt, region, row_num, seat_num))
                    else:
                        heat_maps[region][row][col] = self.seat_count[int(region * 10000 + row_num * 100 + seat_num)]
                        self.perchase_frequence_of_seat[int(region * 10000 + row_num * 100 + seat_num)] = heat_maps[region][row][col]
            self.frequence_flag = True

        else:
            cnt = 0
            for processed_table in processed_table_list:
                cnt += 1
                for item in processed_table:
                    region = int(item[2])
                    if isinstance(item[3], str):
                        row_num = int("".join(filter(str.isdigit, item[3])))
                    else:
                        row_num = int(item[3])
                    seat_num = int(item[4])
                    try:
                        row = seat[region][row_num][seat_num][0]
                        col = seat[region][row_num][seat_num][1]
                    except IndexError:
                        print("第{}张表，{}区域，{}排，{}座，不存在这个位置！".format(cnt, region, row_num, seat_num))
                    else:
                        # exec("heat_map_%s[row][col] = time_len" % region)
                        heat_maps[region][row][col] = self.perchase_frequence_of_seat[int(region * 10000 + row_num * 100 + seat_num)]

        return heat_maps

    # 计算结合购票频次与购票速度的整体热力图，获取13张座位分布的numpy矩阵并将值填入矩阵，最终对所有场次取平均。
    def get_ensemble_distribution_numpy_matrix(self, processed_table_list, seat) -> np.ndarray:
        """
        获取13张座位分布的numpy矩阵并将值填入矩阵。最终对所有场次取平均。
        :param processed_table_list: 列表。有多少个文件该列表就有多少个元素，每个元素是处理过退票后的表格。
        :param seat: 座位的映射表。由read_distribution_map()函数产生
        :return: 填入数值的热力图列表。
        """
        speed_heat_maps = self.get_distribution_numpy_matrix(processed_table_list, seat)
        frequence_heat_maps = self.get_frequency_distribution_numpy_matrix(processed_table_list, seat)

        # 对speed_heat_maps做 z-score
        c = []
        # 拉平数组，这样才能使用numpy的求中位数的方法。否则不规则的numpy数组无法求中位数等。
        for i in speed_heat_maps[1:]:
            for j in i:
                for k in j:
                    if k != 0:
                        c.append(14-k)
        ave1 = np.mean(c)
        std1 = np.std(c)
        for i in range(1,len(speed_heat_maps)):
            for j in range(len(speed_heat_maps[i])):
                for k in range(len(speed_heat_maps[i][j])):
                    if speed_heat_maps[i][j][k] != 0:
                        speed_heat_maps[i][j][k] = (14-speed_heat_maps[i][j][k] - ave1) / std1

        # 对frequence_heat_maps做 z-score
        c = []
        # 拉平数组，这样才能使用numpy的求中位数的方法。否则不规则的numpy数组无法求中位数等。
        for i in frequence_heat_maps[1:]:
            for j in i:
                for k in j:
                    if k != self.movie_cnt + 1:
                        c.append(k)
        ave2 = np.mean(c)
        std2 = np.std(c)
        for i in range(1,len(frequence_heat_maps)):
            for j in range(len(frequence_heat_maps[i])):
                for k in range(len(frequence_heat_maps[i][j])):
                    if frequence_heat_maps[i][j][k] != self.movie_cnt + 1:
                        frequence_heat_maps[i][j][k] = (frequence_heat_maps[i][j][k] - ave2) / std2

        heat_maps = []
        for i in range(len(frequence_heat_maps)):
            heat_maps.append(speed_heat_maps[i] + frequence_heat_maps[i])
        """
            为了在显示热力图时，能够让各个座位的视角效果差异上更加明显，我们可以将不是座位的地方（即值为self.movie_cnt+1）
            的值设为所有座位中值最大的数值+0.5。
        """
        c = []
        # 拉平数组，这样才能使用numpy的求中位数的方法。否则不规则的numpy数组无法求中位数等。
        for i in heat_maps[1:]:
            for j in i:
                for k in j:
                    if k != self.movie_cnt + 1:
                        c.append(k)

        self.ensemble_mask = max(c) + 0.5

        for i in range(1,len(heat_maps)):
            for j in range(len(heat_maps[i])):
                for k in range(len(heat_maps[i][j])):
                    if heat_maps[i][j][k] == self.movie_cnt + 1:
                        heat_maps[i][j][k] = self.ensemble_mask

        return heat_maps

    # 画购票速度热力图
    def draw_heat_map(self, heat_map, save_file_path):
        """
        生成热力图
        :param heat_map: numpy的array类型。表示每个位置的热力值。
        :return: void。生成热力图。
        """

        c = []
        # 拉平数组，这样才能使用numpy的求中位数的方法。否则不规则的numpy数组无法求中位数等。
        for i in heat_map:
            for j in i:
                for k in j:
                    c.append(k)

        c = np.array(c)

        # print(c)

        # 定义颜色条的显示范围
        med = np.median(c)     # median number
        minv = np.min(c)       # min number
        maxv = np.max(c)       # max number
        # med = None  # median number
        # minv = None  # min number
        # maxv = None  # max number

        # 定义渐变颜色条（白色-蓝色-红色）
        # my_colormap = LinearSegmentedColormap.from_list("", ["red", "orange", "green"])

        # 分别画各区域的图，并保存
        for i in range(1,14):
            sns.heatmap(heat_map[i], linewidths=0.05, linecolor="grey", center=med, vmax=maxv, vmin=minv, mask=heat_map[i] == 0,
                        cmap=self.heatmap_theme)
            plt.axis('off')
            file_named = save_file_path+'\《'+ self.theater_name + "》"+self.ni_seat_number[i]+"购票速度热力图.png"
            plt.savefig(file_named,dpi=500,bbox_inches = 'tight')
            plt.close()

        fig = plt.figure(num = "《"+ self.theater_name + "》整体购票速度热力图")

        # 表1
        plt.axes([0.05, 0.57, 0.9, 0.42])
        sns.heatmap(heat_map[1], cbar=False,linewidths=0.05, linecolor="grey",center=med, vmax=maxv, vmin=minv, mask=heat_map[1] == 0, cmap=self.heatmap_theme)
        plt.axis('off')

        # 表2
        plt.axes([0.1, 0.46, 0.14, 0.09])
        sns.heatmap(heat_map[2], cbar=False,linewidths=0.05, linecolor="grey",center=med, vmax=maxv, vmin=minv, mask=heat_map[2] == 0, cmap=self.heatmap_theme)
        plt.axis('off')

        # 表3
        plt.axes([0.71, 0.46, 0.15, 0.09])
        sns.heatmap(heat_map[3], cbar=False,linewidths=0.05, linecolor="grey",center=med, vmax=maxv, vmin=minv, mask=heat_map[3] == 0, cmap=self.heatmap_theme)
        plt.axis('off')

        # 表4
        plt.axes([0.45,0.37,0.09,0.05])
        sns.heatmap(heat_map[4], cbar=False,linewidths=0.05, linecolor="grey",center=med, vmax=maxv, vmin=minv, mask=heat_map[4] == 0, cmap=self.heatmap_theme)
        plt.axis('off')

        # 表5
        plt.axes([0.56, 0.37, 0.09, 0.07])
        sns.heatmap(heat_map[5], cbar=False,linewidths=0.05, linecolor="grey",center=med, vmax=maxv, vmin=minv, mask=heat_map[5] == 0, cmap=self.heatmap_theme)
        plt.axis('off')

        # 表6
        plt.axes([0.34, 0.37, 0.09, 0.07])
        sns.heatmap(heat_map[6], cbar=False,linewidths=0.05, linecolor="grey",center=med, vmax=maxv, vmin=minv, mask=heat_map[6] == 0, cmap=self.heatmap_theme)
        plt.axis('off')

        # 表7
        plt.axes([0.71, 0.37, 0.1, 0.07])
        sns.heatmap(heat_map[7], cbar=False,linewidths=0.05, linecolor="grey",center=med, vmax=maxv, vmin=minv, mask=heat_map[7] == 0, cmap=self.heatmap_theme)
        plt.axis('off')

        # 表8
        plt.axes([0.17, 0.37, 0.1, 0.07])
        sns.heatmap(heat_map[8], cbar=False,linewidths=0.05, linecolor="grey",center=med, vmax=maxv, vmin=minv, mask=heat_map[8] == 0, cmap=self.heatmap_theme)
        plt.axis('off')

        # 表9
        plt.axes([0.84, 0.37, 0.1, 0.07])
        sns.heatmap(heat_map[9], cbar=False,linewidths=0.05, linecolor="grey",center=med, vmax=maxv, vmin=minv, mask=heat_map[9] == 0, cmap=self.heatmap_theme)
        plt.axis('off')

        # 表10
        plt.axes([0.04, 0.37, 0.1, 0.07])
        sns.heatmap(heat_map[10], cbar=False,linewidths=0.05, linecolor="grey",center=med, vmax=maxv, vmin=minv, mask=heat_map[10] == 0, cmap=self.heatmap_theme)
        plt.axis('off')

        # 表11
        plt.axes([0.15, 0.26, 0.09, 0.07])
        sns.heatmap(heat_map[11], cbar=False,linewidths=0.05, linecolor="grey",center=med, vmax=maxv, vmin=minv, mask=heat_map[11] == 0, cmap=self.heatmap_theme)
        plt.axis('off')

        # 表12
        plt.axes([0.73, 0.26, 0.09, 0.07])
        sns.heatmap(heat_map[12], cbar=False,linewidths=0.05, linecolor="grey",center=med, vmax=maxv, vmin=minv, mask=heat_map[12] == 0, cmap=self.heatmap_theme)
        plt.axis('off')

        # 表13
        plt.axes([0.05, 0.05, 0.9, 0.2])
        h = sns.heatmap(heat_map[13],cbar = True,cbar_kws = {'orientation' : 'horizontal'},linewidths=0.05, linecolor="grey",center=med, vmax=maxv, vmin=minv, mask=heat_map[13] == 0, cmap=self.heatmap_theme)
        plt.axis('off')

        # 显示
        plt.savefig(save_file_path+"\《"+ self.theater_name + "》整体购票速度热力图.png",dpi=500,bbox_inches = 'tight')
        # plt.show()
        plt.close()

    # 画购票频次热力图
    def draw_frequence_heat_map(self, heat_map, save_file_path):
        """
        生成热力图
        :param heat_map: numpy的array类型。表示每个位置的热力值。
        :return: void。生成热力图。
        """

        c = []
        # 拉平数组，这样才能使用numpy的求中位数的方法。否则不规则的numpy数组无法求中位数等。
        for i in heat_map:
            for j in i:
                for k in j:
                    c.append(k)

        c = np.array(c)

        # print(c)

        # 定义颜色条的显示范围
        med = np.median(c)  # median number
        minv = np.min(c)  # min number
        maxv = np.max(c)  # max number
        # med = None  # median number
        # minv = None  # min number
        # maxv = None  # max number

        # 定义渐变颜色条（白色-蓝色-红色）
        # my_colormap = LinearSegmentedColormap.from_list("", ["red", "orange", "green"])

        # 分别画各区域的图，并保存
        for i in range(1, 14):
            sns.heatmap(heat_map[i], linewidths=0.05, linecolor="grey", center=med, vmax=maxv, vmin=minv,
                        mask=heat_map[i] == self.movie_cnt + 1,
                        cmap=self.heatmap_theme)
            plt.axis('off')
            file_named = save_file_path + '\《'+ self.theater_name + "》"+ self.ni_seat_number[i] + "购票频次热力图.png"
            plt.savefig(file_named,dpi=500,bbox_inches = 'tight')
            plt.close()

        fig = plt.figure(num="《" + self.theater_name + "》整体购票频次热力图")

        # 表1
        plt.axes([0.05, 0.57, 0.9, 0.42])
        sns.heatmap(heat_map[1], cbar=False, linewidths=0.05, linecolor="grey", center=med, vmax=maxv, vmin=minv,
                    mask=heat_map[1] == self.movie_cnt + 1, cmap=self.heatmap_theme)
        plt.axis('off')

        # 表2
        plt.axes([0.1, 0.46, 0.14, 0.09])
        sns.heatmap(heat_map[2], cbar=False, linewidths=0.05, linecolor="grey", center=med, vmax=maxv, vmin=minv,
                    mask=heat_map[2] == self.movie_cnt + 1, cmap=self.heatmap_theme)
        plt.axis('off')

        # 表3
        plt.axes([0.71, 0.46, 0.15, 0.09])
        sns.heatmap(heat_map[3], cbar=False, linewidths=0.05, linecolor="grey", center=med, vmax=maxv, vmin=minv,
                    mask=heat_map[3] == self.movie_cnt + 1, cmap=self.heatmap_theme)
        plt.axis('off')

        # 表4
        plt.axes([0.45, 0.37, 0.09, 0.05])
        sns.heatmap(heat_map[4], cbar=False, linewidths=0.05, linecolor="grey", center=med, vmax=maxv, vmin=minv,
                    mask=heat_map[4] == self.movie_cnt + 1, cmap=self.heatmap_theme)
        plt.axis('off')

        # 表5
        plt.axes([0.56, 0.37, 0.09, 0.07])
        sns.heatmap(heat_map[5], cbar=False, linewidths=0.05, linecolor="grey", center=med, vmax=maxv, vmin=minv,
                    mask=heat_map[5] == self.movie_cnt + 1, cmap=self.heatmap_theme)
        plt.axis('off')

        # 表6
        plt.axes([0.34, 0.37, 0.09, 0.07])
        sns.heatmap(heat_map[6], cbar=False, linewidths=0.05, linecolor="grey", center=med, vmax=maxv, vmin=minv,
                    mask=heat_map[6] == self.movie_cnt + 1, cmap=self.heatmap_theme)
        plt.axis('off')

        # 表7
        plt.axes([0.71, 0.37, 0.1, 0.07])
        sns.heatmap(heat_map[7], cbar=False, linewidths=0.05, linecolor="grey", center=med, vmax=maxv, vmin=minv,
                    mask=heat_map[7] == self.movie_cnt + 1, cmap=self.heatmap_theme)
        plt.axis('off')

        # 表8
        plt.axes([0.17, 0.37, 0.1, 0.07])
        sns.heatmap(heat_map[8], cbar=False, linewidths=0.05, linecolor="grey", center=med, vmax=maxv, vmin=minv,
                    mask=heat_map[8] == self.movie_cnt + 1, cmap=self.heatmap_theme)
        plt.axis('off')

        # 表9
        plt.axes([0.84, 0.37, 0.1, 0.07])
        sns.heatmap(heat_map[9], cbar=False, linewidths=0.05, linecolor="grey", center=med, vmax=maxv, vmin=minv,
                    mask=heat_map[9] == self.movie_cnt + 1, cmap=self.heatmap_theme)
        plt.axis('off')

        # 表10
        plt.axes([0.04, 0.37, 0.1, 0.07])
        sns.heatmap(heat_map[10], cbar=False, linewidths=0.05, linecolor="grey", center=med, vmax=maxv, vmin=minv,
                    mask=heat_map[10] == self.movie_cnt + 1, cmap=self.heatmap_theme)
        plt.axis('off')

        # 表11
        plt.axes([0.15, 0.26, 0.09, 0.07])
        sns.heatmap(heat_map[11], cbar=False, linewidths=0.05, linecolor="grey", center=med, vmax=maxv, vmin=minv,
                    mask=heat_map[11] == self.movie_cnt + 1, cmap=self.heatmap_theme)
        plt.axis('off')

        # 表12
        plt.axes([0.73, 0.26, 0.09, 0.07])
        sns.heatmap(heat_map[12], cbar=False, linewidths=0.05, linecolor="grey", center=med, vmax=maxv, vmin=minv,
                    mask=heat_map[12] == self.movie_cnt + 1, cmap=self.heatmap_theme)
        plt.axis('off')

        # 表13
        plt.axes([0.05, 0.05, 0.9, 0.2])
        h = sns.heatmap(heat_map[13], cbar=True, cbar_kws={'orientation': 'horizontal'}, linewidths=0.05,
                        linecolor="grey", center=med, vmax=maxv, vmin=minv, mask=heat_map[13] == self.movie_cnt + 1,
                        cmap=self.heatmap_theme)
        plt.axis('off')

        # 显示
        plt.savefig(save_file_path + "\《" + self.theater_name + "》整体购票频次热力图.png",dpi=500,bbox_inches = 'tight')
        # plt.show()
        plt.close()

    # 画结合购票速度和购票频次的热力图
    def draw_ensemble_heat_map(self, heat_map, save_file_path):
        """
        生成热力图
        :param heat_map: numpy的array类型。表示每个位置的热力值。
        :return: void。生成热力图。
        """

        c = []
        # 拉平数组，这样才能使用numpy的求中位数的方法。否则不规则的numpy数组无法求中位数等。
        for i in heat_map:
            for j in i:
                for k in j:
                    c.append(k)

        c = np.array(c)

        # print(c)

        # 定义颜色条的显示范围
        med = np.median(c)  # median number
        minv = np.min(c)  # min number
        maxv = np.max(c)  # max number
        # med = None  # median number
        # minv = None  # min number
        # maxv = None  # max number

        # 定义渐变颜色条（白色-蓝色-红色）
        # my_colormap = LinearSegmentedColormap.from_list("", ["red", "orange", "green"])

        # 分别画各区域的图，并保存
        for i in range(1, 14):
            sns.heatmap(heat_map[i], linewidths=0.05, linecolor="grey", center=med, vmax=maxv, vmin=minv,
                        mask=heat_map[i] == self.ensemble_mask,
                        cmap=self.heatmap_theme)
            plt.axis('off')
            file_named = save_file_path + '\《'+ self.theater_name + "》"+ self.ni_seat_number[i] + "综合热力图.png"
            plt.savefig(file_named,dpi=500,bbox_inches = 'tight')
            plt.close()

        fig = plt.figure(num="《" + self.theater_name + "》整体综合热力图")

        # 表1
        plt.axes([0.05, 0.57, 0.9, 0.42])
        sns.heatmap(heat_map[1], cbar=False, linewidths=0.05, linecolor="grey", center=med, vmax=maxv, vmin=minv,
                    mask=heat_map[1] == self.ensemble_mask, cmap=self.heatmap_theme)
        plt.axis('off')

        # 表2
        plt.axes([0.1, 0.46, 0.14, 0.09])
        sns.heatmap(heat_map[2], cbar=False, linewidths=0.05, linecolor="grey", center=med, vmax=maxv, vmin=minv,
                    mask=heat_map[2] == self.ensemble_mask, cmap=self.heatmap_theme)
        plt.axis('off')

        # 表3
        plt.axes([0.71, 0.46, 0.15, 0.09])
        sns.heatmap(heat_map[3], cbar=False, linewidths=0.05, linecolor="grey", center=med, vmax=maxv, vmin=minv,
                    mask=heat_map[3] == self.ensemble_mask, cmap=self.heatmap_theme)
        plt.axis('off')

        # 表4
        plt.axes([0.45, 0.37, 0.09, 0.05])
        sns.heatmap(heat_map[4], cbar=False, linewidths=0.05, linecolor="grey", center=med, vmax=maxv, vmin=minv,
                    mask=heat_map[4] == self.ensemble_mask, cmap=self.heatmap_theme)
        plt.axis('off')

        # 表5
        plt.axes([0.56, 0.37, 0.09, 0.07])
        sns.heatmap(heat_map[5], cbar=False, linewidths=0.05, linecolor="grey", center=med, vmax=maxv, vmin=minv,
                    mask=heat_map[5] == self.ensemble_mask, cmap=self.heatmap_theme)
        plt.axis('off')

        # 表6
        plt.axes([0.34, 0.37, 0.09, 0.07])
        sns.heatmap(heat_map[6], cbar=False, linewidths=0.05, linecolor="grey", center=med, vmax=maxv, vmin=minv,
                    mask=heat_map[6] == self.ensemble_mask, cmap=self.heatmap_theme)
        plt.axis('off')

        # 表7
        plt.axes([0.71, 0.37, 0.1, 0.07])
        sns.heatmap(heat_map[7], cbar=False, linewidths=0.05, linecolor="grey", center=med, vmax=maxv, vmin=minv,
                    mask=heat_map[7] == self.ensemble_mask, cmap=self.heatmap_theme)
        plt.axis('off')

        # 表8
        plt.axes([0.17, 0.37, 0.1, 0.07])
        sns.heatmap(heat_map[8], cbar=False, linewidths=0.05, linecolor="grey", center=med, vmax=maxv, vmin=minv,
                    mask=heat_map[8] == self.ensemble_mask, cmap=self.heatmap_theme)
        plt.axis('off')

        # 表9
        plt.axes([0.84, 0.37, 0.1, 0.07])
        sns.heatmap(heat_map[9], cbar=False, linewidths=0.05, linecolor="grey", center=med, vmax=maxv, vmin=minv,
                    mask=heat_map[9] == self.ensemble_mask, cmap=self.heatmap_theme)
        plt.axis('off')

        # 表10
        plt.axes([0.04, 0.37, 0.1, 0.07])
        sns.heatmap(heat_map[10], cbar=False, linewidths=0.05, linecolor="grey", center=med, vmax=maxv, vmin=minv,
                    mask=heat_map[10] == self.ensemble_mask, cmap=self.heatmap_theme)
        plt.axis('off')

        # 表11
        plt.axes([0.15, 0.26, 0.09, 0.07])
        sns.heatmap(heat_map[11], cbar=False, linewidths=0.05, linecolor="grey", center=med, vmax=maxv, vmin=minv,
                    mask=heat_map[11] == self.ensemble_mask, cmap=self.heatmap_theme)
        plt.axis('off')

        # 表12
        plt.axes([0.73, 0.26, 0.09, 0.07])
        sns.heatmap(heat_map[12], cbar=False, linewidths=0.05, linecolor="grey", center=med, vmax=maxv, vmin=minv,
                    mask=heat_map[12] == self.ensemble_mask, cmap=self.heatmap_theme)
        plt.axis('off')

        # 表13
        plt.axes([0.05, 0.05, 0.9, 0.2])
        h = sns.heatmap(heat_map[13], cbar=True, cbar_kws={'orientation': 'horizontal'}, linewidths=0.05,
                        linecolor="grey", center=med, vmax=maxv, vmin=minv, mask=heat_map[13] == self.ensemble_mask,
                        cmap=self.heatmap_theme)
        plt.axis('off')

        # 显示
        plt.savefig(save_file_path + "\《" + self.theater_name + "》整体综合热力图.png",dpi=500,bbox_inches = 'tight')
        # plt.show()
        plt.close()

    # 用来将所有要分析的文件进行整体处理。之后可以进行生成分析表和热力图
    def enter_data_process(self) -> list:
        if self.previous_seat_count == {}:
            self.cal_previous_seat_count()
        ls_files_processed_table = []
        for file in self.files_name:
            temp_table = self.process_data(file)
            temp_processed_table = self.process_refund(temp_table)
            ls_files_processed_table.append(temp_processed_table)
        return ls_files_processed_table

    # 画购票速度热力图的总入口
    def enter_draw_speed_heatmap(self, save_file_path, table):
        temp_seat = self.read_distribution_map()
        self.WorkThread.progressbarValue.emit(55)
        heat_map = self.get_distribution_numpy_matrix(table, temp_seat)
        self.WorkThread.progressbarValue.emit(75)
        self.draw_heat_map(heat_map,save_file_path)
        self.WorkThread.progressbarValue.emit(95)

    # 画购票频次热力图的总入口
    def enter_draw_frequence_heatmap(self, save_file_path, table):
        temp_seat = self.read_distribution_map()
        self.WorkThread.progressbarValue.emit(55)
        heat_map = self.get_frequency_distribution_numpy_matrix(table, temp_seat)
        self.WorkThread.progressbarValue.emit(75)
        self.draw_frequence_heat_map(heat_map, save_file_path)
        self.WorkThread.progressbarValue.emit(95)

    # 画结合购票频次和购票速度的热力图的总入口
    def enter_draw_ensemble_heatmap(self, save_file_path, table):
        temp_seat = self.read_distribution_map()
        self.WorkThread.progressbarValue.emit(55)
        heat_map = self.get_ensemble_distribution_numpy_matrix(table, temp_seat)
        self.WorkThread.progressbarValue.emit(75)
        self.draw_ensemble_heat_map(heat_map, save_file_path)
        self.WorkThread.progressbarValue.emit(95)

    # 生成分析表的总入口
    def enter_generate_table(self, save_file_path, processed_table_list):
        speed_array = []
        frequcen_array = []

        if self.flag is False:
            # temp_backup = [0 for _ in range(999999)]
            if self.frequence_flag is False:
                # 计算频次
                self.cal_seat_count(processed_table_list)
            # 计算速度
            for processed_table in processed_table_list:
                for item in processed_table:
                    region = int(item[2])
                    if isinstance(item[3], str):
                        row_num = int("".join(filter(str.isdigit, item[3])))
                    else:
                        row_num = int(item[3])
                    seat_num = int(item[4])

                    """ 将这个位置中的所有耗时取出来，求平均"""
                    cur_array = []
                    nums = 0
                    for k,v in self.previous_seat_count.items():
                        if region * 10000 + row_num * 100 + seat_num in v:
                            nums += 1
                    # remain_num指的是：总场次数 - 预售的场次数 - 散客买的数目
                    # remain >= 0，表示有多少场没有被买，应该添加remain个self.maxv
                    remain_num = self.movie_cnt - nums - len(self.every_seat_cost_time[int(region*10000+row_num*100+seat_num)])
                    for i in range(remain_num):
                        cur_array.append(self.maxv)
                    # 加入散客在该位置的购买耗时
                    for i in self.every_seat_cost_time[int(region*10000+row_num*100+seat_num)]:
                        cur_array.append(i)
                    if len(cur_array) == 0:     # 这里与上面的处理不同（上面是直接continue），因为上面有初始化的过程，这里没有，所以当cur_array中没有数字时，应该将self.maxv放进去
                        cur_array.append(self.maxv)
                    valu = 0
                    for i in cur_array:
                        valu += i
                    # print(valu / len(cur_array))

                    finish_value = valu / len(cur_array)
                    if self.theater_name == "巴黎圣母院":
                        finish_value = self.balishengmu_transformation_equation1(finish_value)
                    elif self.theater_name == "马修伯恩 天鹅湖":
                        finish_value = self.goose_transformation_equation(finish_value)
                    elif self.theater_name == "悲惨世界":
                        finish_value = self.world_transformation_equation(finish_value)
                    elif self.theater_name == "歌舞线上":
                        finish_value = self.song_transformation_equation(finish_value)
                    elif self.theater_name == "深夜小狗离奇事件":
                        finish_value = self.dog_transformation_equation(finish_value)
                    elif self.theater_name == "泰坦尼克号":
                        finish_value = self.titanic_transformation_equation(finish_value)
                    elif self.theater_name == "叶普盖尼奥涅金":
                        finish_value = self.gold_transformation_equation(finish_value)
                    elif self.theater_name == "德语音乐剧明星音乐会":
                        finish_value = self.germanytheater_transformation_equation(finish_value)

                    self.perchase_speed_of_seat[int(region * 10000 + row_num * 100 + seat_num)] = finish_value
                    speed_array.append(14-finish_value)
            self.flag = True

        if self.frequence_flag is False:
            if self.flag is False:
                # 计算频次
                self.cal_seat_count(processed_table_list)
            # 计算频次
            for processed_table in processed_table_list:
                for item in processed_table:
                    region = int(item[2])
                    if isinstance(item[3], str):
                        row_num = int("".join(filter(str.isdigit, item[3])))
                    else:
                        row_num = int(item[3])
                    seat_num = int(item[4])
                    self.perchase_frequence_of_seat[int(region * 10000 + row_num * 100 + seat_num)] = self.seat_count[int(region * 10000 + row_num * 100 + seat_num)]
                    frequcen_array.append(self.perchase_frequence_of_seat[int(region * 10000 + row_num * 100 + seat_num)])
            self.frequence_flag = True

        # 处理某些位置不在预售表和散客表中的情况，这个位置的速度应该是最大
        # 预处理出来最大值的转换值
        finish_value = self.maxv
        if self.theater_name == "巴黎圣母院":
            finish_value = self.balishengmu_transformation_equation1(finish_value)
        elif self.theater_name == "马修伯恩 天鹅湖":
            finish_value = self.goose_transformation_equation(finish_value)
        elif self.theater_name == "悲惨世界":
            finish_value = self.world_transformation_equation(finish_value)
        elif self.theater_name == "歌舞线上":
            finish_value = self.song_transformation_equation(finish_value)
        elif self.theater_name == "深夜小狗离奇事件":
            finish_value = self.dog_transformation_equation(finish_value)
        elif self.theater_name == "泰坦尼克号":
            finish_value = self.titanic_transformation_equation(finish_value)
        elif self.theater_name == "叶普盖尼奥涅金":
            finish_value = self.gold_transformation_equation(finish_value)
        elif self.theater_name == "德语音乐剧明星音乐会":
            finish_value = self.germanytheater_transformation_equation(finish_value)
        # 读取座位表格
        for num in range(1, 14):
            file_name = self.cwd_2 + '\seat_distribution\\NO_' + str(num) + '_seat_distribution.npy'
            a = np.load(file_name, allow_pickle=True)
            res = a.tolist()
            # num就是区域号，i就是排号，j就是列号
            for i in range(len(res)):
                if i == 0:  # 没有第0排
                    continue
                for j in range(len(res[i])):
                    if j == 0:  # 没有第0号座位
                        continue
                    if self.perchase_frequence_of_seat[num*10000+i*100+j] == 0:
                        self.perchase_speed_of_seat[num*10000+i*100+j] = finish_value
                        speed_array.append(14-finish_value)

        # 计算各个座位结合购票速度和购票频率的结果
        ave_speed = np.mean(speed_array)
        std_speed = np.std(speed_array)
        ave_frequence = np.mean(frequcen_array)
        std_frequence = np.std(frequcen_array)

        ensemble_of_seat = [0 for _ in range(999999)]

        for num in range(1, 14):
            file_name = self.cwd_2 + '\seat_distribution\\NO_' + str(num) + '_seat_distribution.npy'
            a = np.load(file_name, allow_pickle=True)
            res = a.tolist()
            # num就是区域号，i就是排号，j就是列号
            for i in range(len(res)):
                if i == 0:  # 没有第0排
                    continue
                for j in range(len(res[i])):
                    if j == 0:  # 没有第0号座位
                        continue
                    ensemble_of_seat[num*10000+i*100+j] = (14-self.perchase_speed_of_seat[num*10000+i*100+j]-ave_speed) / std_speed + (self.perchase_frequence_of_seat[num*10000+i*100+j]-ave_frequence) / std_frequence

        # 创建一个workbook 设置编码
        workbook = xlwt.Workbook(encoding='utf-8')
        # 创建一个worksheet
        worksheet = workbook.add_sheet('分析结果')

        # 写入excel。参数对应 行, 列, 值
        worksheet.write(0, 0, '区域名称')
        worksheet.write(0, 1, '排号')
        worksheet.write(0, 2, '座位号')
        worksheet.write(0, 3, '购票平均耗时')
        worksheet.write(0, 4, '购买频次(次数)')
        worksheet.write(0, 5, '购票速度及频次整合值')
        for i in range(self.movie_cnt):
            worksheet.write(0, 6+i, self.changci_time_name[i])
        data_cnts = 1
        for num in range(1, 14):
            file_name = self.cwd_2+'\seat_distribution\\NO_' + str(num) + '_seat_distribution.npy'
            a = np.load(file_name, allow_pickle=True)
            res = a.tolist()
            # num相当于是区域号，rows_number相当于是排号，cols_number相当于是座位号
            for rows_number in range(len(res)):
                if rows_number == 0:
                    continue
                for cols_number in range(len(res[rows_number])):
                    if cols_number == 0 or len(res[rows_number][cols_number]) == 0:
                        continue
                    worksheet.write(data_cnts, 0, self.ni_seat_number[num])
                    worksheet.write(data_cnts, 1, rows_number)
                    worksheet.write(data_cnts, 2, cols_number)
                    worksheet.write(data_cnts, 3, float(self.perchase_speed_of_seat[num*10000+rows_number*100+cols_number]))
                    worksheet.write(data_cnts, 4, self.seat_count[num*10000+rows_number*100+cols_number])
                    worksheet.write(data_cnts, 5, ensemble_of_seat[num*10000+rows_number*100+cols_number])
                    for i in range(self.movie_cnt):
                        # 判断是否在预售表中， 在预售表中应该填“预售”
                        if self.changci_time_name[i] in self.previous_seat_count.keys():
                            if num*10000+rows_number*100+cols_number in self.previous_seat_count[self.changci_time_name[i]]:
                                worksheet.write(data_cnts, 7 + i, "预售")
                            elif num * 10000 + rows_number * 100 + cols_number in \
                                    self.every_seat_every_changci_cost_time[self.changci_time_name[i]]:
                                worksheet.write(data_cnts, 7 + i,self.every_seat_every_changci_cost_time[self.changci_time_name[i]][num * 10000 + rows_number * 100 + cols_number])
                            else:
                                worksheet.write(data_cnts, 7 + i, "未售出")
                        elif num*10000+rows_number*100+cols_number in self.every_seat_every_changci_cost_time[self.changci_time_name[i]]:
                            worksheet.write(data_cnts, 7 + i, self.every_seat_every_changci_cost_time[self.changci_time_name[i]][num*10000+rows_number*100+cols_number])
                        else:
                            worksheet.write(data_cnts, 7 + i, "未售出")
                    data_cnts += 1

        workbook.save(save_file_path + '\《'+self.theater_name+'》分析结果.xls')

if __name__ == '__main__':
    save_table_path = '.\\res'
    file_paths = []
    rootdir = '.\《巴黎圣母院》（2019、2020）散客购票\《巴黎圣母院》（2020）10场\\'
    ls = os.listdir(rootdir)  # 列出文件夹下所有的目录与文件
    # for i in range(0, 1):
    for i in range(0, len(ls)):
        file_paths.append(rootdir + ls[i])
    # start_time = '2019-9-10/0:0:0'
    # end_time = '2020-01-16/19:30:0'
    sol = Solve(filepath=file_paths, changci=len(file_paths))
    temp_table = sol.enter_data_process()
    sol.enter_draw(temp_table)
    sol.enter_generate_table(save_file_path=save_table_path, processed_table_list=temp_table)