// 财务工具函数
export function annuityPayment(principal, annualRate, years) {
  // 年金法：年供 = P * r * (1+r)^n / ((1+r)^n - 1)
  const r = annualRate
  const n = Math.max(1, Math.round(years))
  if (r <= 0) return Math.round(principal / n)
  const up = principal * r * Math.pow(1 + r, n)
  const down = Math.pow(1 + r, n) - 1
  return Math.round(up / down)
}

// 获取房屋年供
export function yearlyMortgage(housing) {
  if (!housing?.mortgage) return 0
  if (housing.mortgage.annualPayment) return housing.mortgage.annualPayment
  if (housing.annualMortgage) return housing.annualMortgage
  const { principal, rate, years } = housing.mortgage
  return annuityPayment(principal, rate, years)
}