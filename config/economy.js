// 经济参数配置
export const CONFIG_ECONOMY = {
  REGIONS: {
    rural: { name: '农村', salaryMul: 0.55, livingBase: 12000, rentBase: 6000, commutePenalty: 1.0 },
    county: { name: '小县城', salaryMul: 0.75, livingBase: 18000, rentBase: 12000, commutePenalty: 1.05 },
    city: { name: '城市', salaryMul: 1.00, livingBase: 28000, rentBase: 30000, commutePenalty: 1.15 },
    mega: { name: '超一线', salaryMul: 1.35, livingBase: 42000, rentBase: 60000, commutePenalty: 1.25 },
  },

  HOUSING: {
    // 学区等级：none/avg/good/top
    schoolTierMul: { none: 0.0, avg: 0.01, good: 0.03, top: 0.06 }, // 智力增益的"上限系数"，而非直接加成
    // 房贷
    downPaymentRatio: 0.35,
    annualRate: 0.046,            // 年化利率（名义）
    years: 30,                    // 30年等额本息
    // 各地区房价"指数（万元/平）"，UI可直接画曲线（12个点表示 12 年）
    PRICE_SERIES: {
      rural: [0.25, 0.26, 0.27, 0.28, 0.29, 0.30, 0.31, 0.33, 0.34, 0.35, 0.36, 0.37],
      county: [0.45, 0.47, 0.49, 0.50, 0.52, 0.55, 0.56, 0.58, 0.60, 0.61, 0.62, 0.63],
      city: [0.9, 0.95, 1.0, 1.05, 1.1, 1.15, 1.18, 1.20, 1.22, 1.23, 1.25, 1.28],
      mega: [1.8, 1.9, 2.0, 2.1, 2.2, 2.35, 2.5, 2.55, 2.6, 2.65, 2.7, 2.8]
    },
    // UI：默认面积区间
    areaOptions: [60, 80, 95, 110],
    rentVolatility: 0.08, // 年波动 ±8%
  },

  // 其它刚性支出项（按家庭维度）
  FAMILY_EXPENSE: {
    car: { has: false, annualFix: 8000, fuelPerYear: 6000 },
    elderCareBase: { min: 6000, max: 12000 }, // 仅当触发赡养事件后启用
  }
}