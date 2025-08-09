// 新经济系统集成测试
const { CONFIG_ECONOMY } = require('./systems/config-economy.js')
const { computeAnnualEconomics, calculateHousePrice, getRandomCity } = require('./systems/economy-new.js')

// 模拟基础职业数据
const CAREERS_TEST = {
  '软件工程师': { minSalary: 150000, maxSalary: 400000 },
  '体力活': { minSalary: 25000, maxSalary: 25000 }
}

// 模拟游戏状态
const mockGameState = {
  persons: [
    { isAlive: true, age: 25 }, // 成年人
    { isAlive: true, age: 10 }  // 儿童
  ],
  familyAssets: {
    housing: {
      mode: 'own',
      regionType: 'city',
      schoolTier: 'mid',
      currentPrice: 1200000
    }
  },
  worldState: {
    regionType: 'city',
    useNewEconomics: true
  }
}

// 模拟人物
const mockPerson = {
  age: 30,
  health: 80,
  intelligence: 75,
  charm: 60,
  stability: 70,
  occupation: '软件工程师',
  competitiveness: 75,
  psyche: 50,
  strain: 40,
  children: []
}

console.log('🧪 新经济系统集成测试开始')

// 测试1：配置加载
console.log('1. 测试配置加载...')
console.log('✅ 配置项数量:', Object.keys(CONFIG_ECONOMY).length)
console.log('✅ 地域数量:', Object.keys(CONFIG_ECONOMY.REGIONS).length)

// 测试2：房价计算
console.log('\n2. 测试房价计算...')
const housePrice = calculateHousePrice('city', 'mid', 1.0)
console.log('✅ 城市中等学区房价:', housePrice.toLocaleString(), '元')

// 测试3：随机城市选择
console.log('\n3. 测试随机城市选择...')
const cityName = getRandomCity('mega')
console.log('✅ 随机超一线城市:', cityName)

// 测试4：经济计算
console.log('\n4. 测试年度经济计算...')
try {
  const result = computeAnnualEconomics(mockPerson, mockGameState, CAREERS_TEST)
  console.log('✅ 年收入:', result.effectiveIncome.toLocaleString())
  console.log('✅ 年支出:', result.totalExpense.toLocaleString())
  console.log('✅ 经济贡献:', result.contribution.toLocaleString())
  console.log('✅ 更新后心理健康:', mockPerson.psyche)
  console.log('✅ 更新后生活压力:', mockPerson.strain)
} catch (error) {
  console.log('❌ 经济计算出错:', error.message)
}

// 测试5：不同地域对比
console.log('\n5. 测试地域差异...')
const regions = ['rural', 'county', 'city', 'mega']
regions.forEach(region => {
  const price = calculateHousePrice(region, 'mid', 1.0)
  console.log(`✅ ${CONFIG_ECONOMY.REGIONS[region].label}: ${price.toLocaleString()}元`)
})

console.log('\n🎉 新经济系统集成测试完成！')

module.exports = { mockGameState, mockPerson }