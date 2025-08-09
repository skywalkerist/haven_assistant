// 新经济系统模块
import { CONFIG_ECONOMY as CFG } from './config-economy.js'

// 简单正态分布与均匀分布生成器
const randn = (mu = 0, sigma = 1) => {
  let u = 0, v = 0
  while(u === 0) u = Math.random() // 避免0
  while(v === 0) v = Math.random()
  const z = Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v)
  return mu + sigma * z
}

const randRange = (a, b) => a + Math.random() * (b - a)
const clamp01 = (x) => Math.max(0, Math.min(1, x))

// 年度房价曲线（基于"上一年价格"乘增长率）
export function nextHousePrice(current, regionType, schoolTier) {
  const r = CFG.REGIONS[regionType]
  const mean = r.houseGrowthMean
  const vol = r.houseVolatility
  const growth = Math.max(-0.2, Math.min(0.25, randn(mean, vol))) // 限幅±25%
  
  // 注意：schoolTier 影响已在绝对价格中体现，这里只更新基础增长
  return Math.max(0.6, current * (1 + growth))
}

// 计算年化房贷（等额本息）
export function yearlyMortgagePayment(totalPrice) {
  const dp = CFG.HOUSING.downPaymentRatio
  const principal = totalPrice * (1 - dp)
  const r = CFG.HOUSING.mortgageRateAnnual
  const n = CFG.HOUSING.mortgageYears
  
  if (principal <= 0) return 0
  
  // 年金公式：A = P * r (1+r)^n / ((1+r)^n - 1)
  const A = principal * r * Math.pow(1 + r, n) / (Math.pow(1 + r, n) - 1)
  return A
}

// 计算年租金（租客支出）
export function yearlyRent(totalPrice, regionType) {
  const y = CFG.REGIONS[regionType].rentYield
  return totalPrice * y
}

// 计算个人"名义工资"（地域×岗位×个人竞争力）
export function calcAnnualSalary(person, regionType, CAREERS) {
  if (!person.occupation) return 0
  
  const c = CAREERS[person.occupation] || { minSalary: 60000, maxSalary: 120000 }
  const base = c.minSalary
  const range = c.maxSalary - c.minSalary
  
  // 用 competitiveness 或综合能力转化到 [0,1]
  const competitiveness = person.competitiveness || 
    Math.min(100, (person.intelligence * 0.4 + person.charm * 0.3 + person.stability * 0.3))
  
  const perfPct = clamp01((competitiveness - 40) / 40) // 40→0, 80→1
  let salary = base + range * perfPct
  
  // 地域调整
  salary *= CFG.REGIONS[regionType].salaryMul
  
  return Math.round(salary)
}

// 失业月数（按地域风险与满意度/心理）
export function unemployedMonths(person, regionType) {
  const baseRisk = CFG.REGIONS[regionType].unemploymentRisk
  const psycheBad = (person.psyche || 50) < 40 ? 0.03 : 0
  const satBad = (person.satisfaction || 60) < 40 ? 0.02 : 0
  const p = Math.min(0.25, baseRisk + psycheBad + satBad)
  
  // 期望失业月数 + 随机波动
  const m = Math.max(0, Math.round(12 * p + randn(0, 1)))
  return Math.min(6, m) // 最大6个月失业
}

// 年度生活成本（成人/儿童）
export function yearlyLivingCost(person, family, regionType) {
  const adults = family.persons.filter(p => p.isAlive && p.age >= 18).length
  const minors = family.persons.filter(p => p.isAlive && p.age < 18).length
  const costMul = CFG.REGIONS[regionType].costMul

  // 基础生活成本
  let living = adults * CFG.COSTS.adultBaseYearly * costMul +
               minors * CFG.COSTS.childBaseYearly * costMul

  // 水电费
  living += CFG.COSTS.utilitiesYearly

  // 交通费（地域差异）
  living += CFG.COSTS.transportYearlyBase * (CFG.COSTS.transportRegionMul[regionType] || 1)

  // 教育年费：按家庭住房的学区等级
  const schoolTier = family?.familyAssets?.housing?.schoolTier || 'none'
  living += CFG.COSTS.educationYearlyBySchoolTier[schoolTier] || 0

  // 医疗（健康<70的指数惩罚）
  const h = Math.max(0, 70 - (person.health || 50))
  living += CFG.COSTS.medicalBaseYearly + (h * h) * CFG.COSTS.medicalHealthPenaltyK

  // 随机礼金/人情
  const gifts = Math.max(0, randn(CFG.COSTS.giftSpendingMean, CFG.COSTS.giftSpendingVar))
  living += gifts

  // 大额一次性支出
  if (Math.random() < CFG.COSTS.bigTicketProb) {
    living += randRange(CFG.COSTS.bigTicketRange[0], CFG.COSTS.bigTicketRange[1])
  }

  return Math.round(living)
}

// 住房相关的年支出：房贷/租金 + 维护
export function yearlyHousingCost(family, regionType) {
  const housing = family?.familyAssets?.housing
  if (!housing || housing.mode === 'none') return 0
  
  const price = housing.currentPrice || 0
  let cost = 0
  
  if (housing.mode === 'own') {
    cost += yearlyMortgagePayment(price)
    cost += price * CFG.HOUSING.annualMaintenanceRate
  } else if (housing.mode === 'rent') {
    cost += yearlyRent(price, regionType)
  }
  
  return Math.round(cost)
}

// 把一切合并为"个人经济贡献"，并给 strain/psyche 反馈
export function computeAnnualEconomics(person, game, CAREERS) {
  const regionType = game.worldState?.regionType || 'city'
  const family = game // 直接用 gameStore 作为家庭上下文

  // 名义工资与失业月数
  const nominal = calcAnnualSalary(person, regionType, CAREERS)
  const um = unemployedMonths(person, regionType)
  const effectiveIncome = Math.round(nominal * (12 - um) / 12)

  // 住房成本：按成年人均摊
  const adults = family.persons.filter(p => p.isAlive && p.age >= 18).length || 1
  const housingCost = yearlyHousingCost(family, regionType) / adults

  // 生活成本个体份额
  const baseLiving = yearlyLivingCost(person, family, regionType)
  const livingShare = baseLiving / Math.max(1, adults)

  // 合计支出
  const totalExpense = Math.round(livingShare + housingCost)
  const contribution = effectiveIncome - totalExpense

  // 反馈到心理与综合压力
  const totalHousingLoad = yearlyHousingCost(family, regionType)
  const strainAdd = (family.familyAssets?.housing?.mode === 'own')
    ? totalHousingLoad * CFG.PSYCHE_STRAIN.mortgageStrainK
    : totalHousingLoad * CFG.PSYCHE_STRAIN.rentStrainK

  // 更新压力值
  person.strain = Math.max(0, Math.min(100, 
    (person.strain || 50) + 
    strainAdd + 
    (um > 0 ? CFG.PSYCHE_STRAIN.unemploymentStrain : 0) - 
    CFG.PSYCHE_STRAIN.strainNaturalRecover
  ))

  // 根据压力更新心理健康
  if (person.strain > CFG.PSYCHE_STRAIN.highStrainThreshold) {
    person.psyche = Math.max(0, (person.psyche || 50) - CFG.PSYCHE_STRAIN.psycheDropWhenHighStrain)
  } else {
    person.psyche = Math.min(100, (person.psyche || 50) + CFG.PSYCHE_STRAIN.psycheRecoverSmall)
  }

  // 设置经济贡献
  person.economicContribution = contribution

  return { effectiveIncome, totalExpense, contribution }
}

// 初始化随机城市选择
export function getRandomCity(regionType) {
  const cities = CFG.REGIONS[regionType]?.cities || []
  return cities[Math.floor(Math.random() * cities.length)] || '未知城市'
}

// 计算房屋当前价格（考虑学区加成）
export function calculateHousePrice(regionType, schoolTier, priceIndex = 1.0) {
  const base = CFG.REGIONS[regionType].housePriceBase
  const tierMul = CFG.HOUSING.schoolTierMul[schoolTier]
  return Math.round(base * tierMul * priceIndex)
}