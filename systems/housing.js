// 住房工具与年度支出整合
import { CONFIG_ECONOMY as CFG } from '../config/economy.js'

export function regionPriceNow(regionType, yearIndex) {
  const series = CFG.HOUSING.PRICE_SERIES[regionType] || []
  const idx = Math.max(0, Math.min(series.length - 1, yearIndex))
  return series[idx] // 单位：万元/平
}

export function annuityPayment(principal, annualRate, years) {
  // 等额本息：A = P * r * (1+r)^n / [(1+r)^n - 1]
  const r = annualRate
  const n = years
  const up = principal * r * Math.pow(1 + r, n)
  const down = Math.pow(1 + r, n) - 1
  return Math.round(up / down) // 年供
}

export function computeHousingAnnualCost(game) {
  const regionType = game.worldState?.regionType || 'city'
  const housing = game.familyAssets?.housing
  if (!housing) return 0

  if (housing.mode === 'rent') {
    // 基准：地区 rentBase，按面积系数、年波动
    const base = CFG.REGIONS[regionType].rentBase
    const areaMul = (housing.area || 80) / 80
    const drift = 1 + (Math.random() * 2 - 1) * CFG.HOUSING.rentVolatility
    return Math.round(base * areaMul * drift)
  }

  if (housing.mode === 'own') {
    // 年供 + 物业维保 + 税费（粗略）
    const annual = housing.annualMortgage || 0
    const hoa = Math.round((housing.area || 90) * 12) // 物业费 12元/平·年
    const tax = Math.round(annual * 0.02)
    return annual + hoa + tax
  }

  return 0
}

export function buildMortgageOnPurchase(game, totalPrice) {
  // totalPrice 单位：元
  const dp = Math.round(totalPrice * CFG.HOUSING.downPaymentRatio)
  const loan = totalPrice - dp
  const annualPay = annuityPayment(loan, CFG.HOUSING.annualRate, CFG.HOUSING.years)
  return { downPayment: dp, loan, annualMortgage: annualPay }
}