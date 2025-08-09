// 效果系统测试
const { applyEffects, rand, sigmoid } = require('./systems/effects.js')

// 模拟游戏状态
const mockGameState = {
  globalEconomy: 500000,
  familyAssets: { housing: { mode: 'rent' } },
  showEventResult: (person, eventName, text, success) => {
    console.log(`${success ? '✅' : '❌'} ${eventName}: ${text}`)
  }
}

// 模拟人物
const mockPerson = {
  id: 'test1',
  name: '测试人物',
  age: 25,
  intelligence: 75,
  charm: 60,
  stability: 70,
  motivation: 65,
  psyche: 50,
  strain: 40,
  competitiveness: 60,
  income: 150000,
  occupation: '软件工程师',
  flags: {}
}

console.log('🧪 效果系统测试开始')

// 测试1：基本属性修改
console.log('\\n1. 测试基本属性修改...')
const originalHealth = mockPerson.health || 50
const effects1 = { health: 10, charm: -5, cash: 5000 }

console.log('修改前:', { health: originalHealth, charm: mockPerson.charm, 现金: mockGameState.globalEconomy })
applyEffects(effects1, mockPerson, mockGameState)
console.log('修改后:', { health: mockPerson.health, charm: mockPerson.charm, 现金: mockGameState.globalEconomy })

// 测试2：收入修改（百分比和绝对值）
console.log('\\n2. 测试收入修改...')
console.log('原收入:', mockPerson.income)

// 百分比增长
applyEffects({ income: 0.1 }, mockPerson, mockGameState) // +10%
console.log('百分比增长后:', mockPerson.income)

// 绝对值增长
applyEffects({ income: 5000 }, mockPerson, mockGameState) // +5000元
console.log('绝对值增长后:', mockPerson.income)

// 测试3：Roll系统
console.log('\\n3. 测试概率Roll系统...')
const rollEffects = {
  roll: {
    p_success: 0.7, // 70%成功率
    onSuccess: { 
      psyche: 5, 
      cash: 10000 
    },
    onFail: { 
      strain: 8, 
      cash: -2000 
    }
  }
}

for (let i = 0; i < 5; i++) {
  const beforePsyche = mockPerson.psyche
  const beforeStrain = mockPerson.strain
  const beforeCash = mockGameState.globalEconomy
  
  applyEffects(rollEffects, mockPerson, mockGameState)
  
  const psycheChange = mockPerson.psyche - beforePsyche
  const strainChange = mockPerson.strain - beforeStrain
  const cashChange = mockGameState.globalEconomy - beforeCash
  
  if (psycheChange > 0) {
    console.log(`第${i+1}次: 成功! 心理+${psycheChange}, 现金+${cashChange}`)
  } else {
    console.log(`第${i+1}次: 失败! 压力+${strainChange}, 现金${cashChange}`)
  }
}

// 测试4：状态标记
console.log('\\n4. 测试状态标记...')
const flagEffects = {
  flag: { testFlag: true, customValue: 'test' },
  unemployed: false // 测试不失业
}

console.log('标记前:', mockPerson.flags)
applyEffects(flagEffects, mockPerson, mockGameState)
console.log('标记后:', mockPerson.flags)

// 测试5：特殊效果
console.log('\\n5. 测试特殊效果...')
const specialEffects = { special: 'layoffChance' }
const beforeJob = mockPerson.occupation

applyEffects(specialEffects, mockPerson, mockGameState)
console.log(`职业变化: ${beforeJob} -> ${mockPerson.occupation || '无'}`)

// 测试6：工具函数
console.log('\\n6. 测试工具函数...')
console.log('随机数(10-20):', [rand(10,20), rand(10,20), rand(10,20)])
console.log('sigmoid测试:', [
  sigmoid(-12), // 接近0
  sigmoid(0),   // 0.5
  sigmoid(12)   // 接近1
].map(v => v.toFixed(3)))

console.log('\\n🎉 效果系统测试完成！')

// 显示最终状态
console.log('\\n📊 最终人物状态:')
console.log('收入:', mockPerson.income?.toLocaleString(), '元')
console.log('心理健康:', mockPerson.psyche)
console.log('生活压力:', mockPerson.strain)
console.log('职业:', mockPerson.occupation || '无')
console.log('家庭现金:', mockGameState.globalEconomy?.toLocaleString(), '元')

module.exports = { mockPerson, mockGameState }