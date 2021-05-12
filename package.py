# -------------- 用来计算现金参数和数据
# 工资划分的区间
sections = [36000, 144000, 300000, 420000, 660000, 960000]
# 每个区间对应的税率
rates = [0.03, 0.1, 0.2, 0.25, 0.3, 0.35, 0.45]
# 每个区间对应的速算扣除数
deductions = [0, 210, 1410, 2660, 4410, 7160, 15160]
# 个税起征点
starting_point = 5000
# 专项扣除(住房租金)
special = 1500


class Package:
    """
    用来描述一个offer的package情况
    """

    def __init__(self, name: str, num_months, monthly_base: float, stocks_price: float, stocks_value: float,
                 sign_on_bonus: float, monthly_bonus: float, individual_insurance_ratio: float,
                 company_insurance_ratio: float,
                 housing_provident_ratio: float, supplement_housing_provident_ratio: float,
                 stocks_cliff: int, num_workdays: int, daily_working_hours: int, pto: int, pto_growth: int):
        # 公司
        self.name = name

        # 现金部分
        self.num_months = num_months
        self.monthly_base = monthly_base

        # 加班费
        self.monthly_bonus = monthly_bonus
        # 签字费
        self.sign_on_bonus = sign_on_bonus

        # 股票相关
        self.stocks_value = stocks_value
        self.stocks_price = stocks_price
        self.stocks_num_shares = 0 if stocks_value == 0 else stocks_value / stocks_price
        self.stocks_cliff = stocks_cliff

        # 工作时间
        self.num_workdays = num_workdays
        self.daily_working_hours = daily_working_hours
        self.pto = pto
        self.pto_growth = pto_growth

        # 社保
        self.individual_insurance_ratio = individual_insurance_ratio
        self.company_insurance_ratio = company_insurance_ratio

        # 公积金
        self.housing_provident_ratio = housing_provident_ratio
        self.supplement_housing_provident_ratio = supplement_housing_provident_ratio

    def get_stocks_gain(self, year: int) -> float:
        """
        股票怎么打税，不懂呀 -.-
        :param year: 工作年限
        :return:
        """
        if year < self.stocks_cliff:
            return 0

        return self.stocks_num_shares * self.stocks_price * 0.8

    def get_total_housing_provident(self) -> float:
        """
        计算公积金
        """
        return self.get_housing_provident() + self.get_supplement_housing_provident()

    def get_housing_provident(self, max_housing_provident=3922.0):
        return min(max_housing_provident, self.monthly_base * self.housing_provident_ratio * 2)

    def get_supplement_housing_provident(self, max_sup_housing_provident=2802.0):
        return min(max_sup_housing_provident, self.monthly_base * self.supplement_housing_provident_ratio * 2)

    def get_hourly_salary(self, yearly_salary: float, year: int) -> float:
        # 一年52周, 每年11个法定节假日
        total_working_hours = (52 * self.num_workdays - self.pto - 11 - (
                self.pto_growth * year)) * self.daily_working_hours
        return yearly_salary / total_working_hours

    def get_monthly_salary_list(self, default_salary: float, bonus: list) -> list:
        """计算每个月到手工资

        Arguments:
            default_salary {float} -- 基本工资
            bonus {list} -- 浮动奖金（绩效工资）一年内拿了几次工资就输入几个
            insurance {float} -- 五险一金比例

        Returns:
            list -- 每个月工资
        """
        # 每月工资
        salary_list = []
        # 累计预扣缴额, 累计已缴税额
        total_need_tax, total_had_tax = 0, 0
        for i in bonus:
            # 当月预扣缴额(每月的应缴税 = 基本工资 + 浮动奖金(绩效工资) - 起征点 - 专项扣除 - 五险一金)
            should_tax = default_salary + i - starting_point - \
                         special - self.get_total_housing_provident() - min(self.monthly_base,
                                                                            28017.0) * self.individual_insurance_ratio
            total_need_tax += should_tax
            # 税率区间
            index = self.get_index_from_sections(total_need_tax)
            # 累计应缴税额(累计应缴税额 * 税率 - 速算扣除数) 速算扣除数*12相当于一年
            total_tax = total_need_tax * rates[index] - deductions[index] * 12
            # 当月应缴税(当月累计应缴税 - 上月累计应缴税(累计已缴税))
            cur_tax = total_tax - total_had_tax
            # 当月工资(当月工资=基本工资 + 浮动奖金(绩效工资) - 当月应缴税 - 五险一金)
            cur_sal = default_salary + i - cur_tax - self.get_total_housing_provident() - min(self.monthly_base,
                                                                                              28017.0) * self.individual_insurance_ratio
            salary_list.append(cur_sal)
            total_had_tax = total_tax
        return salary_list

    @staticmethod
    def get_index_from_sections(bonus: float):
        """
        :param bonus:税前年终奖
        :return:返回年终奖所在税率区间
        """
        index = 0
        while index < len(sections) and bonus > sections[index]:
            index = index + 1
        return index

    def get_year_end_bonus(self, bonus: float):
        """
        算年终奖，但是有两种不同的算法，这里只实现了一种
        :param bonus: 税前年终奖
        :return: 税后年终奖
        """
        index = self.get_index_from_sections(bonus)
        # 年终奖纳税 = 税前年终奖 * 税率 - 速算扣除数
        tax = bonus * rates[index] - deductions[index]
        # 税后年终奖 = 税前年终奖 - 年终奖纳税
        return bonus - tax

    def package_stats(self):
        print("-------- {} --------".format(self.name))
        for year in range(1, 4):
            salary_list = self.get_monthly_salary_list(self.monthly_base, [self.monthly_bonus] * 12)
            accumulated_salary = 0
            for s in salary_list:
                accumulated_salary += s
            print("\t第{}年每个月的工资为{}, 总{}".format(year, salary_list, accumulated_salary))

            bonus = self.get_year_end_bonus((self.num_months - 12) * self.monthly_base)
            print("\t第{}年的税后年终奖为{}".format(year, bonus))

            stocks_gain = self.get_stocks_gain(year)
            print("\t第{}年的股票收益为{}".format(year, stocks_gain))

            social_insurance = self.get_total_housing_provident() * 12
            print("\t第{}年的公积金为{}".format(year, social_insurance))

            net_package = accumulated_salary + bonus + stocks_gain + social_insurance
            print("\t第{}年的税后总共为{}".format(year, net_package))

            hourly_salary = self.get_hourly_salary(net_package, year)
            print("\t第{}年的时薪为{}".format(year, hourly_salary))

            print()
