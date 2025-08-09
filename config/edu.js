// 学业参数配置
export const CONFIG_EDU = {
  // 辅导强度 0~3 的"递减收益"，用于 competitiveness/intelligence 的年增益上限约束
  TUTOR_LEVEL: {
    0: { cost: 0, eff: 0.00 },
    1: { cost: 8000, eff: 0.35 },
    2: { cost: 18000, eff: 0.60 },
    3: { cost: 36000, eff: 0.75 },
  },
  // 学校层级（初/高中的资源质量对"竞争力成长上限"的约束）
  SCHOOL_QUALITY: {
    // none: 普通学校，avg: 一般重点，good:市重点，top:省重点/竞赛氛围
    none: { cap: 0.6, mockStd: 18 },
    avg: { cap: 0.75, mockStd: 16 },
    good: { cap: 0.9, mockStd: 14 },
    top: { cap: 1.0, mockStd: 12 }
  },
  // 高考映射阈值（百分位近似）
  COLLEGE_MAP: [
    { tier: '985', cut: 88 },
    { tier: '211', cut: 70 },
    { tier: '双非', cut: 45 },
    { tier: '二本', cut: 0 },
  ],
  // 结果方差参数
  STD_BASE: 13,
  STD_LOVE_EXTRA: 4,     // 谈恋爱方差增加
  STD_STRAIN_EXTRA: 0.10 // 压力>70附加10%方差
}