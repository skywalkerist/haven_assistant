// systems/events.js
// ============= 统一事件池（v2.2） =============
// 说明：
// 1) 本文件导出的事件是**唯一来源**。请删除/停用其它散落的旧事件定义。
// 2) 通过 audience/age 精准限制受众，避免“婴儿弹按揭”“幼儿园加智力”之类问题。
// 3) 家庭级事件（如房贷/换房断链/法拍/家庭赡养）只会在**户主**身上触发一次。
// 4) 不再让 K12 事件直接 +intelligence；统一以轻量的 competitiveness/psyche 或标记 flag，
//    最终在升学/求职环节兑现。
// 5) 只导出：EVENT_POOL, EVENT_BASE_PROBABILITIES, applyAdjustments, rand。

/** 随机整数 [a,b] */
export function rand(a,b){ return Math.round(a + Math.random()*(b-a)) }

/** 家庭级事件清单（由调度器识别，只触发一次并绑定户主） */
export const FAMILY_LEVEL = new Set([
  'house_rent_hike','house_hoa_repair','house_chain_break','policy_mortgage_rate'
]);

/** 受众辅助 */
export function fitsAudience(evt, person){
  if (!evt.audience || evt.audience==='any') return true;
  if (evt.audience==='child') return person.age < 18 && !person.occupation;
  if (evt.audience==='adult') return person.age >= 18;
  return true;
}
export function fitsAge(evt, person){
  if (!evt.age) return true;
  const [lo, hi] = evt.age;
  return person.age >= lo && person.age <= hi;
}

/** 概率基础表（被 checkNewEventSystem 读取） */
export const EVENT_BASE_PROBABILITIES = {
  // 大学线
  'uni_slump': 0.12,
  'uni_skip': 0.10,
  'uni_burnout': 0.06,
  'uni_mentor_pua': 0.05,
  'uni_award': 0.08,
  'uni_club': 0.08,
  'uni_breakup': 0.10,

  // 职场线
  'work_headhunt': 0.10,
  'work_perf': 0.12,
  'work_layoff': 0.06,
  'work_offer_conflict': 0.05,
  'work_probation_fail': 0.05,
  'work_micromistake': 0.10,
  'work_small_raise': 0.10,

  // 家庭线
  'fam_quarrel': 0.10,
  'fam_fertility_issue': 0.06,
  'fam_child_sick': 0.08,
  'fam_elder_care': 0.05,
  'fam_family_trip': 0.08,

  // 财务线
  'fin_gift_spike': 0.10,
  'fin_fund_drawdown': 0.08,
  'fin_med_expense': 0.05,
  'fin_traffic_fine': 0.08,
  'fin_fraud_scam': 0.03,

  // 住房&政策（家庭级）
  'house_rent_hike': 0.10,
  'house_hoa_repair': 0.08,
  'house_chain_break': 0.05,
  'policy_mortgage_rate': 0.10,

  // 心理线
  'psy_anxiety': 0.10,
  'psy_depression_risk': 0.05,
  'psy_counselling': 0.08,
  'psy_mindfulness': 0.08,
};

/** 概率修正器（由调度器调用）
 * 返回修正后的概率（0~1）
 */
export function applyAdjustments(id, baseP, person, game, regionType){
  let p = baseP;

  // 区域景气 & 行业影响（粗粒度）
  const econ = game?.worldState?.economicCycle ?? 1.0;
  if (id.startsWith('work_')) {
    p *= (0.9 + (1.1 - 0.9) * econ); // 0.9~1.1
  }

  // 压力/心理影响
  const strain = person.strain ?? 30;
  const psyche = person.psyche ?? 50;
  if (['psy_anxiety','psy_depression_risk'].includes(id)){
    p *= (1 + Math.max(0, strain-60)/120); // 压力越高越容易触发
    p *= (1 + Math.max(0, 50-psyche)/150); // 心理越差越容易触发
  }
  if (id==='fam_quarrel'){
    p *= (1 + Math.max(0, strain-55)/200);
  }

  // 婚育状态
  if (id==='fam_fertility_issue'){
    if (!person.partner) p = 0; // 未婚不触发
  }

  // 住房状态驱动
  const housing = game?.familyAssets?.housing || {};
  if (['house_rent_hike'].includes(id) && housing.mode!=='rent') p = 0;
  if (['house_hoa_repair'].includes(id) && housing.mode!=='own') p = 0;
  if (id==='house_chain_break' && !person.flags?.isSwitchingHouse) p = 0;

  // 职场与状态
  if (id.startsWith('work_') && (!person.occupation || person.isRetired)) p = 0;
  if (id==='work_probation_fail' && (person.workYears||0) > 1) p = 0;

  // 大学线 gate
  const inUni = (person.education?.includes('大学') || person.education==='硕士在读');
  if (id.startsWith('uni_') && !inUni) p = 0;

  // 家庭级事件降低频率：一年最多一次（由调度器限流外，再小幅降低）
  if (FAMILY_LEVEL.has(id)) p *= 0.8;

  // 安全钳位
  p = Math.max(0, Math.min(0.95, p));
  return p;
}

// ============= 统一事件池（只此一处） =============
export const EVENT_POOL = [
  // ===== 大学线（7）=====
  {
    id: "uni_slump", importance: "normal", cooldownYears: 1,
    audience: "adult", age:[18,28],
    when: (p,g)=> (p.education?.includes('大学') || p.education==='硕士在读'),
    ui: "sheet",
    title: "学习低潮", icon: "📉",
    text: "专注力下降，效率变差。",
    choices: [
      { text:"硬拉强度训练", effects:{ strain:+10, psyche:-2, competitiveness:+rand(2,4) } },
      { text:"调整作息",     effects:{ strain:-5,  psyche:+2, competitiveness:+rand(1,2) } },
      { text:"摆烂一周",     effects:{ strain:-8,  psyche:+3, competitiveness:-1 } }
    ]
  },
  {
    id: "uni_skip", importance: "normal", cooldownYears: 1,
    audience: "adult", age:[18,28],
    when: (p,g)=> (p.education?.includes('大学') || p.education==='硕士在读'),
    ui: "sheet",
    title: "逃课诱惑", icon: "🛋️",
    text: "同学邀你划水，今晚联盟开黑。",
    choices: [
      { text:"拒绝并去自习", effects:{ motivation:+3, competitiveness:+2, psyche:-1 } },
      { text:"只玩1小时",    effects:{ psyche:+2, competitiveness:0 } },
      { text:"通宵开黑",      effects:{ competitiveness:-2, strain:+5, psyche:+3 } }
    ]
  },
  {
    id: "uni_burnout", importance: "major", cooldownYears: 2,
    audience: "adult", age:[18,30],
    when: (p,g)=> (p.education?.includes('大学') || p.education==='硕士在读'),
    ui: "modal",
    title: "过劳预警", icon: "⛔",
    text: "长时间高压学习与实习，身体与情绪已报警。",
    choices: [
      { text:"立刻休整一月", effects:{ strain:-15, psyche:+6, competitiveness:-1, cash:-2000 } },
      { text:"咬牙坚持",     effects:{ strain:+10, psyche:-4, competitiveness:+2 } }
    ]
  },
  {
    id: "uni_mentor_pua", importance: "major", cooldownYears: 3,
    audience: "adult", age:[20,30],
    when: (p,g)=> p.education==='硕士在读',
    ui: "modal",
    title: "导师压迫", icon: "🧪",
    text: "导师不合理加压与占用私人时间。",
    choices: [
      { text:"反抗并换课题组", effects:{ strain:-8, psyche:+4, competitiveness:-1 } },
      { text:"隐忍继续",       effects:{ strain:+8, psyche:-5, competitiveness:+2 } }
    ]
  },
  {
    id: "uni_award", importance: "normal", cooldownYears: 1,
    audience: "adult", age:[18,28],
    when: (p,g)=> (p.education?.includes('大学') || p.education==='硕士在读'),
    ui: "sheet",
    title: "竞赛获奖", icon: "🏅",
    text: "在竞赛中表现突出。",
    choices: [
      { text:"全力冲击更高奖项", effects:{ motivation:+3, competitiveness:+3, strain:+4 } },
      { text:"稳住已有成果",     effects:{ competitiveness:+2 } }
    ]
  },
  {
    id: "uni_club", importance: "normal", cooldownYears: 1,
    audience: "adult", age:[18,26],
    when: (p,g)=> (p.education?.includes('大学')),
    ui: "sheet",
    title: "学生干部竞选", icon: "📣",
    text: "同学推荐你竞选组织部长。",
    choices: [
      { text:"参选并拉票", effects:{ competitiveness:+2, charm:+2, strain:+3 } },
      { text:"婉拒专注学业", effects:{ psyche:+1 } }
    ]
  },
  {
    id: "uni_breakup", importance: "normal", cooldownYears: 1,
    audience: "adult", age:[18,30],
    when: (p,g)=> (p.education?.includes('大学') || p.education==='硕士在读') && p.flags?.inRelationship,
    ui: "sheet",
    title: "感情变故", icon: "💔",
    text: "沟通不畅，矛盾升级。",
    choices: [
      { text:"冷静沟通修复", effects:{ psyche:-1, strain:+2, motivation:+1 } },
      { text:"和平分手",     effects:{ psyche:-3, strain:+4, motivation:+2, flag:{inRelationship:false} } }
    ]
  },

  // ===== 职场线（7）=====
  {
    id: "work_headhunt", importance: "normal", cooldownYears: 1,
    audience: "adult", age:[20,65],
    when: (p,g)=> !!p.occupation && !p.isRetired,
    ui: "sheet",
    title: "猎头来电", icon: "📞",
    text: "对方给出看起来不错的岗位。",
    choices: [
      { text:"面谈了解", effects:{ competitiveness:+1, motivation:+1 } },
      { text:"直接婉拒", effects:{ psyche:+1 } }
    ]
  },
  {
    id: "work_perf", importance: "normal", cooldownYears: 1,
    audience: "adult", age:[20,65],
    when: (p,g)=> !!p.occupation && !p.isRetired,
    ui: "sheet",
    title: "绩效谈话", icon: "🗂️",
    text: "经理与你沟通近期表现与目标。",
    choices: [
      { text:"接受挑战", effects:{ motivation:+2, strain:+2 } },
      { text:"争取资源", effects:{ motivation:+1, competitiveness:+1 } }
    ]
  },
  {
    id: "work_layoff", importance: "major", cooldownYears: 3,
    audience: "adult", age:[22,60],
    when: (p,g)=> !!p.occupation && !p.isRetired,
    ui: "modal",
    title: "裁员风波", icon: "⚠️",
    text: "组织优化波及到你的部门。",
    choices: [
      { text:"内部转岗", effects:{ special:'layoffChance' } },
      { text:"N+1离开",  effects:{ unemployed:true, cash:+rand(15000,30000), strain:+8 } }
    ]
  },
  {
    id: "work_offer_conflict", importance: "major", cooldownYears: 2,
    audience: "adult", age:[22,60],
    when: (p,g)=> !!p.occupation && !p.isRetired,
    ui: "modal",
    title: "多Offer冲突", icon: "🧭",
    text: "两份Offer需要快速抉择。",
    choices: [
      { text:"选高薪高压", effects:{ income:+0.12, strain:+8, psyche:-2, motivation:+2 } },
      { text:"选稳定成长", effects:{ income:+0.05, strain:+2, psyche:+2 } }
    ]
  },
  {
    id: "work_probation_fail", importance: "major", cooldownYears: 2,
    audience: "adult", age:[20,35],
    when: (p,g)=> !!p.occupation && !p.isRetired && (p.workYears||0)<=1,
    ui: "modal",
    title: "试用危机", icon: "🧾",
    text: "试用期评估结果不理想。",
    choices: [
      { text:"沟通补救", effects:{ special:'probationTest' } },
      { text:"体面离开", effects:{ unemployed:true, psyche:+1 } }
    ]
  },
  {
    id: "work_micromistake", importance: "normal", cooldownYears: 1,
    audience: "adult", age:[20,65],
    when: (p,g)=> !!p.occupation && !p.isRetired,
    ui: "sheet",
    title: "小失误", icon: "🧯",
    text: "一次低级错误需要你收拾残局。",
    choices: [
      { text:"连夜补锅", effects:{ strain:+4, competitiveness:+1 } },
      { text:"主动复盘", effects:{ stability:+1 } }
    ]
  },
  {
    id: "work_small_raise", importance: "normal", cooldownYears: 1,
    audience: "adult", age:[20,65],
    when: (p,g)=> !!p.occupation && !p.isRetired,
    ui: "sheet",
    title: "微幅调薪", icon: "💸",
    text: "绩效达标获小幅加薪。",
    choices: [
      { text:"心里美滋滋", effects:{ income:+0.03, psyche:+2 } }
    ]
  },

  // ===== 家庭线（5）=====
  {
    id: "fam_quarrel", importance: "normal", cooldownYears: 1,
    audience: "adult", age:[20,70],
    when: (p,g)=> !!p.partner,
    ui: "sheet",
    title: "家庭矛盾", icon: "🗯️",
    text: "家务分工与育儿理念产生分歧。",
    choices: [
      { text:"共同制定分工表", effects:{ psyche:+2, strain:-2, cash:-200 } },
      { text:"冷战几天再说",     effects:{ psyche:-3, strain:+4 } }
    ]
  },
  {
    id: "fam_fertility_issue", importance: "major", cooldownYears: 2,
    audience: "adult", age:[25,40],
    when: (p,g)=> !!p.partner && !p.flags?.hasChild,
    ui: "modal",
    title: "备孕不顺", icon: "🍼",
    text: "尝试一段时间仍未成功。",
    choices: [
      { text:"就医检查", effects:{ cash:-5000, psyche:+2 } },
      { text:"顺其自然", effects:{ psyche:+1, motivation:-1 } }
    ]
  },
  {
    id: "fam_child_sick", importance: "normal", cooldownYears: 1,
    audience: "adult", age:[22,70],
    when: (p,g)=> (p.children||[]).some(c=>c.isAlive),
    ui: "sheet",
    title: "孩子生病", icon: "🤒",
    text: "需要额外照护与花费。",
    choices: [
      { text:"赴三甲医院", effects:{ cash:-2000, strain:+2, psyche:-1 } },
      { text:"社区诊所",   effects:{ cash:-500,  psyche:0 } }
    ]
  },
  {
    id: "fam_elder_care", importance: "major", cooldownYears: 2,
    audience: "adult", age:[30,80],
    when: (p,g)=> g.persons.some(pp=>pp.age>=75 && pp.isAlive),
    ui: "modal",
    title: "赡养压力上升", icon: "🧓",
    text: "老人身体状况下滑，需要固定照护。",
    choices: [
      { text:"请护工",   effects:{ cash:-12000, strain:+2, psyche:+1 } },
      { text:"轮流照料", effects:{ strain:+6, psyche:-1 } }
    ]
  },
  {
    id: "fam_family_trip", importance: "normal", cooldownYears: 1,
    audience: "adult", age:[22,70],
    when: (p,g)=> !!p.partner,
    ui: "sheet",
    title: "家庭旅行", icon: "✈️",
    text: "放松关系，增加亲密。",
    choices: [
      { text:"短途周末", effects:{ cash:-2000, psyche:+3, strain:-2 } },
      { text:"不去了",   effects:{ psyche:-1 } }
    ]
  },

  // ===== 财务线（5）=====
  {
    id: "fin_gift_spike", importance: "normal", cooldownYears: 1,
    audience: "adult", age:[22,80],
    when: (p,g)=> true,
    ui: "sheet",
    title: "人情开支暴增", icon: "🧧",
    text: "连续多场婚丧喜事，需要随礼。",
    choices: [
      { text:"礼到位",   effects:{ cash:-rand(3000,8000), charm:+1 } },
      { text:"量力而行", effects:{ cash:-rand(1000,3000) } }
    ]
  },
  {
    id: "fin_fund_drawdown", importance: "normal", cooldownYears: 1,
    audience: "adult", age:[22,80],
    when: (p,g)=> !!g.flags?.hasFunds,
    ui: "sheet",
    title: "基金回撤", icon: "📉",
    text: "净值下跌，是否调仓？",
    choices: [
      { text:"止损换债基", effects:{ cash:+rand(2000,8000), psyche:+1 } },
      { text:"继续持有",   effects:{ psyche:-1 } }
    ]
  },
  {
    id: "fin_med_expense", importance: "major", cooldownYears: 3,
    audience: "adult", age:[22,85],
    when: (p,g)=> true,
    ui: "modal",
    title: "突发医疗支出", icon: "🏥",
    text: "意外疾病需要住院治疗。",
    choices: [
      { text:"走医保与商保", effects:{ cash:-rand(8000,20000), psyche:-1 } },
      { text:"自费治疗",     effects:{ cash:-rand(20000,60000), psyche:-2 } }
    ]
  },
  {
    id: "fin_traffic_fine", importance: "normal", cooldownYears: 1,
    audience: "adult", age:[22,80],
    when: (p,g)=> true,
    ui: "sheet",
    title: "交通罚单", icon: "🚗",
    text: "违停/超速被罚。",
    choices: [
      { text:"及时缴纳并学习", effects:{ cash:-rand(200,500), motivation:+1 } }
    ]
  },
  {
    id: "fin_fraud_scam", importance: "major", cooldownYears: 3,
    audience: "adult", age:[18,85],
    when: (p,g)=> true,
    ui: "modal",
    title: "电信诈骗", icon: "📵",
    text: "陌生链接与可疑来电频繁。",
    choices: [
      { text:"反诈学习并上报", effects:{ psyche:+2 } },
      { text:"不慎中招",       effects:{ cash:-rand(5000,30000), psyche:-4 } }
    ]
  },

  // ===== 住房&政策（4）（家庭级）=====
  {
    id: "house_rent_hike", importance: "normal", cooldownYears: 1,
    audience: "adult", age:[22,80],
    when: (p,g)=> g.familyAssets?.housing?.mode==='rent',
    ui: "sheet",
    title: "房东涨租", icon: "🏠",
    text: "合同到期，房东提出涨租。",
    choices: [
      { text:"接受续租", effects:{ cash:-rand(2000,6000), strain:+2 } },
      { text:"换房",     effects:{ cash:-rand(3000,8000), strain:+4, flag:{isSwitchingHouse:true} } }
    ]
  },
  {
    id: "house_hoa_repair", importance: "normal", cooldownYears: 1,
    audience: "adult", age:[22,80],
    when: (p,g)=> g.familyAssets?.housing?.mode==='own',
    ui: "sheet",
    title: "小区大修基金", icon: "🧱",
    text: "电梯/外立面维修分摊。",
    choices: [
      { text:"缴纳", effects:{ cash:-rand(3000,12000) } }
    ]
  },
  {
    id: "house_chain_break", importance: "major", cooldownYears: 2,
    audience: "adult", age:[22,80],
    when: (p,g)=> !!g.persons.find(pp=>pp.flags?.isSwitchingHouse),
    ui: "modal",
    title: "换房断链", icon: "⛓️",
    text: "买卖两端不同步，资金链紧张。",
    choices: [
      { text:"短期过桥资金", effects:{ cash:-rand(5000,15000), strain:+4, special:'house_chain_break' } },
      { text:"暂缓交易",     effects:{ psyche:-1, flag:{ isSwitchingHouse:false } } }
    ]
  },
  {
    id: "policy_mortgage_rate", importance: "normal", cooldownYears: 1,
    audience: "adult", age:[22,80],
    when: (p,g)=> g.familyAssets?.housing && g.familyAssets.housing.mode!=='none',
    ui: "sheet",
    title: "利率调整", icon: "📈",
    text: "房贷基准利率微调。",
    choices: [
      { text:"考虑转按揭", effects:{ flag:{considerRefinance:true} } },
      { text:"观望",       effects:{ } }
    ]
  },

  // ===== 心理（4）=====
  {
    id: "psy_anxiety", importance: "normal", cooldownYears: 1,
    audience: "adult", age:[15,85],
    when: (p,g)=> true,
    ui: "sheet",
    title: "焦虑波动", icon: "🌫️",
    text: "入睡困难/心绪不宁。",
    choices: [
      { text:"运动与作息", effects:{ strain:-6, psyche:+3, cash:-300 } },
      { text:"短期逃避",   effects:{ psyche:+1, motivation:-1 } }
    ]
  },
  {
    id: "psy_depression_risk", importance: "major", cooldownYears: 2,
    audience: "adult", age:[15,85],
    when: (p,g)=> true,
    ui: "modal",
    title: "心理健康预警", icon: "🛟",
    text: "长时间高压与低情绪，存在抑郁风险。",
    choices: [
      { text:"就医与心理咨询", effects:{ cash:-2000, psyche:+10, strain:-12 } },
      { text:"暂且观望",       effects:{ psyche:-5 } }
    ]
  },
  {
    id: "psy_counselling", importance: "normal", cooldownYears: 1,
    audience: "adult", age:[15,85],
    when: (p,g)=> true,
    ui: "sheet",
    title: "心理咨询契机", icon: "🧠",
    text: "学校/单位提供团辅经历。",
    choices: [
      { text:"报名参加", effects:{ psyche:+5, strain:-4, cash:-200 } },
      { text:"不参加",   effects:{ psyche:0 } }
    ]
  },
  {
    id: "psy_mindfulness", importance: "normal", cooldownYears: 1,
    audience: "adult", age:[12,85],
    when: (p,g)=> true,
    ui: "sheet",
    title: "正念训练", icon: "🧘",
    text: "尝试冥想/呼吸练习。",
    choices: [
      { text:"坚持21天", effects:{ psyche:+4, strain:-3, motivation:+1 } },
      { text:"浅尝辄止", effects:{ psyche:+1 } }
    ]
  }
];
