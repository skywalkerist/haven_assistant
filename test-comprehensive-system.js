// 综合系统测试：地区经济 + 高考链路
const { CONFIG_ECONOMY } = require('./config/economy.js')
const { CONFIG_EDU } = require('./config/edu.js')
const { regionPriceNow, annuityPayment, computeHousingAnnualCost } = require('./systems/housing.js')
const { computePersonalLiving, computeFamilyAnnualExpense } = require('./systems/finance.js')
const { calcGaokaoResult } = require('./systems/gaokao.js')
const { applyEffects } = require('./systems/effects.js')

console.log('🧪 综合系统测试开始')

// 测试1：地区经济配置
console.log('\\n1. 测试地区经济配置...')
Object.keys(CONFIG_ECONOMY.REGIONS).forEach(region => {
  const config = CONFIG_ECONOMY.REGIONS[region]
  console.log(`✅ ${config.name}: 薪资系数${config.salaryMul}, 生活成本${config.livingBase}, 租金基准${config.rentBase}`)
})

// 测试2：房价系列
console.log('\\n2. 测试房价系列...')
const testYears = [0, 3, 6, 9, 11]
testYears.forEach(year => {
  console.log(`第${year}年房价:`)
  Object.keys(CONFIG_ECONOMY.REGIONS).forEach(region => {
    const price = regionPriceNow(region, year)
    console.log(`  ${CONFIG_ECONOMY.REGIONS[region].name}: ${price}万/平`)
  })
})

// 测试3：房贷计算
console.log('\\n3. 测试房贷计算...')
const housePrice = 1200000 // 120万
const mortgage = annuityPayment(housePrice * 0.65, 0.046, 30) // 65%贷款，4.6%利率，30年
console.log(`✅ 120万房子30年房贷年供: ${mortgage.toLocaleString()}元`)

// 测试4：个人生活成本
console.log('\\n4. 测试个人生活成本...')
const testPersons = [
  { name: '正常人', psyche: 50, strain: 50 },
  { name: '压力大', psyche: 40, strain: 80 },
  { name: '心理差', psyche: 30, strain: 60 }
]

testPersons.forEach(person => {
  const costs = {}
  Object.keys(CONFIG_ECONOMY.REGIONS).forEach(region => {
    costs[region] = computePersonalLiving(person, region)
  })
  console.log(`✅ ${person.name}年生活成本:`, costs)
})

// 测试5：高考计算模型
console.log('\\n5. 测试高考计算模型...')
const mockFamily = {
  familyAssets: { housing: { schoolTier: 'good' } }
}

const testStudents = [
  { 
    name: '学霸', 
    intelligence: 85, 
    competitiveness: 80, 
    psyche: 70, 
    strain: 40,
    flags: { mathMedals: 2 }
  },
  { 
    name: '中等生', 
    intelligence: 65, 
    competitiveness: 60, 
    psyche: 50, 
    strain: 60,
    flags: {}
  },
  { 
    name: '问题学生', 
    intelligence: 60, 
    competitiveness: 45, 
    psyche: 40, 
    strain: 80,
    flags: { truancyTimes: 5, gamingHours: 300, highSchoolLove: true }
  }
]

testStudents.forEach(student => {
  const results = []
  // 多次测试看分布
  for (let i = 0; i < 5; i++) {
    const { score, percentile, tier } = calcGaokaoResult(student, mockFamily)
    results.push({ score, percentile, tier })
  }
  console.log(`✅ ${student.name}高考结果样本:`)
  results.forEach((r, i) => {
    console.log(`  第${i+1}次: ${r.score}分 ${r.percentile}% → ${r.tier}`)
  })
})

// 测试6：效果系统集成
console.log('\\n6. 测试效果系统集成...')
const testPerson = {
  name: '测试学生',
  age: 16,
  intelligence: 70,
  competitiveness: 50,
  psyche: 60,
  strain: 40,
  flags: {}
}

const testGame = {
  globalEconomy: 300000,
  showEventResult: (person, event, text, success) => {
    console.log(`  ${success ? '✅' : '❌'} ${event}: ${text}`)
  }
}

// 模拟高中事件选择
const highSchoolEffects = [
  { text: '冲刺班选择', effects: { cash: -36000, competitiveness: +6, strain: +7, psyche: -2 } },
  { text: '竞赛训练', effects: { competitiveness: +3, strain: +3, cash: -3000, flag: { mathMedals: 1 } } },
  { text: '谈恋爱', effects: { psyche: +3, strain: +2, flag: { highSchoolLove: true } } }
]

console.log('模拟高中阶段选择:')
console.log('选择前状态:', { 
  competitiveness: testPerson.competitiveness, 
  psyche: testPerson.psyche, 
  strain: testPerson.strain,
  现金: testGame.globalEconomy 
})

highSchoolEffects.forEach(choice => {
  console.log(`\\n选择: ${choice.text}`)
  applyEffects(choice.effects, testPerson, testGame)
  console.log('选择后状态:', { 
    competitiveness: testPerson.competitiveness, 
    psyche: testPerson.psyche, 
    strain: testPerson.strain,
    现金: testGame.globalEconomy,
    flags: testPerson.flags 
  })
})

// 最终高考测试
console.log('\\n最终高考测试:')
testPerson.age = 18
const finalResult = calcGaokaoResult(testPerson, mockFamily)
console.log(`✅ 综合培养结果: ${finalResult.score}分 → ${finalResult.tier}`)

console.log('\\n🎉 综合系统测试完成！')

// 展示系统总结
console.log('\\n📊 系统特性总结:')
console.log('1. 地区差异化经济模型 - 4个地区层级，不同薪资和生活成本')
console.log('2. 房价历史序列 - 12年房价走势，支持可视化')
console.log('3. 复杂高考模型 - 智力+竞争力+心理+压力+行为+学校质量综合计算')
console.log('4. 高中事件系统 - 13个事件影响高考准备，不简单加减智力')
console.log('5. 年度支出整合 - 住房+生活+心理状态综合支出模型')
console.log('6. 效果统一处理 - 支持概率roll、百分比收入、复杂状态标记')

module.exports = { testPersons, testStudents, testGame }