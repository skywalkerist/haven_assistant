// 就业系统模块 - 毕业求职生成器
// 岗位池生成 + 成功率/起薪公式 + 申请动作 hook

// 岗位分桶配置
export const JOB_BUCKETS = {
  corpTech: ['软件工程师','网络安全工程师','数据分析师','电气工程师','机械工程师','UI/UX设计师','食品研发工程师','建筑设计师','供应链管理','电商运营','新媒体运营'],
  corpBiz:  ['市场营销经理','人力资源专员','会计师','项目经理','金融分析师','保险顾问','销售代表'],
  gov:      ['公务员'], // 走单独"考公事件"，但也可以作为 offer 展示
  medEdu:   ['医生（临床）','护士','中小学教师','心理咨询师','兽医'],
  fallback: ['体力活'],
}

// 专业到岗位桶的映射提示
export const MAJOR_TO_BUCKET_HINT = {
  '计算机科学与技术':'corpTech','软件工程':'corpTech','统计学':'corpTech','数学':'corpTech','网络安全':'corpTech',
  '市场营销':'corpBiz','工商管理':'corpBiz','会计学':'corpBiz','财务管理':'corpBiz','经济学':'corpBiz','金融学':'corpBiz',
  '临床医学':'medEdu','护理学':'medEdu','师范类':'medEdu','学科相关专业':'medEdu','心理学':'medEdu','应用心理学':'medEdu','动物医学':'medEdu',
  // 其他专业默认走 corpTech 或 corpBiz
}

// 构建个人求职偏好向量
export function buildPreference(person) {
  const gov = Math.min(1, (person.prefGov || 0))
  const corp = Math.min(1, (person.prefCorp || 0))
  const startup = Math.min(1, (person.prefStartup || 0) + (person.ambition || 50) / 200) // 野心提高创业偏好
  
  // 归一化
  const sum = (gov + corp + startup) || 1
  return { 
    gov: gov / sum, 
    corp: corp / sum, 
    startup: startup / sum 
  }
}

// 权重随机选择函数
function weightedPick(pairs, k) {
  const arr = [...pairs]
  const res = []
  for (let i = 0; i < k && arr.length > 0; i++) {
    const sum = arr.reduce((s, [, w]) => s + w, 0) || 1
    let r = Math.random() * sum
    let idx = 0
    for (; idx < arr.length; idx++) {
      r -= arr[idx][1]
      if (r <= 0) break
    }
    const [picked] = arr.splice(Math.max(0, Math.min(idx, arr.length - 1)), 1)[0]
    res.push(picked)
  }
  return res
}

// 根据偏好和专业生成岗位选项 (需要传入CAREERS对象)
export function generateJobOffers(person, regionType, CAREERS) {
  const pref = buildPreference(person)
  const school = person.schoolLevel || '双非'
  const major = person.major || ''
  const hintBucket = MAJOR_TO_BUCKET_HINT[major]

  // 候选桶权重
  let pools = []
  // 企业技术/商务
  pools.push(['corpTech', 0.5 * (pref.corp) + (hintBucket === 'corpTech' ? 0.3 : 0)])
  pools.push(['corpBiz', 0.5 * (pref.corp) + (hintBucket === 'corpBiz' ? 0.3 : 0)])
  // 体制（公务员单独事件，但这里也允许出现"事业单位/教师/医生"）
  pools.push(['medEdu', 0.35 * pref.gov + (hintBucket === 'medEdu' ? 0.25 : 0)])
  // 兜底
  pools.push(['fallback', 0.1])

  // 按权重抽 2~3 个桶，再从桶里随机岗位（满足学历）
  const pickBuckets = weightedPick(pools, 3)
  let offers = []
  
  pickBuckets.forEach(b => {
    const list = JOB_BUCKETS[b]
    const candidates = list.filter(name => {
      const c = CAREERS[name]
      if (!c) return false
      // 学历要求过滤
      if (c.eduReq === '硕士' && person.education !== '硕士') return false
      if (c.eduReq === '本科' && !(person.education?.includes('大学') || person.education === '硕士')) return false
      return true
    })
    
    if (candidates.length > 0) {
      const one = candidates[Math.floor(Math.random() * candidates.length)]
      if (!offers.includes(one)) offers.push(one)
    }
  })
  
  // 永远加一个"体力活"
  if (!offers.includes('体力活')) offers.push('体力活')

  return offers.slice(0, 4)
}

// 计算求职成功率 success rate ∈ [0.05, 0.95]
export function calcJobSuccess(person, jobName, regionType, CAREERS) {
  const c = CAREERS[jobName] || { minSalary: 50000, maxSalary: 100000, majors: [], eduReq: '本科以下' }

  // --- 基础项 ---
  let p = 0.35 // 基础成功率

  // 学历加成
  const sl = person.schoolLevel || '双非'
  if (sl === '985') p += 0.18
  else if (sl === '211') p += 0.12
  else if (sl === '双非') p += 0.06
  else p += 0.02 // 二本

  if (person.education === '硕士') p += 0.08

  // 专业匹配
  const isMatch = (c.majors || []).length === 0 || (c.majors || []).includes(person.major)
  p += isMatch ? 0.06 : -0.10

  // 竞争力（0–100）
  const comp = person.competitiveness || 50
  p += (comp - 50) / 200  // +0.25 at 100, -0.25 at 0

  // 履历层级：实习/科研/干部（加和）
  const internTier = person.flags?.internTier || 0  // 0/1/2 → 0/0.04/0.08
  const researchTier = person.flags?.researchTier || 0
  const leaderTier = person.flags?.leaderTier || 0
  p += internTier * 0.04 + researchTier * 0.03 + leaderTier * 0.02

  // 心理/压力修正
  const psy = person.psyche || 50
  const st = person.strain || 50
  p += (psy - 50) / 250   // 心理好+0.2极限
  if (st > 70) p -= (st - 70) / 150 // 压力过高，-0.2极限

  // 地区竞争度：超一线更卷
  if (regionType === 'mega') p -= 0.06
  else if (regionType === 'city') p -= 0.02
  else if (regionType === 'rural') p += 0.02

  // 体力活特殊
  if (jobName === '体力活') p = 0.9

  // 失败叠加惩罚（可选）
  const fails = person.flags?.jobFailCount || 0
  p -= Math.min(0.1, fails * 0.03)

  return Math.max(0.05, Math.min(0.95, p))
}

// 计算期望起薪
export function calcStartingSalary(person, jobName, regionType, CAREERS) {
  const c = CAREERS[jobName] || { minSalary: 60000, maxSalary: 120000 }
  const range = Math.max(0, c.maxSalary - c.minSalary)

  let q = 0.35
  const sl = person.schoolLevel || '双非'
  if (sl === '985') q += 0.20
  else if (sl === '211') q += 0.12
  else if (sl === '双非') q += 0.05

  if (person.education === '硕士') q += 0.08

  const comp = person.competitiveness || 50
  q += (comp - 50) / 250 // +0.2上限

  const internTier = person.flags?.internTier || 0
  const researchTier = person.flags?.researchTier || 0
  q += internTier * 0.05 + researchTier * 0.03

  // 地区薪资系数微调
  if (regionType === 'mega') q += 0.05
  else if (regionType === 'rural') q -= 0.03

  q = Math.max(0.1, Math.min(0.95, q))
  return Math.round(c.minSalary + range * q)
}

// 计算考公成功率
export function calcCivilExamSuccess(person) {
  let p = 0.06 // 基础6%成功率
  
  // 学历加成
  const sl = person.schoolLevel || '双非'
  if (sl === '985') p += 0.06
  else if (sl === '211') p += 0.04
  else p += 0.02

  // 竞争力影响
  const comp = person.competitiveness || 50
  p += comp / 400 // 最高+0.25

  // 科研和领导经历有助于考公
  const researchTier = person.flags?.researchTier || 0
  const leaderTier = person.flags?.leaderTier || 0
  p += researchTier * 0.02 + leaderTier * 0.03

  return Math.max(0.02, Math.min(0.25, p))
}

// 计算创业成功率
export function calcStartupSuccess(person) {
  const intelligence = person.intelligence || 50
  const comp = person.competitiveness || 50
  const psyche = person.psyche || 50
  const ambition = person.ambition || 50
  
  let p = 0.12 // 基础12%成功率
  
  // 智力和竞争力
  p += (intelligence - 50) / 200
  p += (comp - 50) / 250
  
  // 心理状态
  p += (psyche - 50) / 300
  
  // 野心加成
  if (ambition > 70) p += 0.08
  else if (ambition > 85) p += 0.15
  
  // 实习经历有助于创业
  const internTier = person.flags?.internTier || 0
  p += internTier * 0.03

  return Math.max(0.05, Math.min(0.45, p))
}