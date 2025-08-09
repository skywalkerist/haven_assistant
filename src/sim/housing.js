// 住房系统 - 租房/买房/按揭管理
import { REGION_UNIT_PRICE, REGION_RENT_BASE, SCHOOL_ZONE_PREMIUM, DOWNPAY_DEFAULT, MORTGAGE_RATE, MORTGAGE_YEARS, DEFAULT_HOUSING_REGION } from './constants.js'
import { annuity } from './util.js'

// 设置租房
export function setupRent(store, region, area = 80) {
  const r = region || store.familyAssets?.housing?.region || DEFAULT_HOUSING_REGION
  const monthly = Math.round(REGION_RENT_BASE[r] * (area / 70))
  store.familyAssets.housing = { 
    mode: 'rent', 
    region: r, 
    area, 
    monthlyRent: monthly 
  }
}

// 购买房屋
export function buyHouse(store, region, area, schoolZone) {
  const unit = REGION_UNIT_PRICE[region] * (schoolZone ? SCHOOL_ZONE_PREMIUM : 1)
  const price = Math.round(unit * area)
  const down = Math.round(price * DOWNPAY_DEFAULT)
  
  if (store.globalEconomy < down - 300000) {
    return { ok: false, reason: '现金不足以支付首付（含30万负债缓冲）' }
  }
  
  store.globalEconomy -= down
  const principal = price - down
  const annualPayment = annuity(principal, MORTGAGE_RATE, MORTGAGE_YEARS)
  
  store.familyAssets.housing = {
    mode: 'own',
    region, 
    area, 
    unitPrice: Math.round(unit),
    price, 
    downPayment: down,
    mortgage: { 
      principal, 
      rate: MORTGAGE_RATE, 
      years: MORTGAGE_YEARS, 
      annualPayment, 
      arrears: 0 
    }
  }
  
  return { ok: true }
}

// 年度住房支出
export function payHousingForYear(store) {
  const h = store.familyAssets?.housing
  if (!h) return
  
  if (h.mode === 'rent') {
    const cost = h.monthlyRent * 12
    store.globalEconomy -= cost
  } else if (h.mode === 'own' && h.mortgage) {
    const pay = h.mortgage.annualPayment
    if (store.globalEconomy - pay < -300000) {
      // 不扣款，记逾期
      h.mortgage.arrears = (h.mortgage.arrears || 0) + 1
    } else {
      store.globalEconomy -= pay
      h.mortgage.years = Math.max(0, h.mortgage.years - 1)
      // 逾期回落
      if (h.mortgage.arrears > 0) h.mortgage.arrears--
    }
  }
}

// 住房状态摘要
export function housingSummary(h) {
  if (!h) return '未居住'
  if (h.mode === 'rent') return `租房 · ${h.region} · ${h.area}㎡ · 月租${h.monthlyRent}`
  if (h.mode === 'own') return `按揭 · ${h.region} · ${h.area}㎡ · 年供${h.mortgage?.annualPayment} · 剩${h.mortgage?.years}年`
  return '居住信息异常'
}