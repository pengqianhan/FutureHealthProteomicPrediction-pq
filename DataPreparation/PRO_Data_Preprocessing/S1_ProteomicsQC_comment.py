# This file simply try to find the proportion of missingness in each individuals
# Individuals with Prop of NA>30% will be removed for further modeling and statistical analysis

import glob  # 导入 glob 模块，用于 Unix 风格的路径名模式扩展
import os  # 导入 os 模块，提供一种使用操作系统依赖功能的方法
import numpy as np  # 导入 numpy，用于数值运算
import pandas as pd  # 导入 pandas，用于数据操作
import re  # 导入 re，用于正则表达式操作

# dpath = '/Volumes/JasonWork/Projects/UKB_Proteomics/Data/'  # 设置数据目录路径（已注释）
# pro_df = pd.read_csv(dpath + 'Proteomics_RAW/Proteomics_ins0.csv')  # 从目录读取 CSV 文件（已注释）
dpath = r'olink_data_proteomics.csv'  # CSV 文件的路径
pro_df = pd.read_csv(dpath)  # 将 CSV 文件读入 DataFrame
my_eid_lst = pro_df.eid.tolist()  # 将 'eid' 列的值提取到列表中
nb_eids = len(my_eid_lst)  # 计算 'eid' 条目的数量
my_pros_lst = pro_df.columns.tolist()[:-1]  # 提取除最后一个之外的所有列名


### 以下代码块用于计算 NA 值的比例，并删除 NA 比例超过 30% 的列
na_prop_lst = []  # 初始化一个列表以存储每列的 NA 值比例
for my_pros in my_pros_lst:  # 遍历列表中的每一列
    tmpdf = pro_df[my_pros]  # 从 DataFrame 中提取列
    nb_na = len(np.where(tmpdf.isna() == True)[0])  # 计算列中 NA 值的数量
    na_prop_lst.append(np.round(nb_na/nb_eids, 3))  # 计算并追加 NA 值的比例

na_pros_df = pd.DataFrame({'Pros': my_pros_lst, 'NA_prop':na_prop_lst})  # 创建一个包含列名和其 NA 比例的 DataFrame
# print(na_pros_df)
na_pros_df.sort_values(ascending=False, by = ['NA_prop'], inplace = True)  # 按 NA 比例降序排序 DataFrame
pros_beyond_na30_lst = na_pros_df.loc[na_pros_df.NA_prop>0.3].Pros.tolist()  # 列出 NA 比例超过 30% 的列
pro_df.drop(pros_beyond_na30_lst, axis = 1, inplace=True)  # 从 DataFrame 中删除 NA 比例超过 30% 的列

nb_pros = pro_df.shape[1] -1  # 计算列数（不包括 'eid'）

### 以下代码块用于计算 NA 值的比例，并删除 NA 比例超过 30% 的行
na_prop_pros_lst = []  # 初始化一个列表以存储每行的 NA 值比例
for my_eid in my_eid_lst:  # 遍历每个 'eid'
    tmpdf = pro_df.loc[pro_df.eid == my_eid]  # 提取对应 'eid' 的行
    nb_na = len(np.where(tmpdf.isna() == True)[0])  # 计算行中 NA 值的数量
    na_prop_pros_lst.append(np.round(nb_na/nb_pros, 3))  # 计算并追加 NA 值的比例

na_eid_df = pd.DataFrame({'eid': my_eid_lst, 'NA_prop':na_prop_pros_lst})  # 创建一个包含 'eid' 及其 NA 比例的 DataFrame
na_eid_df.sort_values(ascending=False, by = ['NA_prop'], inplace = True)  # 按 NA 比例降序排序 DataFrame

eid_beyond_na30_lst = na_eid_df.loc[na_eid_df.NA_prop>0.3].eid.tolist()  # 列出 NA 比例超过 30% 的 'eid'
pro_df = pro_df[~pro_df.eid.isin(eid_beyond_na30_lst)]  # 从 DataFrame 中移除 NA 比例超过 30% 的行

pro_id_lst = pro_df.columns[:-1].tolist()  # 提取除最后一个之外的所有列名
pro_df_preprocessed = pro_df[['eid'] + pro_id_lst]  # 创建一个新的 DataFrame，包含 'eid' 和剩余的列
# pro_df_preprocessed.to_csv(dpath + 'Proteomics_RAW/Proteomics_S1QC.csv', index = False)  # 将预处理后的 DataFrame 保存为 CSV 文件（已注释）
pro_df_preprocessed.to_csv('Proteomics_RAW/Proteomics_S1QC.csv', index = False)  # 将预处理后的 DataFrame 保存为 CSV 文件
