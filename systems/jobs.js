import { CONFIG } from './config.js'
import { clamp } from './random.js'

export function decorateCareers(CAREERS) {
  // 为职业补充分类与行业类别（默认），你也可在原 CAREERS 里直接写死
  const cat = (name) => {
    if (/工程师|软件|网络|数据|电气|机械|研发/.test(name)) return 'tech'
    if (/设计|新媒体|UI|艺术/.test(name)) return 'creative'
    if (/销售|市场|公关|顾问/.test(name)) return 'relation'
    if (/公务员|教师|护士|中小学|电商运营|人力资源/.test(name)) return 'stable'
    return 'other'
  }
  Object.keys(CAREERS).forEach(k=>{
    CAREERS[k].category = CAREERS[k].category || cat(k)
    CAREERS[k].cycleCategory = CAREERS[k].cycleCategory || CAREERS[k].category
    CAREERS[k].promotion = CAREERS[k].promotion || { interval: CONFIG.jobs.promo.intervalYears }
  })
}

export function degreeBonus(person){
  let b = 0
  if (person.schoolLevel === '985') b += CONFIG.jobs.degreeBonus['985']
  if (person.schoolLevel === '211') b += CONFIG.jobs.degreeBonus['211']
  if (person.education === '硕士') b += CONFIG.jobs.degreeBonus['硕士']
  return b
}

export function calcPromotionProb(person, jobName, salesLike=false) {
  if (salesLike) {
    const x = (person.intelligence/CONFIG.jobs.salesFormula.intelDiv + person.charm/CONFIG.jobs.salesFormula.charmDiv)
    return clamp(x/100, CONFIG.jobs.promo.probClamp[0], CONFIG.jobs.promo.probClamp[1])
  }
  const x = (person.intelligence/5 + person.charm/3) + degreeBonus(person)*100
  return clamp(x/100, CONFIG.jobs.promo.probClamp[0], CONFIG.jobs.promo.probClamp[1])
}

export function updateSatisfaction(person, careerMatch, stress) {
  // 简化：满意度 = 基础50 + 匹配加成 - 压力惩罚；年末clamp
  const base = person.satisfaction ?? 50
  const delta = (careerMatch ? +5 : -5) - (stress>80 ? 5 : 0)
  person.satisfaction = Math.max(0, Math.min(100, base + delta))
}

export function maybeVoluntaryQuit(person) {
  if (!person.occupation) return false
  if ((person.satisfaction ?? 50) >= CONFIG.jobs.quit.satisfactionThreshold) return false
  if (Math.random() < CONFIG.jobs.quit.annualProb) {
    // 离职：清空工作状态，进入求职
    person.occupation = null
    person.income = 0
    person.jobSeeking = true
    return true
  }
  return false
}