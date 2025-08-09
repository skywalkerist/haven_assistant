// 就业系统 - 基于现有employment.js的增强版本
import { REGION_SALARY_MULT } from './constants.js'
import { clamp01 } from './util.js'
import { suggestTargetRegion } from './migration.js'

// 使用已有的CAREERS数据（从gameStore引入）
export function generateJobOffers(person, CAREERS) {
  const names = Object.keys(CAREERS).filter(n => {
    const c = CAREERS[n]
    if (c.eduReq === '硕士' && person.education !== '硕士') return false
    if (c.eduReq === '本科' && !String(person.education || '').includes('大学') && person.education !== '硕士') return false
    return true
  })
  
  // 体力活必出 + 专业对口优先 + 随机补齐
  const opts = new Set()
  opts.add('体力活')
  
  if (person.major) {
    const m = names.filter(n => CAREERS[n].majors?.includes(person.major))
    if (m.length) opts.add(m[Math.floor(Math.random() * m.length)])
  }
  
  while (opts.size < 3 && names.length) {
    const n = names[Math.floor(Math.random() * names.length)]
    opts.add(n)
  }
  
  // 为每个岗位附上"工作地域"
  const current = person.region || 'city'
  const ambition = person.ambition ?? 50
  
  const regionFor = (job) => {
    // 体制内更偏向本地；高压高薪更偏向外地大城
    const isSystem = job === '公务员'
    if (isSystem) return current
    // 50% 本地 + 50% 外地建议
    return Math.random()<0.5 ? current : (suggestTargetRegion(current,'job') || current)
  }

  return Array.from(opts).map(job => ({ job, region: regionFor(job) }))
}

export function calcJobSuccess(person, jobName, CAREERS) {
  if (jobName === '体力活') return 0.9
  
  const career = CAREERS[jobName]
  if (!career) return 0.5
  
  let p = 0.50
  
  // 学历层级
  if (person.schoolLevel === '211') p += 0.10
  if (person.schoolLevel === '985') p += 0.20
  if (person.education === '硕士' && career.eduReq !== '硕士') p += 0.08
  
  // 专业匹配
  const match = !career.majors?.length || career.majors.includes(person.major)
  if (!match) p -= 0.15
  
  // 竞争力/心理/压力修正
  p += (person.competitiveness - 50) / 250
  p += (person.psyche - 50) / 300
  p -= Math.max(0, person.strain - 65) / 250
  
  // 野心匹配（销售/创业类喜欢高野心；体制内喜欢低野心）
  const ambition = person.ambition ?? 50
  const systemJobs = ['公务员']
  if (systemJobs.includes(jobName)) p += (50 - ambition) / 300
  const salesy = ['销售代表', '保险顾问']
  if (salesy.includes(jobName)) p += (ambition - 50) / 250
  
  return clamp01(p)
}

export function calcStartingSalary(person, jobName, region, CAREERS) {
  const c = CAREERS[jobName]
  if (!c) return 60000
  
  let base = c.minSalary + Math.random() * (c.maxSalary - c.minSalary) * 0.35 // 入职通常偏下限
  
  if (person.education === '硕士') base += 30000
  
  // 辍学薪酬惩罚
  if (person.education === '初中') base *= 0.5
  else if (person.education === '高中') base /= 1.5
  
  // 区域倍率
  const reg = region || 'city'
  base *= (REGION_SALARY_MULT[reg] || 1)
  
  return Math.round(base)
}