// 计算：高考分布
import { CONFIG_EDU as EDU } from '../config/edu.js'

// Box-Muller 正态分布
function normal(mean, std) {
  let u = 0, v = 0
  while (u === 0) u = Math.random()
  while (v === 0) v = Math.random()
  const z = Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v)
  return Math.round(Math.max(0, Math.min(100, mean + z * std)))
}

// 学习相关"有效成长值"计算：由 竞争力/智力/压力/心理 等共同决定
function academicBase(person, schoolTier) {
  const IQ = person.intelligence ?? 50
  const CP = person.competitiveness ?? 50
  const PSY = person.psyche ?? 50
  const ST = person.strain ?? 50

  // 基础分：智力 60% + 竞争力 30% + 心理 10%
  let mean = 0.6 * IQ + 0.3 * CP + 0.1 * PSY

  // 压力惩罚（>65 才产生负作用；<45 也不佳）
  if (ST > 65) mean -= (ST - 65) * 0.6
  else if (ST < 45) mean -= (45 - ST) * 0.2

  // truancy / gaming 等不良学习习惯惩罚
  const truancy = person.flags?.truancyTimes || 0
  const gaming = person.flags?.gamingHours || 0
  mean -= Math.min(10, truancy * 1.5 + gaming * 0.2)

  // 科目竞赛/模拟考稳定度加分（来自 flags）
  const medals = person.flags?.mathMedals || 0
  mean += medals * 2

  // 上限与下限
  mean = Math.max(15, Math.min(95, mean))

  // 方差
  let std = EDU.STD_BASE
  if (person.flags?.highSchoolLove) std += EDU.STD_LOVE_EXTRA
  if (ST > 70) std *= (1 + EDU.STD_STRAIN_EXTRA)
  // 学校质量越高，模拟考方差更小
  const tierStd = EDU.SCHOOL_QUALITY[schoolTier]?.mockStd ?? 16
  std = Math.round((std + tierStd) / 2)

  return { mean, std }
}

// 返回：{score, percentile, tier}
export function calcGaokaoResult(person, family) {
  // 学校层级（来自住房学区 or 高中选择）
  const schoolTier = person.flags?.highSchoolTier || family.familyAssets?.housing?.schoolTier || 'none'
  const { mean, std } = academicBase(person, schoolTier)

  // 最终分
  const score = normal(mean, std)

  // 简单把分数近似映射到百分位（不是严格统计）
  const percentile = Math.round(score)

  // 映射到学历档
  const tier = EDU.COLLEGE_MAP.find(t => percentile >= t.cut)?.tier || '二本'
  return { score, percentile, tier }
}