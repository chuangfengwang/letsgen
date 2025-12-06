# -*- coding: utf-8 -*-
"""
# @File    : collection_util.py
# @Desc    : 
# @Author  : chuangfeng.wang
# @Time    : 2025-12-05 15:28
"""

from typing import List


def split_list_evenly(input_list: list, n_splits: int) -> List[list]:
    """
    将一个列表尽可能均匀地切分成 N 份。
    如果列表长度 L 小于切分的份数 N (L < N)，则返回原始列表的单个元素构成的嵌套 list, 最外层元素数量不足 N。
    """

    # 检查 N 是否有效
    if n_splits <= 0:
        raise ValueError("n_splits must be a positive integer (N > 0)")

    list_len = len(input_list)

    # 如果列表长度 L 小于 N，直接返回原始元素构成的列表
    if list_len <= n_splits:
        return [[ele] for ele in input_list]

    # 如果列表为空，返回一个空列表 (如果按照 L < N 的规则，可以考虑返回 [])
    if list_len == 0:
        return []

    # 1. 计算基础大小 (每份最少应有的元素数量)
    base_size = list_len // n_splits

    # 2. 计算余数 (有多少份需要额外多一个元素)
    remainder = list_len % n_splits

    result = []
    current_index = 0

    for i in range(n_splits):
        # 3. 确定当前份的大小
        part_size = base_size + 1 if i < remainder else base_size

        # 4. 切割列表并添加到结果
        end_index = current_index + part_size
        result.append(input_list[current_index:end_index])

        # 5. 更新下一份的起始索引
        current_index = end_index

    return result
