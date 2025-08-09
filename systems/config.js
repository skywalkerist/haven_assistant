export const CONFIG = {
  // 学习与压力
  study: {
    diminishingHours: 5000,
    diminishingPower: 1.2,
    effWeights: { intelligence: 0.5, motivation: 0.3, stability: 0.2 },
    healthPenaltyThreshold: 60, healthPenaltyFactor: 0.8,
    stressPenaltyThreshold: 80, stressPenaltyFactor: 0.6,
    // 学习事件注入
    tutoring: { hours: 200, stress: [5,10] },
    olympic:  { hours: 300, stress: [8,12] },
    hobby:    { hours: 120, stress: [2,6] }
  },

  stress: {
    annualRecovery: 10,
    cap: [0,100],
    burnoutThreshold: 80,
    burnoutProb: 0.2, // 20%
    burnoutEffects: { motivation: -10, performanceMul: 0.8 }
  },

  gaokao: {
    baseSigma: 15,
    loveSigma: 20,
    // 新均值: 智力*1.2；再加学习效率修正 capped [-20, +25]
    effCap: [-20, 25],
    band: [
      {name:'985', min:75, max:100},
      {name:'211', min:50, max:74},
      {name:'双非', min:25, max:49},
      {name:'二本', min:0,  max:24}
    ],
    stateMods: { highStress:-10, highMotivation:+5, stressThreshold:80, motivationThreshold:70 }
  },

  jobs: {
    // 普通职业升职成功率映射：(智/5 + 魅/3 + 学历加成)/100 → 概率
    degreeBonus: { '985':0.08, '211':0.05, '硕士':0.05 },
    salesFormula: { intelDiv:10, charmDiv:1.5 }, // 销售类
    promo: { intervalYears: 3, raisePct: 0.10, healthCost: 2, probClamp:[0.05,0.6] },
    quit: { satisfactionThreshold:40, annualProb:0.15 },
    // 入职基础成功率 0.5，体力活 0.9，辍学特例见原逻辑
    mismatchPenalty: -0.15
  },

  industry: {
    // 行业景气度类别与波动区间
    cycles: [
      { category: 'tech',      every:[5,8],  impact:[-0.2, 0.2] },
      { category: 'creative',  every:[4,7],  impact:[-0.3, 0.3] },
      { category: 'macro',     every:[7,10], impact:[-0.1, 0.1], applyAll:true }
    ],
    // 初始行业乘数
    baseMultiplier: 1.0
  },

  economy: {
    livingMinor: { mean:15000, std:2250, min:5000 },
    livingAdult: { mean:28000, std:4200, min:10000 },
    medicalPenalty: (health)=> Math.max(0, Math.pow(70-health,2)*10),
    lifestyleCreep: { everyYears:10, multiplier:1.2 },
    randomExpense: { prob:0.05, range:[20000,500000] }
  }
}