// 新经济系统配置文件
export const CONFIG_ECONOMY = {
  "REGIONS": {
    "rural": {
      "label": "农村",
      "cities": ["xx乡镇A", "xx乡镇B", "xx乡镇C", "xx乡镇D", "xx乡镇E", "xx乡镇F"],
      "salaryMul": 0.60,
      "costMul": 0.55,
      "unemploymentRisk": 0.10,
      "housePriceBase": 280000,
      "houseGrowthMean": 0.00,
      "houseVolatility": 0.05,
      "rentYield": 0.025,
      "commutePenalty": 0.5
    },
    "county": {
      "label": "小县城",
      "cities": ["临川", "仪陇", "诸城", "高邮", "德清", "莒南", "新蔡", "瑞金"],
      "salaryMul": 0.80,
      "costMul": 0.75,
      "unemploymentRisk": 0.08,
      "housePriceBase": 520000,
      "houseGrowthMean": 0.01,
      "houseVolatility": 0.06,
      "rentYield": 0.023,
      "commutePenalty": 0.7
    },
    "city": {
      "label": "城市",
      "cities": ["合肥", "长沙", "杭州", "青岛", "厦门", "成都", "西安", "南京", "苏州", "佛山"],
      "salaryMul": 1.00,
      "costMul": 1.00,
      "unemploymentRisk": 0.07,
      "housePriceBase": 1200000,
      "houseGrowthMean": 0.03,
      "houseVolatility": 0.10,
      "rentYield": 0.020,
      "commutePenalty": 1.0
    },
    "mega": {
      "label": "超一线",
      "cities": ["北京", "上海", "深圳", "广州", "杭州(核心)", "南京(核心)", "成都(核心)", "苏州(核心)"],
      "salaryMul": 1.25,
      "costMul": 1.35,
      "unemploymentRisk": 0.09,
      "housePriceBase": 2600000,
      "houseGrowthMean": 0.04,
      "houseVolatility": 0.15,
      "rentYield": 0.018,
      "commutePenalty": 1.4
    }
  },
  "HOUSING": {
    "defaultAreaSqm": 80,
    "downPaymentRatio": 0.30,
    "mortgageRateAnnual": 0.045,
    "mortgageYears": 30,
    "buyTxnFeeRate": 0.03,
    "sellTxnFeeRate": 0.02,
    "annualMaintenanceRate": 0.01,
    "schoolTierMul": {
      "none": 1.00,
      "weak": 1.05,
      "mid": 1.15,
      "strong": 1.35
    }
  },
  "COSTS": {
    "adultBaseYearly": 28000,
    "childBaseYearly": 15000,
    "utilitiesYearly": 6000,
    "transportYearlyBase": 4000,
    "transportRegionMul": { "rural": 0.8, "county": 1.0, "city": 1.2, "mega": 1.5 },
    "educationYearlyBySchoolTier": { "none": 0, "weak": 5000, "mid": 12000, "strong": 25000 },
    "medicalBaseYearly": 2000,
    "medicalHealthPenaltyK": 10,
    "giftSpendingMean": 5000,
    "giftSpendingVar": 3000,
    "bigTicketProb": 0.05,
    "bigTicketRange": [20000, 80000]
  },
  "EMPLOYMENT": {
    "companyTierThreshold": { "T0": 78, "T1": 72, "T2": 65, "T3": 58 },
    "hireSigmoidS": 8,
    "tierSalaryMul": { "T0": 1.25, "T1": 1.15, "T2": 1.00, "T3": 0.90 },
    "opportunityLambdaBySchool": { "985": 2.2, "211": 1.7, "双非": 1.2, "二本": 1.0 },
    "regionOpportunityMul": { "rural": 0.8, "county": 0.9, "city": 1.0, "mega": 1.2 }
  },
  "PSYCHE_STRAIN": {
    "mortgageStrainK": 0.000004,
    "rentStrainK": 0.000003,
    "unemploymentStrain": 8,
    "strainNaturalRecover": 10,
    "psycheRecoverSmall": 3,
    "psycheDropWhenHighStrain": 2,
    "highStrainThreshold": 80
  }
}