// 事件效果统一解释器
// 负责把事件 choices[*].effects 里的各类字段统一落到 person 和 gameStore 上

// 小工具
const clamp = (x, a, b) => Math.max(a, Math.min(b, x))
const isNum = (v) => typeof v === 'number' && !isNaN(v)
export const rand = (a, b) => Math.round(a + Math.random() * (b - a))

// 简单 sigmoid，用于 roll 成功率
export const sigmoid = (x) => 1 / (1 + Math.exp(-x / 6))

// 将 effects 中的"百分比增减"应用到数值
function applyRatio(base, ratio) {
  // ratio=+0.12 表示 +12%，ratio=-0.05 表示 -5%
  return Math.round(base * (1 + ratio))
}

// 统一入口：把 effects 应用到 person & game
export function applyEffects(effects, person, game) {
  if (!effects) return

  // 1) 处理概率 roll（若存在）——优先
  if (effects.roll) {
    const { p_success, onSuccess, onFail } = effects.roll
    let p = 0
    
    if (typeof p_success === 'string') {
      // 支持具名计算函数
      if (p_success === 'civil_exam') {
        // 考公成功率计算
        const { calcCivilExamSuccess } = require('./employment.js')
        p = calcCivilExamSuccess(person)
      } else if (p_success === 'startup') {
        // 创业成功率计算
        const { calcStartupSuccess } = require('./employment.js')
        p = calcStartupSuccess(person)
      } else {
        // 支持 'sigmoid(HireScore-68)' 这种表达式：从上下文取 HireScore
        const HireScore = computeHireScore(person, game)
        const expr = p_success.replace(/HireScore/g, String(HireScore))
        // 仅支持 sigmoid(x) 形式
        const m = expr.match(/sigmoid\\(([-\\d\\.]+)\\)/)
        p = m ? sigmoid(parseFloat(m[1])) : 0.5
      }
    } else if (isNum(p_success)) {
      p = clamp(p_success, 0.01, 0.99)
    } else {
      p = 0.5
    }
    
    if (Math.random() < p) {
      applyEffects(onSuccess, person, game)
    } else {
      applyEffects(onFail, person, game)
    }
    return // roll 处理完就返回，不再处理其他字段
  }

  // 2) 现金 / 收入
  if (isNum(effects.cash)) {
    game.globalEconomy += effects.cash // 直接改家庭现金
  }
  
  if (isNum(effects.income)) {
    // income 是"比例"还是"绝对"？规则：abs(|x|>1)当作绝对值；-1~+1 之间当作比例
    const v = effects.income
    if (Math.abs(v) < 1 && person.income) {
      person.income = applyRatio(person.income, v)
    } else {
      person.income = Math.max(0, Math.round((person.income || 0) + v))
    }
  }
  
  if (isNum(effects.salary)) { // 同义词
    const v = effects.salary
    if (Math.abs(v) < 1 && person.income) {
      person.income = applyRatio(person.income, v)
    } else {
      person.income = Math.max(0, Math.round((person.income || 0) + v))
    }
  }

  // 3) 属性（统一按 0-100 限幅）
  const bounded = (k, delta) => {
    person[k] = clamp(Math.round((person[k] || 50) + delta), 0, 100)
  }
  
  const attributes = [
    'health', 'charm', 'intelligence',
    'stability', 'motivation', 'creativity',
    'psyche', 'strain', 'competitiveness'
  ]
  
  attributes.forEach(k => {
    if (isNum(effects[k])) bounded(k, effects[k])
  })

  // 4) 状态位 / 标记
  if (effects.flag) {
    person.flags = person.flags || {}
    Object.keys(effects.flag).forEach(k => {
      person.flags[k] = effects.flag[k]
    })
  }
  
  if (effects.keepJob !== undefined) { // 语义糖
    if (effects.keepJob === false) {
      person.occupation = null
      person.income = 0
      person.jobSeeking = true
    }
  }
  
  if (effects.unemployed) {
    person.occupation = null
    person.jobSeeking = true
    person.income = 0
    person.workYears = 0
  }

  // 5) 住房相关（若你定义在 game.familyAssets.housing）
  if (effects.housing) {
    game.familyAssets = game.familyAssets || {}
    game.familyAssets.housing = { ...(game.familyAssets.housing || {}), ...effects.housing }
  }

  // 6) 特殊处理字段
  if (effects.special) {
    handleSpecialEffects(effects.special, person, game)
  }
}

// 特殊效果处理
function handleSpecialEffects(special, person, game) {
  switch (special) {
    case 'layoffChance':
      // 裁员风险：基于竞争力判断
      const keepJobRate = Math.min(0.8, (person.competitiveness || 50) / 100 * 0.6 + 0.2)
      if (Math.random() < keepJobRate) {
        // 成功保住工作但薪资下降
        person.income = Math.round((person.income || 0) * 0.95)
        showEventResult(game, person, '内部转岗', 
          `🎯 成功转岗避免裁员！\\n💼 保住工作但薪资略降5%\\n💪 危机中展现韧性`, true)
      } else {
        // 被裁员
        person.occupation = null
        person.income = 0
        person.jobSeeking = true
        person.workYears = 0
        person.strain = Math.min(100, (person.strain || 0) + 12)
        showEventResult(game, person, '裁员', 
          `😢 不幸被裁员\\n💔 失去工作和收入\\n🔍 需要重新找工作\\n📈 压力大幅上升`, false)
      }
      break
      
    case 'probationTest':
      // 试用期测试：基于能力判断
      const passRate = Math.min(0.8, (person.competitiveness || 0) / 100 + (person.motivation || 0) / 150)
      if (Math.random() < passRate) {
        showEventResult(game, person, '试用期转正', 
          `✅ 成功通过试用期！\\n🎉 正式转正\\n📈 工作稳定性提升`, true)
      } else {
        person.occupation = null
        person.income = 0
        person.jobSeeking = true
        person.psyche = Math.max(0, (person.psyche || 50) - 8)
        showEventResult(game, person, '试用期失败', 
          `😞 试用期未能转正\\n💼 需要重新找工作\\n😔 心理健康受挫`, false)
      }
      break
  }
}

// 一个示例打分，用于试用/转岗成功率
function computeHireScore(person, game) {
  const base = 50
  const comp = (person.competitiveness || 50) * 0.5
  const moti = (person.motivation || 50) * 0.2
  const psy = (person.psyche || 50) * 0.15
  const strn = (person.strain || 50) * -0.15
  return Math.round(base + comp + moti + psy + strn)
}

// 显示事件结果的辅助函数
function showEventResult(game, person, eventName, resultText, isSuccess = true) {
  // 使用游戏存储的方法显示事件结果
  if (game.showEventResult) {
    game.showEventResult(person, eventName, resultText, isSuccess)
  } else {
    // 降级处理
    console.log(`${isSuccess ? '✅' : '❌'} ${eventName}: ${resultText}`)
  }
}