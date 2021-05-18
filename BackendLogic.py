#-*- coding = utf-8 -*-
#@Time : 2021/5/8 10:03
#@Author : ZXREAPER zhangxu
#@File : BackendLogic.py
#@Software : PyCharm

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import functools
import xlwt
import os
import seaborn as sns
from dateutil.parser import parse
from matplotlib.colors import LinearSegmentedColormap


class Solve:
    def __init__(self,filepath,changci = 1):
        """
        初始化。
        :param filepath: 列表。文件名
        :param changci: 总的场次数
        """
        # 多文件的路径集合。列表。
        self.files_name = filepath
        # 起售时间
        # self.start_time = 0
        # 电影上映时间
        # self.end_time = 0
        # 设置场次数量
        self.movie_cnt = changci
        # 设置座位表所在的路径。
        self.cwd = './'
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
        self.seat_number = {"一楼观众厅": 1, "二楼单号包厢": 2, "二楼双号包厢": 3, "二楼贵宾席V1": 4, "二楼贵宾席V2": 5,
                       "二楼贵宾席V3": 6, "二楼贵宾席V4": 7, "二楼贵宾席V5": 8, "二楼贵宾席V6": 9, "二楼贵宾席V7": 10,
                       "三楼单号包厢": 11, "三楼双号包厢": 12, "三楼观众厅": 13}
        self.ni_seat_number = {1: "一楼观众厅", 2: "二楼单号包厢", 3: "二楼双号包厢", 4: "二楼贵宾席V1", 5: "二楼贵宾席V2",
                          6: "二楼贵宾席V3", 7: "二楼贵宾席V4", 8: "二楼贵宾席V5", 9: "二楼贵宾席V6", 10: "二楼贵宾席V7",
                          11: "三楼单号包厢", 12: "三楼双号包厢", 13: "三楼观众厅"}

        # 用来标记是否已经计算过self.seat_count和self.perchase_speed_of_seat了
        # 若已经计算过了那么就不需要再重复计算了
        self.flag = False

        # 用来记录在这些场次中每个位置被购买的次数
        self.seat_count = [0 for _ in range(999999)]

        # 用来记录在这些场次中每个位置的平均购票耗时
        self.perchase_speed_of_seat = [0 for _ in range(999999)]

    # 读取单张数据表并处理.
    def process_data(self, file_name):
        """
        读取单张数据表并处理。
        :param file_name: 处理的单个文件的文件路径。
        :return: DataFrame。
        """
        org_table = pd.read_excel(file_name, usecols=[0, 1, 3, 4, 5, 6, 8, 9, 10], engine='openpyxl')
        for index, rows in org_table.iterrows():
            org_table['区域名称'][index] = self.seat_number[rows[6]]
        temp_table = org_table
        temp_table['时间间隔'] = 0
        for index, rows in temp_table.iterrows():
            a = parse(str(temp_table["创建日期"][index]))
            b = parse(str(temp_table["开票时间"][index]))
            diff = (a - b).total_seconds()
            if diff < 0:
                # 如果存在创建日期早于开票日期的情况那么购买的折后价格一定是333元或444元，否则就有问题，下面就是判断有没有这样的数据存在
                if temp_table["折后价格"][index] != 333 and temp_table["折后价格"][index] != 444:
                    print(file_name, temp_table["区域名称"][index],temp_table["排"][index],temp_table["座"][index])
                    continue
            temp_table["时间间隔"][index] = diff
            # 创建时间（即购票时间）可能遭遇开票时间，即存在大量预售票的情况
            # print(a,b)
            # print((a - b).total_seconds())
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
            file_name = 'D:/影院座位购票速度热力图/seat_distribution/NO_' + str(i) + '_seat_distribution.npy'
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
        if a[1] == b[1]:
            if a[2] == b[2]:
                if a[3] == b[3]:
                    if a[0] == b[0]:
                        if a[4] < b[4]:
                            return 1
                        else:
                            return -1
                    else:
                        if a[0] < b[0]:
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
        else:
            if a[1] > b[1]:
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
        cur_table = table[['数量', '区域名称', '排', '座', '时间间隔']]
        cur_table = cur_table.values.tolist()
        cur_table.sort(key=functools.cmp_to_key(self.cmp))

        processed_table = []

        last = cur_table[0]
        length = len(cur_table)

        for i in range(1, length):
            if cur_table[i][1] == last[1] and cur_table[i][2] == last[2] and cur_table[i][3] == last[3]:
                if cur_table[i][0] == 1:
                    last.append(cur_table[i][4])
                else:
                    last.pop()
            else:
                processed_table.append(last)
                last = cur_table[i]
        processed_table.append(last)
        return processed_table

    # 计算每个座位出现的次数
    def cal_seat_count(self, processed_table_list):
        """
        用来计算每个座位出现的次数
        :param processed_table_list: 列表。有多少个文件该列表就有多少个元素，每个元素是处理过退票后的表格。
        :return: void。结果回填入self.seat_count列表中。
        """
        # 统计所有场次中每个位置的出现次数
        for processed_table in processed_table_list:
            for item in processed_table:
                region = item[1]
                row_num = item[2]
                seat_num = item[3]
                # if len(item) == 5:这里不能加判断，否则那种买了有退的就会造成除0的情况
                self.seat_count[region*10000+row_num*100+seat_num] += 1


    # 获取13张座位分布的numpy矩阵并将值填入矩阵，最终对所有场次取平均。
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
            file_name = 'D:/影院座位购票速度热力图/seat_distribution/NO_' + str(num) + '_seat_distribution.npy'
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
            temp = np.zeros([mx_row + 1, mx_col + 1], dtype=int)
            # exec("heat_map_%s=np.zeros([mx_row+1,mx_col+1],dtype=int)"%num)
            heat_maps.append(temp)

        if self.flag is False:
            self.cal_seat_count(processed_table_list)
            # 这一步将单个表的结果填入上面生成的座位表格
            cnt = 0
            for processed_table in processed_table_list:
                cnt += 1
                for item in processed_table:
                    region = item[1]
                    row_num = item[2]
                    seat_num = item[3]
                    if len(item) == 5:
                        time_len = item[4]
                    else:
                        time_len = 0
                    # print(cnt, region, row_num, seat_num)
                    try:
                        row = seat[region][row_num][seat_num][0]
                        col = seat[region][row_num][seat_num][1]
                    except IndexError:
                        print("{}张表，{}区域，{}排，{}座，不存在这个位置！".format(cnt, region, row_num, seat_num))
                    else:
                        # exec("heat_map_%s[row][col] = time_len" % region)
                        heat_maps[region][row][col] += (time_len / self.seat_count[region*10000+row_num*100+seat_num])
                        self.perchase_speed_of_seat[region*10000+row_num*100+seat_num] = heat_maps[region][row][col]
            self.flag = True

        else:
            cnt = 0
            for processed_table in processed_table_list:
                cnt += 1
                for item in processed_table:
                    region = item[1]
                    row_num = item[2]
                    seat_num = item[3]
                    if len(item) == 5:
                        time_len = item[4]
                    else:
                        time_len = 0
                    try:
                        row = seat[region][row_num][seat_num][0]
                        col = seat[region][row_num][seat_num][1]
                    except IndexError:
                        print("{}张表，{}区域，{}排，{}座，不存在这个位置！".format(cnt, region, row_num, seat_num))
                    else:
                        # exec("heat_map_%s[row][col] = time_len" % region)
                        heat_maps[region][row][col] = self.perchase_speed_of_seat[region * 10000 + row_num * 100 + seat_num]

        return heat_maps

    # 画热力图
    def draw_heat_map(self, heat_map):
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


        # 定义颜色条的显示范围
        med = np.median(c)     # median number
        minv = np.min(c)       # min number
        maxv = np.max(c)       # max number

        # 定义渐变颜色条（白色-蓝色-红色）
        my_colormap = LinearSegmentedColormap.from_list("", ["red", "orange", "green"])

        # grid = plt.GridSpec(5,7)

        # 分别画各区域的图，并保存
        for i in range(1,14):
            sns.heatmap(heat_map[i], linewidths=0.05, linecolor="grey", center=med, vmax=maxv, vmin=minv, mask=heat_map[i] == 0,
                        cmap='rainbow')
            plt.axis('off')
            file_named = 'D:/影院座位购票速度热力图/'+self.ni_seat_number[i]+".png"
            plt.savefig(file_named)
            plt.close()

        # 表1
        # ax1 = plt.subplot(grid[0,0:7])
        # ax1.margins(2, 2)  # Values >0.0 zoom out
        # ax1.set_title('pic-1')
        plt.axes([0.05, 0.57, 0.9, 0.42])
        sns.heatmap(heat_map[1], cbar=False,linewidths=0.05, linecolor="grey",center=med, vmax=maxv, vmin=minv, mask=heat_map[1] == 0, cmap='rainbow')
        plt.axis('off')

        # 表2
        # ax2 = plt.subplot(grid[1,1:2])
        # ax2.margins(2, 2)  # Values >0.0 zoom out
        # ax2.set_title('pic-2')
        plt.axes([0.1, 0.46, 0.14, 0.09])
        sns.heatmap(heat_map[2], cbar=False,linewidths=0.05, linecolor="grey",center=med, vmax=maxv, vmin=minv, mask=heat_map[2] == 0, cmap='rainbow')
        plt.axis('off')

        # 表3
        # ax3 = plt.subplot(grid[1,6:7])
        # ax3.margins(2, 2)  # Values >0.0 zoom out
        # ax3.set_title('pic-3')
        plt.axes([0.71, 0.46, 0.15, 0.09])
        sns.heatmap(heat_map[3], cbar=False,linewidths=0.05, linecolor="grey",center=med, vmax=maxv, vmin=minv, mask=heat_map[3] == 0, cmap='rainbow')
        plt.axis('off')

        # 表4
        # ax4 = plt.subplot(grid[2,3:4])
        # ax4.margins(2, 2)  # Values >0.0 zoom out
        # ax4.set_title('pic-4')
        plt.axes([0.45,0.37,0.09,0.05])
        sns.heatmap(heat_map[4], cbar=False,linewidths=0.05, linecolor="grey",center=med, vmax=maxv, vmin=minv, mask=heat_map[4] == 0, cmap='rainbow')
        plt.axis('off')

        # 表5
        # ax5 = plt.subplot(grid[2,4:5])
        # ax5.margins(2, 2)  # Values >0.0 zoom out
        # ax5.set_title('pic-5')
        plt.axes([0.56, 0.37, 0.09, 0.07])
        sns.heatmap(heat_map[5], cbar=False,linewidths=0.05, linecolor="grey",center=med, vmax=maxv, vmin=minv, mask=heat_map[5] == 0, cmap='rainbow')
        plt.axis('off')

        # 表6
        # ax6 = plt.subplot(grid[2,2:3])
        # ax6.margins(2, 2)  # Values >0.0 zoom out
        # ax6.set_title('pic-6')
        plt.axes([0.34, 0.37, 0.09, 0.07])
        sns.heatmap(heat_map[6], cbar=False,linewidths=0.05, linecolor="grey",center=med, vmax=maxv, vmin=minv, mask=heat_map[6] == 0, cmap='rainbow')
        plt.axis('off')

        # 表7
        # ax7 = plt.subplot(grid[2,5:6])
        # ax7.margins(2, 2)  # Values >0.0 zoom out
        # ax7.set_title('pic-7')
        plt.axes([0.71, 0.37, 0.1, 0.07])
        sns.heatmap(heat_map[7], cbar=False,linewidths=0.05, linecolor="grey",center=med, vmax=maxv, vmin=minv, mask=heat_map[7] == 0, cmap='rainbow')
        plt.axis('off')

        # 表8
        # ax8 = plt.subplot(grid[2,1:2])
        # ax8.margins(2, 2)  # Values >0.0 zoom out
        # ax8.set_title('pic-8')
        plt.axes([0.17, 0.37, 0.1, 0.07])
        sns.heatmap(heat_map[8], cbar=False,linewidths=0.05, linecolor="grey",center=med, vmax=maxv, vmin=minv, mask=heat_map[8] == 0, cmap='rainbow')
        plt.axis('off')

        # 表9
        # ax9 = plt.subplot(grid[2,6:7])
        # ax9.margins(2, 2)  # Values >0.0 zoom out
        # ax9.set_title('pic-9')
        plt.axes([0.84, 0.37, 0.1, 0.07])
        sns.heatmap(heat_map[9], cbar=False,linewidths=0.05, linecolor="grey",center=med, vmax=maxv, vmin=minv, mask=heat_map[9] == 0, cmap='rainbow')
        plt.axis('off')

        # 表10
        # ax10 = plt.subplot(grid[2,0:1])
        # ax10.margins(2, 2)  # Values >0.0 zoom out
        # ax10.set_title('pic-10')
        plt.axes([0.04, 0.37, 0.1, 0.07])
        sns.heatmap(heat_map[10], cbar=False,linewidths=0.05, linecolor="grey",center=med, vmax=maxv, vmin=minv, mask=heat_map[10] == 0, cmap='rainbow')
        plt.axis('off')

        # 表11
        # ax11 = plt.subplot(grid[3,1:2])
        # ax11.margins(2, 2)  # Values >0.0 zoom out
        # ax11.set_title('pic-11')
        plt.axes([0.15, 0.26, 0.09, 0.07])
        sns.heatmap(heat_map[11], cbar=False,linewidths=0.05, linecolor="grey",center=med, vmax=maxv, vmin=minv, mask=heat_map[11] == 0, cmap='rainbow')
        plt.axis('off')

        # 表12
        # ax12 = plt.subplot(grid[3,6:7])
        # ax12.margins(2, 2)  # Values >0.0 zoom out
        # ax12.set_title('pic-12')
        plt.axes([0.73, 0.26, 0.09, 0.07])
        sns.heatmap(heat_map[12], cbar=False,linewidths=0.05, linecolor="grey",center=med, vmax=maxv, vmin=minv, mask=heat_map[12] == 0, cmap='rainbow')
        plt.axis('off')

        # 表13
        # ax13 = plt.subplot(grid[4,0:7])
        # ax13.margins(2, 2)  # Values >0.0 zoom out
        # ax13.set_title('pic-13')
        plt.axes([0.05, 0.05, 0.9, 0.2])
        h = sns.heatmap(heat_map[13],cbar = True,cbar_kws = {'orientation' : 'horizontal'},linewidths=0.05, linecolor="grey",center=med, vmax=maxv, vmin=minv, mask=heat_map[13] == 0, cmap='rainbow')
        plt.axis('off')

        # 显示
        # fig.tight_layout()
        # plt.subplot_tool()
        plt.savefig("D:/影院座位购票速度热力图/整体热力图.png")
        plt.show()

    # 用来将所有要分析的文件进行整体处理。之后可以进行生成分析表和热力图
    def enter_data_process(self) -> list:
        ls_files_processed_table = []
        for file in self.files_name:
            temp_table = self.process_data(file)
            temp_processed_table = self.process_refund(temp_table)
            ls_files_processed_table.append(temp_processed_table)
        return ls_files_processed_table

    # 画热力图的总入口
    def enter_draw(self, table):
        temp_seat = self.read_distribution_map()
        heat_map = self.get_distribution_numpy_matrix(table, temp_seat)
        self.draw_heat_map(heat_map)

    # 生成分析表的总入口
    def enter_generate_table(self, save_file_path, processed_table_list):
        if self.flag is False:
            # 计算频次
            self.cal_seat_count(processed_table_list)
            # 计算速度
            for processed_table in processed_table_list:
                for item in processed_table:
                    region = item[1]
                    row_num = item[2]
                    seat_num = item[3]
                    if len(item) == 5:
                        time_len = item[4]
                    else:
                        time_len = 0
                    self.perchase_speed_of_seat[region*10000+row_num*100+seat_num] += (time_len / self.seat_count[region*10000+row_num*100+seat_num])
            self.flag = True

        # 创建一个workbook 设置编码
        workbook = xlwt.Workbook(encoding='utf-8')
        # 创建一个worksheet
        worksheet = workbook.add_sheet('分析结果')

        # 写入excel。参数对应 行, 列, 值
        worksheet.write(0, 0, '区域名称')
        worksheet.write(0, 1, '排号')
        worksheet.write(0, 2, '座位号')
        worksheet.write(0, 3, '购票平均耗时(秒)')
        worksheet.write(0, 4, '购买频次(次数)')
        data_cnts = 1
        for num in range(1, 14):
            file_name = 'D:/影院座位购票速度热力图/seat_distribution/NO_' + str(num) + '_seat_distribution.npy'
            a = np.load(file_name, allow_pickle=True)
            res = a.tolist()
            # num相当于是区域号，rows_number相当于是排号，cols_number相当于是座位号
            for rows_number in range(len(res)):
                if rows_number == 0:
                    continue
                for cols_number in range(len(res[rows_number])):
                    if cols_number == 0 or len(res[rows_number][cols_number]) == 0:
                        continue
                    worksheet.write(data_cnts, 0, num)
                    worksheet.write(data_cnts, 1, rows_number)
                    worksheet.write(data_cnts, 2, cols_number)
                    worksheet.write(data_cnts, 3, float(self.perchase_speed_of_seat[num*10000+rows_number*100+cols_number]))
                    worksheet.write(data_cnts, 4, self.seat_count[num*10000+rows_number*100+cols_number])
                    data_cnts += 1

        workbook.save(save_file_path + '/分析结果.xls')

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
    # sol.enter_draw(temp_table)
    sol.enter_generate_table(save_file_path=save_table_path, processed_table_list=temp_table)