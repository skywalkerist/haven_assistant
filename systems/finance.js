// 年度收支改造：接入地区薪资系数 & 家庭年度支出
import { CONFIG_ECONOMY as CFG } from '../config/economy.js'
import { computeHousingAnnualCost } from './housing.js'

// 年度：按地区重算个人收入（乘地区系数）
export function recalcIncomeByRegion(person, regionType) {
  const mul = CFG.REGIONS[regionType]?.salaryMul ?? 1
  if (person.income > 0) {
    person.income = Math.round(person.income * mul)
  }
}

// 年度：计算"个人生活成本"（不含房/车/赡养），替换你原来的生活支出
export function computePersonalLiving(person, regionType) {
  const base = CFG.REGIONS[regionType]?.livingBase ?? 28000
  // 心理与压力影响日常额外支出（报复性消费/保健等）
  const psyche = person.psyche ?? 50
  const strain = person.strain ?? 50
  const mentalLeak = Math.max(0, (60 - psyche)) * 80   // 心理差 → 额外花费
  const stressLeak = Math.max(0, (strain - 65)) * 60   // 压力高 → 外卖/保健品
  return Math.round(base + mentalLeak + stressLeak)
}

// 年度：家庭层面的固定其它支出（车、赡养）
export function computeFamilyFixed(game) {
  const car = game.flags?.hasCar ? (game.flags.carAnnual || (8000 + 6000)) : 0
  const elder = game.flags?.elderCareAnnual || 0
  return car + elder
}

// 总家庭年度支出（现金）
export function computeFamilyAnnualExpense(game) {
  const regionType = game.worldState?.regionType || 'city'
  // 1) 房/租
  const housingCost = computeHousingAnnualCost(game)
  // 2) 车/赡养
  const fixed = computeFamilyFixed(game)
  // 3) 家庭成员日常
  const living = game.persons.filter(p => p.isAlive).reduce((sum, p) => {
    return sum + computePersonalLiving(p, regionType)
  }, 0)
  return housingCost + fixed + living
}