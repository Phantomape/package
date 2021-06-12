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

    def __init__(self, name: str, num_months, monthly_base: float,
                 sign_on_bonus: float, monthly_bonus: float, individual_insurance_ratio: float,
                 company_insurance_ratio: float, avg_monthly_salary: float,
                 options_price: float, options_num_shares: float, options_ratio: list,
                 housing_provident_ratio: float, supplement_housing_provident_ratio: float,
                 stocks_price: float, stocks_value: float, stocks_growth_ratio: float, stocks_ratio: list,
                 num_workdays: float, daily_working_hours: int, pto: int, pto_growth: int):
        # 公司
        self.name = name

        # 当地平均工资, 社保缴费基数上限为3倍当地平均工资
        self.avg_monthly_salary = avg_monthly_salary

        # 现金部分
        self.num_months = num_months
        self.monthly_base = monthly_base

        # 加班费
        self.monthly_bonus = monthly_bonus

        # 签字费，目前不参与总包计算，只是做个样子
        self.sign_on_bonus = sign_on_bonus

        # 每年股票总额
        self.stocks_value = stocks_value

        # 股票授予日价格
        self.stocks_price = stocks_price

        # 股票每年增幅比例, 这个变量名字有待商榷
        self.stocks_growth_ratio = stocks_growth_ratio

        # 每一年股票解禁的比例以及股数，一般都会报一个总价然后分多少年授予，因此每年授予的比例就放在stock_ratio里面，然后计算一下总的股数以及
        # 后续每一年的股数，这里就统一向上取整数，后续建议改成直接赋值为股票数目填进来，能省很多奇怪的取整逻辑
        self.stocks_ratio = stocks_ratio
        self.stocks_num_shares_yearly = list()
        for ratio in self.stocks_ratio:
            if ratio == 0.0:
                self.stocks_num_shares_yearly.append(0)
            else:
                self.stocks_num_shares_yearly.append(stocks_value / stocks_price)

        # 期权相关
        self.options_price = options_price
        self.options_num_shares = options_num_shares

        # 其实想描述每一年期权解禁的比例，没有想到合适的词
        self.options_ratio = options_ratio

        # 工作时间
        self.num_workdays = num_workdays
        self.daily_working_hours = daily_working_hours
        self.pto = pto
        self.pto_growth = pto_growth

        # 社保
        self.individual_insurance_ratio = individual_insurance_ratio
        self.company_insurance_ratio = company_insurance_ratio

        # 公积金缴纳比例
        self.housing_provident_ratio = housing_provident_ratio
        self.supplement_housing_provident_ratio = supplement_housing_provident_ratio

        # 公积金缴纳上限由当地平均工资决定，并且最后四舍五入
        self.max_housing_provident = float(round(self.avg_monthly_salary * 3 * self.housing_provident_ratio * 2))
        self.max_sup_housing_provident = float(
            round(self.avg_monthly_salary * 3 * self.supplement_housing_provident_ratio * 2))

    def get_options_gain(self, year: int) -> float:
        """
        期权算收益只能拿回购价格 * 比例系数 - 行权价格来算，真的很难算，还是按照股票那样随便算一下先 -.-
        :param year: 工作年限
        :return:
        """
        year_idx = year - 1
        if year_idx >= len(self.options_ratio):
            raise Exception("options_ratio has smaller number of length compared with year")

        return self.options_num_shares * self.options_ratio[year_idx] * self.options_price

    def get_stocks_gain(self, year: int) -> float:
        """
        根据个人所得税法计算，来源：https://www.shui5.cn/article/97/134633.html，这里只计算RSU，而且统一设置取得RSU时候所要支付的那
        笔钱，以10000代替，具体参考上面网址里面的例子
        :param year: 工作年限
        :return:
        """
        year_idx = year - 1
        if year_idx >= len(self.stocks_num_shares_yearly):
            raise Exception("stocks_num_shares_yearly has smaller number of length compared with year")

        # 该一年授予的股票数目
        num_shares_granted = self.stocks_num_shares_yearly[year_idx]
        if num_shares_granted == 0:
            return 0.0

        # 该一年行权股票价格
        price_per_share = self.stocks_price * (1.0 + self.stocks_growth_ratio) ** year

        # 股票期权形式的工资薪金应纳税所得额
        total_stocks_num_shares = 0
        for shares in self.stocks_num_shares_yearly:
            total_stocks_num_shares += shares
        total_need_tax = (price_per_share + self.stocks_price) / 2.0 * num_shares_granted - 10000.0 * (
                    num_shares_granted / total_stocks_num_shares)
        if price_per_share <= self.stocks_price:
            total_need_tax = 0

        # 累计应缴税额(累计应缴税额 * 税率 - 速算扣除数) 速算扣除数*12相当于一年
        index = self.get_index_from_sections(total_need_tax)
        total_tax = total_need_tax * rates[index] - deductions[index] * 12

        return price_per_share * num_shares_granted - total_tax

    def get_total_housing_provident(self) -> float:
        """
        计算公积金
        """
        return self.get_housing_provident() + self.get_supplement_housing_provident()

    def get_housing_provident(self):
        """
        计算住房公积金
        :return:
        """
        return min(self.max_housing_provident, self.monthly_base * self.housing_provident_ratio * 2)

    def get_supplement_housing_provident(self):
        """
        计算补充公积金
        :return:
        """
        return min(self.max_sup_housing_provident, self.monthly_base * self.supplement_housing_provident_ratio * 2)

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
                         special - self.get_total_housing_provident() - \
                         min(self.monthly_base, self.avg_monthly_salary * 3) * self.individual_insurance_ratio
            total_need_tax += should_tax
            # 税率区间
            index = self.get_index_from_sections(total_need_tax)
            # 累计应缴税额(累计应缴税额 * 税率 - 速算扣除数) 速算扣除数*12相当于一年
            total_tax = total_need_tax * rates[index] - deductions[index] * 12
            # 当月应缴税(当月累计应缴税 - 上月累计应缴税(累计已缴税))
            cur_tax = total_tax - total_had_tax
            # 当月工资(当月工资=基本工资 + 浮动奖金(绩效工资) - 当月应缴税 - 五险一金)
            cur_sal = default_salary + i - cur_tax - self.get_total_housing_provident() - \
                      min(self.monthly_base, self.avg_monthly_salary * 3) * self.individual_insurance_ratio
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

            options_gain = self.get_options_gain(year)
            print("\t第{}年的期权收益为{}".format(year, options_gain))

            social_insurance = self.get_total_housing_provident() * 12
            print("\t第{}年的公积金为{}".format(year, social_insurance))

            net_package = accumulated_salary + bonus + stocks_gain + social_insurance + options_gain
            print("\t第{}年的税后总共为{}".format(year, net_package))

            hourly_salary = self.get_hourly_salary(net_package, year)
            print("\t第{}年的时薪为{}".format(year, hourly_salary))

            print()
