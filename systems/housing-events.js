// 住房相关事件模块
import { CONFIG_ECONOMY as CFG } from './config-economy.js'
import { calculateHousePrice, yearlyMortgagePayment, yearlyRent, getRandomCity } from './economy-new.js'

// 住房事件辅助函数
export const HousingEventHelpers = {
  // 计算购房总成本（首付+手续费）
  calculateBuyCost(regionType, schoolTier, priceIndex = 1.0) {
    const totalPrice = calculateHousePrice(regionType, schoolTier, priceIndex)
    const downPayment = totalPrice * CFG.HOUSING.downPaymentRatio
    const txnFee = totalPrice * CFG.HOUSING.buyTxnFeeRate
    return Math.round(downPayment + txnFee)
  },
  
  // 计算租房启动成本（押金+中介费等）
  calculateRentStartCost(regionType, schoolTier, priceIndex = 1.0) {
    const totalPrice = calculateHousePrice(regionType, schoolTier, priceIndex)
    const yearlyRentAmount = yearlyRent(totalPrice, regionType)
    // 按2.5个月租金估算（押一付三+中介费）
    return Math.round(yearlyRentAmount * 2.5 / 12)
  },
  
  // 检查是否能负担购房
  canAffordBuying(globalEconomy, regionType, schoolTier) {
    const cost = this.calculateBuyCost(regionType, schoolTier)
    return globalEconomy >= cost
  }
}

// 1. 结婚后住房选择事件
export const MarriageHousingEvent = {
  id: 'marriage_housing_decision',
  type: '结婚住房选择',
  // 触发条件：刚结婚且没有住房
  when: (person, game) => {
    return person.partner && 
           person.flags?.marriageYear === game.currentYear && 
           game.familyAssets.housing?.mode === 'none'
  },
  
  getOptions: (person, game) => {
    const regionType = game.worldState.regionType
    const options = []
    
    // 选项1：购买中等学区房
    const midTierCost = HousingEventHelpers.calculateBuyCost(regionType, 'mid')
    if (HousingEventHelpers.canAffordBuying(game.globalEconomy, regionType, 'mid')) {
      options.push({
        text: `买房（${regionType === 'mega' ? '超一线' : regionType === 'city' ? '城市' : '县城'}中等学区）`,
        cost: midTierCost,
        effects: {},
        special: 'buyHouse',
        housingData: { 
          mode: 'own', 
          schoolTier: 'mid',
          description: `获得80㎡住房，月供${Math.round(yearlyMortgagePayment(calculateHousePrice(regionType, 'mid')) / 12).toLocaleString()}元`
        }
      })
    }
    
    // 选项2：购买普通学区房（更便宜）
    const weakTierCost = HousingEventHelpers.calculateBuyCost(regionType, 'weak')
    if (HousingEventHelpers.canAffordBuying(game.globalEconomy, regionType, 'weak')) {
      options.push({
        text: `买房（普通片区）`,
        cost: weakTierCost,
        effects: {},
        special: 'buyHouse',
        housingData: { 
          mode: 'own', 
          schoolTier: 'weak',
          description: `获得80㎡住房，月供${Math.round(yearlyMortgagePayment(calculateHousePrice(regionType, 'weak')) / 12).toLocaleString()}元`
        }
      })
    }
    
    // 选项3：租房（普通片区）
    const rentCost = HousingEventHelpers.calculateRentStartCost(regionType, 'weak')
    options.push({
      text: '租房（普通片区）',
      cost: rentCost,
      effects: {},
      special: 'rentHouse',
      housingData: { 
        mode: 'rent', 
        schoolTier: 'weak',
        description: `租赁80㎡住房，月租${Math.round(yearlyRent(calculateHousePrice(regionType, 'weak'), regionType) / 12).toLocaleString()}元`
      }
    })
    
    // 选项4：和父母同住（省钱但影响心理）
    if (game.globalEconomy < weakTierCost * 0.5) { // 经济困难时提供此选项
      options.push({
        text: '和父母同住',
        cost: 0,
        effects: { psyche: -5, strain: 5 },
        special: 'liveWithParents',
        housingData: { 
          mode: 'none', 
          schoolTier: 'none',
          description: '节省住房开支，但影响家庭独立性'
        }
      })
    }
    
    return options
  }
}

// 2. 城市迁移事件
export const RelocateCityEvent = {
  id: 'relocate_city',
  type: '城市迁移',
  cooldownYears: 5, // 5年冷却期
  
  getOptions: (person, game) => {
    const currentRegion = game.worldState.regionType
    const options = []
    
    // 选项1：去超一线城市发展
    if (currentRegion !== 'mega' && person.age <= 35) {
      options.push({
        text: '去超一线城市发展（北上广深）',
        cost: 30000, // 搬家+适应成本
        effects: {},
        special: 'relocateToMega',
        description: '收入+25%，生活成本+35%，更多机会但压力更大'
      })
    }
    
    // 选项2：回到城市/县城寻求稳定
    if (currentRegion === 'mega' && person.age >= 30) {
      const targetRegion = person.stability > 60 ? 'city' : 'county'
      options.push({
        text: `回${targetRegion === 'city' ? '城市' : '小县城'}求稳定`,
        cost: 15000,
        effects: {},
        special: 'relocateToStable',
        targetRegion: targetRegion,
        description: `降低生活成本和压力，收入相应减少`
      })
    }
    
    // 选项3：不迁移，继续当前生活
    options.push({
      text: '不迁移，继续当前生活',
      cost: 0,
      effects: {},
      special: 'stayPut',
      description: '维持现状，稳定发展'
    })
    
    return options
  }
}

// 3. 学区升级/降级事件
export const SchoolTierAdjustEvent = {
  id: 'school_tier_adjust',
  type: '学区调整',
  
  // 触发条件：有房且有未成年子女
  when: (person, game) => {
    const hasMinors = game.persons.some(p => p.isAlive && p.age < 18)
    return game.familyAssets.housing?.mode === 'own' && hasMinors
  },
  
  getOptions: (person, game) => {
    const housing = game.familyAssets.housing
    const currentTier = housing.schoolTier
    const regionType = housing.regionType
    const options = []
    
    // 升级学区选项
    if (currentTier !== 'strong') {
      const targetTier = currentTier === 'mid' ? 'strong' : 
                         currentTier === 'weak' ? 'mid' : 'weak'
      const currentPrice = housing.currentPrice
      const targetPrice = calculateHousePrice(regionType, targetTier, housing.priceIndex)
      const upgradeCost = Math.max(0, 
        (targetPrice - currentPrice) * CFG.HOUSING.downPaymentRatio + 
        targetPrice * CFG.HOUSING.buyTxnFeeRate
      )
      
      if (upgradeCost > 0) {
        options.push({
          text: `升级到${targetTier === 'strong' ? '顶级' : '中等'}学区`,
          cost: Math.round(upgradeCost),
          effects: {},
          special: 'upgradeSchoolTier',
          targetTier: targetTier,
          description: `年教育费用增加${CFG.COSTS.educationYearlyBySchoolTier[targetTier] - CFG.COSTS.educationYearlyBySchoolTier[currentTier]}元，但子女教育质量提升`
        })
      }
    }
    
    // 降级学区选项（套现）
    if (currentTier !== 'none') {
      const targetTier = currentTier === 'strong' ? 'mid' : 
                         currentTier === 'mid' ? 'weak' : 'none'
      const currentPrice = housing.currentPrice
      const targetPrice = calculateHousePrice(regionType, targetTier, housing.priceIndex)
      const cashBack = Math.max(0, 
        Math.round((currentPrice - targetPrice) * (1 - CFG.HOUSING.sellTxnFeeRate))
      )
      
      options.push({
        text: `降级到${targetTier === 'none' ? '无学区' : targetTier === 'weak' ? '普通' : '中等'}片区`,
        cost: -cashBack, // 负数表示获得现金
        effects: { psyche: -2 },
        special: 'downgradeSchoolTier', 
        targetTier: targetTier,
        cashBack: cashBack,
        description: `获得现金${cashBack.toLocaleString()}元，但子女教育环境下降`
      })
    }
    
    // 保持现状
    options.push({
      text: '保持现有学区',
      cost: 0,
      effects: {},
      special: 'keepCurrentTier',
      description: '维持当前教育环境'
    })
    
    return options
  }
}

// 4. 投资性购房事件（高收入者）
export const InvestmentHousingEvent = {
  id: 'investment_housing',
  type: '投资性购房',
  
  // 触发条件：高收入且有充足现金
  when: (person, game) => {
    return person.income > 200000 && 
           game.globalEconomy > 800000 &&
           person.age >= 35 && person.age <= 50
  },
  
  getOptions: (person, game) => {
    const regionType = game.worldState.regionType
    const options = []
    
    // 投资当地房产
    const investCost = HousingEventHelpers.calculateBuyCost(regionType, 'weak')
    options.push({
      text: '投资一套出租房产',
      cost: investCost,
      effects: {},
      special: 'investmentProperty',
      description: `年租金收益约${Math.round(yearlyRent(calculateHousePrice(regionType, 'weak'), regionType)).toLocaleString()}元`
    })
    
    // 不投资
    options.push({
      text: '暂不投资房产',
      cost: 0,
      effects: {},
      special: 'noInvestment',
      description: '保持资金流动性，观望市场'
    })
    
    return options
  }
}