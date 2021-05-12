#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from package import Package


def examples():
    # 小王在上海阿里一年15薪，每月工资4W，每月加班费用为8200
    # 股价入职时候为200美元，美元人民币汇率按7来算，一共15万的股票价值，3万的签字费，股票解禁为两年50%，
    # 后续两年每一年25%，5天工作, 大小周直接填写5.5天，每天工作12小时，7天年假，每年年假 +1
    # 上海的个人五险一金比例为10.5%（养老保险 8%，医疗保险 2%，失业保险0.5%）
    # 上海的公司五险一金比例为28%（养老保险 16%，医疗保险 9.5%，失业保险0.5%，生育保险1%，工伤保险0.16% ~ 1.52%，近似为1%
    # 住房公积金7%，补充公积金5%
    Package(name="ali", num_months=15, monthly_base=40000, monthly_bonus=8200, sign_on_bonus=30000,
            stocks_price=200 * 7, stocks_value=150000, stocks_cliff=2,
            num_workdays=5, daily_working_hours=12,
            pto=7, pto_growth=1,
            individual_insurance_ratio=0.105, company_insurance_ratio=0.28,
            housing_provident_ratio=0.07, supplement_housing_provident_ratio=0.05) \
        .package_stats()


if __name__ == '__main__':
    # 计算工资和年终奖的几个小例子
    examples()
