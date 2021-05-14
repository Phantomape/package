#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from package import Package


def examples():
    # 小王在上海腾讯一年16薪，每月工资3.75W，每月加班费用为0，3万的签字费
    # 股价入职时候为80美元，美元人民币汇率按6.5来算，每年15万的股票
    # 5天工作，每天工作10小时，7天年假，每年年假 +1
    # 上海的平均工资为9339元， 这个数字明年7月都要更新一次
    # 上海的个人五险一金比例为10.5%（养老保险 8%，医疗保险 2%，失业保险0.5%）
    # 上海的公司五险一金比例为28%（养老保险 16%，医疗保险 9.5%，失业保险0.5%，生育保险1%，工伤保险0.16% ~ 1.52%，近似为1%
    # 住房公积金7%，补充公积金5%
    Package(name="tencent", num_months=16, monthly_base=37500, monthly_bonus=0, sign_on_bonus=30000,
            stocks_price=80 * 6.5, stocks_value=150000,
            num_workdays=5, daily_working_hours=12,
            pto=7, pto_growth=1, avg_monthly_salary=9339.0,
            individual_insurance_ratio=0.105, company_insurance_ratio=0.28,
            housing_provident_ratio=0.07, supplement_housing_provident_ratio=0.05,
            options_price=0, options_ratio=[0] * 12, options_num_shares=0) \
        .package_stats()

    # 小吴在上海头条一年15薪，每月工资4.5W，每月加班费用为8200
    # 没有股票收益，没有签字费，大小周，每天工作12小时，7天年假，每年年假 +1
    # 期权入职时候为190美元，美元人民币汇率按6.5来算，一共243股期权分四年，比例依次为15%，25%，25%，35%
    # 上海的平均工资为9339元，这个数字明年7月都要更新一次
    # 上海的个人五险一金比例为10.5%（养老保险 8%，医疗保险 2%，失业保险0.5%）
    # 上海的公司五险一金比例为28%（养老保险 16%，医疗保险 9.5%，失业保险0.5%，生育保险1%，工伤保险0.16% ~ 1.52%，近似为1%
    # 住房公积金7%，补充公积金5%
    Package(name="bytedance", num_months=15, monthly_base=45000, monthly_bonus=8200, sign_on_bonus=0,
            stocks_price=0, stocks_value=0,
            options_price=190 * 6.5, options_ratio=[0.15, 0.25, 0.25, 0.35], options_num_shares=243,
            num_workdays=5.5, daily_working_hours=12,
            pto=7, pto_growth=1, avg_monthly_salary=9339.0,
            individual_insurance_ratio=0.105, company_insurance_ratio=0.28,
            housing_provident_ratio=0.07, supplement_housing_provident_ratio=0.05) \
        .package_stats()


if __name__ == '__main__':
    # 计算工资和年终奖的几个小例子
    examples()
