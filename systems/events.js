// ========================= systems/events.js =========================
// 唯一事件源：所有随机/脚本化事件集中在这里
// 约定：
// - 每个事件：{ id, importance: 'major'|'normal', cooldownYears, ui:'modal', icon, title, text, when(p,g):bool, choices:[{text,effects,meta?,special?}] }
// - 效果不直接改 UI，由 gameStore 的 applyNewEventEffects 统一落地（保持解耦）

export const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v))
export const rand = (a,b)=> Math.round(a + Math.random()*(b-a))

// —— 家庭户主选择器（家庭级事件统一由户主承载弹窗）
export function getHouseholdHead(game){
  const alive = (game?.persons||[]).filter(p=>p.isAlive)
  if (alive.length===0) return null
  const adults = alive.filter(p=>p.age>=18)
  const pick = (arr)=> arr.sort((a,b)=> b.age - a.age)[0]
  return adults.length? pick(adults) : pick(alive)
}

// —— 概率基础表（可按需继续补充）
export const EVENT_BASE_PROBABILITIES = {
  // 大学线
  uni_slump: 0.25,
  uni_skip: 0.25,
  uni_burnout: 0.15,
  uni_award: 0.12,
  uni_club: 0.10,
  // 职场线
  work_headhunt: 0.18,
  work_perf: 0.25,
  work_layoff: 0.08,
  work_offer_conflict: 0.1,
  work_probation_fail: 0.12,
  work_micromistake: 0.25,
  work_small_raise: 0.22,
  // 家庭线
  fam_quarrel: 0.22,
  fam_fertility_issue: 0.10,
  fam_child_sick: 0.18,
  fam_elder_care: 0.10,
  fam_family_trip: 0.16,
  // 财务线
  fin_gift_spike: 0.20,
  fin_fund_drawdown: 0.15,
  fin_med_expense: 0.06,
  fin_traffic_fine: 0.15,
  fin_fraud_scam: 0.04,
  // 住房&政策
  house_rent_hike: 0.15,
  house_hoa_repair: 0.12,
  house_chain_break: 0.10,
  policy_mortgage_rate: 0.12,
  // 心理
  psy_anxiety: 0.22,
  psy_depression_risk: 0.08,
  psy_counselling: 0.18,
  psy_mindfulness: 0.18,
  // 迁移/住房决策（由调度器插入，基础值给个兜底）
  migrate_cost_pressure: 0.10,
  migrate_elder_return: 0.12,
  housing_upgrade: 0.10,
}

// —— 概率修正器：按地域、状态、属性微调（保持轻量，避免过度耦合）
export function applyAdjustments(id, base, p, g, regionType){
  let k = base
  // 压力对心理类事件提升概率
  if(/^psy_/.test(id)){
    const s = clamp((p.strain||0),0,100)
    k *= 1 + (s-50)/200 // strain 80 → +15%
  }
  // 职场波动：行业周期/年龄段
  if(/^work_/.test(id)){
    const ageK = (p.age>=22 && p.age<=35)? 1.15 : 1
    k *= ageK
  }
  // 家庭：有伴侣/有子女
  if(/^fam_/.test(id)){
    if(!p.partner) k *= 0.6
    if((p.children||[]).length>0) k *= 1.15
  }
  // 住房：仅在对应模式下生效
  if(id==='house_rent_hike' && g?.familyAssets?.housing?.mode!=='rent') k = 0
  if(id==='house_hoa_repair' && g?.familyAssets?.housing?.mode!=='own') k = 0
  // 地域对财务礼金开支
  if(id==='fin_gift_spike'){
    const map = { rural:0.9, county:1.0, city:1.05, mega:1.1 }
    k *= (map[regionType]||1)
  }
  // 上限/下限
  return clamp(k, 0, 0.95)
}

// —— 事件池（去除了“幼儿园/早教直接+智力”的旧逻辑，统一到竞争力/心理/压力）
export const EVENT_POOL = [
  // ===== 大学线 =====
  {
    id: 'uni_slump', importance:'normal', cooldownYears:1, ui:'modal', icon:'📉',
    title:'学习低潮',
    text:'专注力下降，效率变差。',
    when:(p)=> (p.education?.includes('大学')||p.education==='硕士在读') && p.age>=18,
    choices:[
      { text:'硬拉强度训练', effects:{ strain:+10, psyche:-2, competitiveness:+rand(2,4) } },
      { text:'调整作息',     effects:{ strain:-5,  psyche:+2, competitiveness:+rand(1,2) } },
      { text:'摆烂一周',     effects:{ strain:-8,  psyche:+3, competitiveness:-1 } }
    ]
  },
  { id:'uni_skip', importance:'normal', cooldownYears:1, ui:'modal', icon:'🛋️', title:'逃课诱惑',
    text:'同学邀你划水，今晚联盟开黑。',
    when:(p)=> (p.education?.includes('大学')||p.education==='硕士在读') && p.age>=18,
    choices:[
      { text:'拒绝并去自习', effects:{ motivation:+3, competitiveness:+2, psyche:-1 } },
      { text:'只玩1小时',    effects:{ psyche:+2 } },
      { text:'通宵开黑',      effects:{ competitiveness:-2, strain:+5, psyche:+3 } }
    ]
  },
  { id:'uni_burnout', importance:'major', cooldownYears:2, ui:'modal', icon:'⛔', title:'过劳预警',
    text:'长时间高压学习与实习，身体与情绪已报警。',
    when:(p)=> (p.education?.includes('大学')||p.education==='硕士在读') && p.age>=18,
    choices:[
      { text:'立刻休整一月', effects:{ strain:-15, psyche:+6, competitiveness:-1, cash:-2000 } },
      { text:'咬牙坚持',     effects:{ strain:+10, psyche:-4, competitiveness:+2 } }
    ]
  },
  { id:'uni_award', importance:'normal', cooldownYears:1, ui:'modal', icon:'🏅', title:'竞赛获奖',
    text:'在竞赛中表现突出。',
    when:(p)=> (p.education?.includes('大学')||p.education==='硕士在读') && p.age>=18,
    choices:[
      { text:'全力冲击更高奖项', effects:{ motivation:+3, competitiveness:+3, strain:+4 } },
      { text:'稳住已有成果',     effects:{ competitiveness:+2 } }
    ]
  },
  { id:'uni_club', importance:'normal', cooldownYears:1, ui:'modal', icon:'📣', title:'学生干部竞选',
    text:'同学推荐你竞选组织部长。',
    when:(p)=> p.education?.includes('大学'),
    choices:[
      { text:'参选并拉票', effects:{ competitiveness:+2, charm:+2, strain:+3 } },
      { text:'婉拒专注学业', effects:{ psyche:+1 } }
    ]
  },

  // ===== 职场线 =====
  { id:'work_headhunt', importance:'normal', cooldownYears:1, ui:'modal', icon:'📞', title:'猎头来电',
    text:'对方给出看起来不错的岗位。', when:(p)=> !!p.occupation && !p.isRetired,
    choices:[ { text:'面谈了解', effects:{ competitiveness:+1, motivation:+1 } }, { text:'直接婉拒', effects:{ psyche:+1 } } ] },
  { id:'work_perf', importance:'normal', cooldownYears:1, ui:'modal', icon:'🗂️', title:'绩效谈话',
    text:'经理与你沟通近期表现与目标。', when:(p)=> !!p.occupation && !p.isRetired,
    choices:[ { text:'接受挑战', effects:{ motivation:+2, strain:+2 } }, { text:'争取资源', effects:{ motivation:+1, competitiveness:+1 } } ] },
  { id:'work_layoff', importance:'major', cooldownYears:3, ui:'modal', icon:'⚠️', title:'裁员风波',
    text:'组织优化波及到你的部门。', when:(p)=> !!p.occupation && !p.isRetired,
    choices:[
      { text:'内部转岗', effects:{ special:'layoffChance' } },
      { text:'N+1离开',  effects:{ unemployed:true, cash:+rand(15000,30000), strain:+8 } }
    ]
  },
  { id:'work_offer_conflict', importance:'major', cooldownYears:2, ui:'modal', icon:'🧭', title:'多Offer冲突',
    text:'两份Offer需要快速抉择。', when:(p)=> !!p.occupation && !p.isRetired,
    choices:[ { text:'选高薪高压', effects:{ income:+0.12, strain:+8, psyche:-2, motivation:+2 } }, { text:'选稳定成长', effects:{ income:+0.05, strain:+2, psyche:+2 } } ] },
  { id:'work_probation_fail', importance:'major', cooldownYears:2, ui:'modal', icon:'🧾', title:'试用危机',
    text:'试用期评估结果不理想。', when:(p)=> !!p.occupation && !p.isRetired && p.workYears<=1,
    choices:[ { text:'沟通补救', effects:{ special:'probationTest' } }, { text:'体面离开', effects:{ unemployed:true, psyche:+1 } } ] },
  { id:'work_micromistake', importance:'normal', cooldownYears:1, ui:'modal', icon:'🧯', title:'小失误',
    text:'一次低级错误需要你收拾残局。', when:(p)=> !!p.occupation && !p.isRetired,
    choices:[ { text:'连夜补锅', effects:{ strain:+4, competitiveness:+1 } }, { text:'主动复盘', effects:{ tenacity:+2 } } ] },
  { id:'work_small_raise', importance:'normal', cooldownYears:1, ui:'modal', icon:'💸', title:'微幅调薪',
    text:'绩效达标获小幅加薪。', when:(p)=> !!p.occupation && !p.isRetired,
    choices:[ { text:'心里美滋滋', effects:{ income:+0.03, psyche:+2 } } ] },

  // ===== 家庭线 =====
  { id:'fam_quarrel', importance:'normal', cooldownYears:1, ui:'modal', icon:'🗯️', title:'家庭矛盾',
    text:'家务分工与育儿理念产生分歧。', when:(p)=> !!p.partner,
    choices:[ { text:'共同制定分工表', effects:{ psyche:+2, strain:-2, cash:-200 } }, { text:'冷战几天再说', effects:{ psyche:-3, strain:+4 } } ] },
  { id:'fam_fertility_issue', importance:'major', cooldownYears:2, ui:'modal', icon:'🍼', title:'备孕不顺',
    text:'尝试一段时间仍未成功。', when:(p)=> !!p.partner && !p.flags?.hasChild && p.age>=25,
    choices:[ { text:'就医检查', effects:{ cash:-5000, psyche:+2 } }, { text:'顺其自然', effects:{ psyche:+1, motivation:-1 } } ] },
  { id:'fam_child_sick', importance:'normal', cooldownYears:1, ui:'modal', icon:'🤒', title:'孩子生病',
    text:'需要额外照护与花费。', when:(p,g)=> (p.children||[]).some(c=>c.isAlive),
    choices:[ { text:'赴三甲医院', effects:{ cash:-2000, strain:+2, psyche:-1 } }, { text:'社区诊所', effects:{ cash:-500, psyche:0 } } ] },
  { id:'fam_elder_care', importance:'major', cooldownYears:2, ui:'modal', icon:'🧓', title:'赡养压力上升',
    text:'老人身体状况下滑，需要固定照护。', when:(p,g)=> g.persons.some(pp=>pp.age>=75 && pp.isAlive),
    choices:[ { text:'请护工', effects:{ cash:-12000, strain:+2, psyche:+1 } }, { text:'轮流照料', effects:{ strain:+6, psyche:-1 } } ] },
  { id:'fam_family_trip', importance:'normal', cooldownYears:1, ui:'modal', icon:'✈️', title:'家庭旅行',
    text:'放松关系，增加亲密。', when:(p)=> !!p.partner,
    choices:[ { text:'短途周末', effects:{ cash:-2000, psyche:+3, strain:-2 } }, { text:'不去了', effects:{ psyche:-1 } } ] },

  // ===== 财务线 =====
  { id:'fin_gift_spike', importance:'normal', cooldownYears:1, ui:'modal', icon:'🧧', title:'人情开支暴增',
    text:'连续多场婚丧喜事，需要随礼。', when:()=> true,
    choices:[ { text:'礼到位', effects:{ cash:-rand(3000,8000), charm:+1 } }, { text:'量力而行', effects:{ cash:-rand(1000,3000) } } ] },
  { id:'fin_fund_drawdown', importance:'normal', cooldownYears:1, ui:'modal', icon:'📉', title:'基金回撤',
    text:'净值下跌，是否调仓？', when:(p,g)=> !!g.flags?.hasFunds,
    choices:[ { text:'止损换债基', effects:{ cash:+rand(2000,8000), psyche:+1 } }, { text:'继续持有', effects:{ psyche:-1 } } ] },
  { id:'fin_med_expense', importance:'major', cooldownYears:3, ui:'modal', icon:'🏥', title:'突发医疗支出',
    text:'意外疾病需要住院治疗。', when:()=> true,
    choices:[ { text:'走医保与商保', effects:{ cash:-rand(8000,20000), psyche:-1 } }, { text:'自费治疗', effects:{ cash:-rand(20000,60000), psyche:-2 } } ] },
  { id:'fin_traffic_fine', importance:'normal', cooldownYears:1, ui:'modal', icon:'🚗', title:'交通罚单',
    text:'违停/超速被罚。', when:()=> true,
    choices:[ { text:'及时缴纳并学习', effects:{ cash:-rand(200,500), motivation:+1 } } ] },
  { id:'fin_fraud_scam', importance:'major', cooldownYears:3, ui:'modal', icon:'📵', title:'电信诈骗',
    text:'陌生链接与可疑来电频繁。', when:()=> true,
    choices:[ { text:'反诈学习并上报', effects:{ psyche:+2 } }, { text:'不慎中招', effects:{ cash:-rand(5000,30000), psyche:-4 } } ] },

  // ===== 住房&政策 =====
  { id:'house_rent_hike', importance:'normal', cooldownYears:1, ui:'modal', icon:'🏠', title:'房东涨租',
    text:'合同到期，房东提出涨租。', when:(p,g)=> g.familyAssets?.housing?.mode==='rent' && p.age>=18,
    choices:[ { text:'接受续租', effects:{ cash:-rand(2000,6000), strain:+2 } }, { text:'换房', effects:{ cash:-rand(3000,8000), strain:+4, flag:{isSwitchingHouse:true} } } ] },
  { id:'house_hoa_repair', importance:'normal', cooldownYears:1, ui:'modal', icon:'🧱', title:'小区大修基金',
    text:'电梯/外立面维修分摊。', when:(p,g)=> g.familyAssets?.housing?.mode==='own' && p.age>=18,
    choices:[ { text:'缴纳', effects:{ cash:-rand(3000,12000) } } ] },
  { id:'house_chain_break', importance:'major', cooldownYears:2, ui:'modal', icon:'⛓️', title:'换房断链',
    text:'买卖两端不同步，资金链紧张。', when:(p)=> !!p.flags?.isSwitchingHouse && p.age>=18,
    choices:[ { text:'短期过桥资金', effects:{ cash:-rand(5000,15000), strain:+4 } }, { text:'暂缓交易', effects:{ psyche:-1 } } ] },
  { id:'policy_mortgage_rate', importance:'normal', cooldownYears:1, ui:'modal', icon:'📈', title:'利率调整',
    text:'房贷基准利率微调。', when:()=> true,
    choices:[ { text:'考虑转按揭', effects:{ flag:{considerRefinance:true}, psyche:+1 } }, { text:'观望', effects:{ psyche:0 } } ] },

  // ===== 心理 =====
  { id:'psy_anxiety', importance:'normal', cooldownYears:1, ui:'modal', icon:'🌫️', title:'焦虑波动',
    text:'入睡困难/心绪不宁。', when:()=> true,
    choices:[ { text:'运动与作息', effects:{ strain:-6, psyche:+3, cash:-300 } }, { text:'短期逃避', effects:{ psyche:+1, motivation:-1 } } ] },
  { id:'psy_depression_risk', importance:'major', cooldownYears:2, ui:'modal', icon:'🛟', title:'心理健康预警',
    text:'长时间高压与低情绪，存在抑郁风险。', when:()=> true,
    choices:[ { text:'就医与心理咨询', effects:{ cash:-2000, psyche:+10, strain:-12 } }, { text:'暂且观望', effects:{ psyche:-5 } } ] },
  { id:'psy_counselling', importance:'normal', cooldownYears:1, ui:'modal', icon:'🧠', title:'心理咨询契机',
    text:'学校/单位提供团辅经历。', when:()=> true,
    choices:[ { text:'报名参加', effects:{ psyche:+5, strain:-4, cash:-200 } }, { text:'不参加', effects:{ psyche:0 } } ] },
  { id:'psy_mindfulness', importance:'normal', cooldownYears:1, ui:'modal', icon:'🧘', title:'正念训练',
    text:'尝试冥想/呼吸练习。', when:()=> true,
    choices:[ { text:'坚持21天', effects:{ psyche:+4, strain:-3, motivation:+1 } }, { text:'浅尝辄止', effects:{ psyche:+1 } } ] },
]