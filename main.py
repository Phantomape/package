#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from matplotlib import pyplot as plt
from package import Package


def examples():
    # 小王在上海阿里每月工资2W，股价入职时候为200美元，美元人民币汇率按7来算，一共15万的股票价值，3万的签字费，股票解禁为两年50%，
    # 后续两年每一年25%，5天工作，每天工作12小时，7天年假，每年年假 +1
    # 上海的五险一金比例为17.5%（养老保险 8%，医疗保险 2%，失业保险0.5%，住房公积金7%）
    Package("ali", 15, 20000, 200 * 7, 150000, 3, 2, 5, 12, 7, 1).package_stats()


if __name__ == '__main__':
    # 计算工资和年终奖的几个小例子
    examples()
