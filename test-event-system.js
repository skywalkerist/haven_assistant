// 新事件系统 v2.0 集成测试
const { applyAdjustments, EVENT_POOL, EVENT_BASE_PROBABILITIES } = require('./systems/events.js')

// 模拟人物数据
const mockPerson = {
  age: 25,
  intelligence: 75,
  charm: 60,
  stability: 70,
  motivation: 65,
  occupation: '软件工程师',
  competitiveness: 75,
  psyche: 50,
  strain: 40,
  education: '985大学',
  flags: {}
}

// 模拟游戏状态
const mockGameState = {
  persons: [mockPerson],
  familyAssets: { housing: { mode: 'rent', schoolTier: 'mid' } },
  worldState: { regionType: 'city', useNewEconomics: true },
  globalEconomy: 500000
}

console.log('🧪 新事件系统 v2.0 集成测试开始')

// 测试1：概率修正函数
console.log('1. 测试概率修正函数...')
const baseProb = 0.1
const adjustedProb = applyAdjustments('work_headhunt', baseProb, mockPerson, mockGameState, 'city')
console.log('✅ 猎头事件基础概率:', baseProb)
console.log('✅ 修正后概率:', adjustedProb.toFixed(4))

// 测试2：事件池加载
console.log('\n2. 测试事件池加载...')
console.log('✅ 事件总数:', EVENT_POOL.length)
const majorEvents = EVENT_POOL.filter(e => e.importance === 'major')
const normalEvents = EVENT_POOL.filter(e => e.importance === 'normal')
console.log('✅ 重要事件数:', majorEvents.length)
console.log('✅ 普通事件数:', normalEvents.length)

// 测试3：事件触发条件检查
console.log('\n3. 测试事件触发条件...')
let triggeredEvents = 0
EVENT_POOL.forEach(event => {
  if (event.when(mockPerson, mockGameState)) {
    triggeredEvents++
    if (triggeredEvents <= 5) { // 只显示前5个
      console.log(`✅ 可触发事件: ${event.title} (${event.importance})`)
    }
  }
})
console.log(`✅ 总可触发事件数: ${triggeredEvents}`)

// 测试4：基础概率配置
console.log('\n4. 测试基础概率配置...')
const probKeys = Object.keys(EVENT_BASE_PROBABILITIES)
console.log('✅ 配置概率的事件数:', probKeys.length)
console.log('✅ 平均基础概率:', (Object.values(EVENT_BASE_PROBABILITIES).reduce((a,b) => a+b, 0) / probKeys.length).toFixed(4))

// 测试5：不同地域概率差异
console.log('\n5. 测试地域概率差异...')
const regions = ['rural', 'county', 'city', 'mega']
regions.forEach(region => {
  const prob = applyAdjustments('house_rent_hike', 0.1, mockPerson, mockGameState, region)
  console.log(`✅ ${region}地区房租上涨概率:`, prob.toFixed(4))
})

console.log('\n🎉 新事件系统 v2.0 集成测试完成！')

module.exports = { mockPerson, mockGameState }