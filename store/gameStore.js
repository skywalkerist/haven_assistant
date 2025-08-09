import { reactive, computed } from 'vue'

// 新增系统模块引入
import { CONFIG } from '../systems/config.js'
import { applyStudyStress, annualStressRecovery, maybeBurnout } from '../systems/stress.js'
import { calcGaokaoScore, bandByScore } from '../systems/education.js'
import { calcGaokaoResult } from '../systems/gaokao.js'
import { initIndustry, tickIndustry, getMultiplier } from '../systems/industry.js'
import { decorateCareers, calcPromotionProb, updateSatisfaction, maybeVoluntaryQuit } from '../systems/jobs.js'
// 经济系统引入
import { computeAnnualEconomics, nextHousePrice, getRandomCity, calculateHousePrice } from '../systems/economy.js'
// 新住房事件引入
// 住房事件系统暂未使用
// import { MarriageHousingEvent, RelocateCityEvent, SchoolTierAdjustEvent, InvestmentHousingEvent, HousingEventHelpers } from '../systems/housing-events.js'
// 新事件系统 v2.0 引入
import { applyAdjustments, EVENT_POOL, EVENT_BASE_PROBABILITIES, rand, FAMILY_LEVEL, fitsAudience, fitsAge } from '../systems/events.js'
// 新财务与住房系统引入
import { computeFamilyAnnualExpense } from '../systems/finance.js'
import { CONFIG_ECONOMY as CFG } from '../config/economy.js'
// 财务工具引入
import { annuityPayment } from '../src/sim/utils/finance.js'
// 就业系统引入（仅保留新版本）
import { generateJobOffers as generateJobOffersNew, calcJobSuccess as calcJobSuccessNew, calcStartingSalary as calcStartingSalaryNew } from '../src/sim/employment.js'
// 住房系统引入
import { setupRent, buyHouse, payHousingForYear } from '../src/sim/housing.js'
// 常量引入
import { 
  COLLEGE_COST_BY_BAND, 
  COLLEGE_COMP_BONUS, 
  COLLEGE_PSY_BONUS,
  REGION_UNIT_PRICE,
  REGION_RENT_BASE,
  SCHOOL_ZONE_PREMIUM,
  DOWNPAY_DEFAULT,
  MORTGAGE_YEARS,
  MORTALITY,
  FUNERAL_COST,
  PENSION
} from '../src/sim/constants.js'
// 迁移系统引入
import { suggestTargetRegion, randomCityName, proposeFamilyMove, applyFamilyMove } from '../src/sim/migration.js'
// 工具函数已通过 events.js 导入

// 专业列表数据
const MAJORS = [
  '计算机科学与技术', '软件工程', '临床医学', '师范类', '学科相关专业', '会计学', 
  '财务管理', '市场营销', '工商管理', '土木工程', '建筑学', '人力资源管理', 
  '心理学', '视觉传达设计', '数字媒体艺术', '电气工程及其自动化', '护理学', 
  '新闻传播', '网络与新媒体', '机械设计制造及其自动化', '电子商务', '法学', 
  '工程管理', '交互设计', '工业设计', '统计学', '数学', '网络安全', '金融学', 
  '经济学', '应用心理学', '城乡规划', '物流管理', '供应链管理', '航空服务', 
  '旅游管理', '食品科学与工程', '生物技术', '动物医学', '体育教育', '运动康复', 
  '环境工程', '能源经济'
]

// 职业数据
const CAREERS = {
  '软件工程师': {
    minSalary: 150000, maxSalary: 400000,
    majors: ['计算机科学与技术', '软件工程'],
    eduReq: '本科'
  },
  '医生（临床）': {
    minSalary: 200000, maxSalary: 500000,
    majors: ['临床医学'],
    eduReq: '硕士'
  },
  '中小学教师': {
    minSalary: 80000, maxSalary: 250000,
    majors: ['师范类', '学科相关专业'],
    eduReq: '本科'
  },
  '会计师': {
    minSalary: 100000, maxSalary: 300000,
    majors: ['会计学', '财务管理'],
    eduReq: '本科'
  },
  '市场营销经理': {
    minSalary: 120000, maxSalary: 350000,
    majors: ['市场营销', '工商管理'],
    eduReq: '本科'
  },
  '土木工程师': {
    minSalary: 100000, maxSalary: 250000,
    majors: ['土木工程', '建筑学'],
    eduReq: '本科'
  },
  '人力资源专员': {
    minSalary: 80000, maxSalary: 200000,
    majors: ['人力资源管理', '心理学'],
    eduReq: '本科'
  },
  '平面设计师': {
    minSalary: 80000, maxSalary: 180000,
    majors: ['视觉传达设计', '数字媒体艺术'],
    eduReq: '本科以下'
  },
  '销售代表': {
    minSalary: 60000, maxSalary: 250000,
    majors: ['市场营销'],
    eduReq: '本科以下'
  },
  '电气工程师': {
    minSalary: 120000, maxSalary: 280000,
    majors: ['电气工程及其自动化'],
    eduReq: '本科'
  },
  '护士': {
    minSalary: 80000, maxSalary: 180000,
    majors: ['护理学'],
    eduReq: '本科以下'
  },
  '新媒体运营': {
    minSalary: 70000, maxSalary: 200000,
    majors: ['新闻传播', '网络与新媒体'],
    eduReq: '本科'
  },
  '机械工程师': {
    minSalary: 100000, maxSalary: 250000,
    majors: ['机械设计制造及其自动化'],
    eduReq: '本科'
  },
  '公务员': {
    minSalary: 80000, maxSalary: 150000,
    majors: [],
    eduReq: '本科'
  },
  '电商运营': {
    minSalary: 80000, maxSalary: 220000,
    majors: ['电子商务', '市场营销'],
    eduReq: '本科以下'
  },
  '律师': {
    minSalary: 150000, maxSalary: 500000,
    majors: ['法学'],
    eduReq: '本科'
  },
  '项目经理': {
    minSalary: 180000, maxSalary: 450000,
    majors: ['工程管理', '工商管理'],
    eduReq: '本科'
  },
  'UI/UX设计师': {
    minSalary: 120000, maxSalary: 300000,
    majors: ['交互设计', '工业设计'],
    eduReq: '本科'
  },
  '数据分析师': {
    minSalary: 150000, maxSalary: 350000,
    majors: ['统计学', '计算机科学与技术', '数学'],
    eduReq: '本科'
  },
  '网络安全工程师': {
    minSalary: 180000, maxSalary: 400000,
    majors: ['网络安全', '计算机科学与技术'],
    eduReq: '本科'
  },
  '金融分析师': {
    minSalary: 180000, maxSalary: 450000,
    majors: ['金融学', '经济学', '统计学'],
    eduReq: '硕士'
  },
  '心理咨询师': {
    minSalary: 80000, maxSalary: 300000,
    majors: ['心理学', '应用心理学'],
    eduReq: '本科'
  },
  '建筑设计师': {
    minSalary: 120000, maxSalary: 350000,
    majors: ['建筑学', '城乡规划'],
    eduReq: '本科'
  },
  '供应链管理': {
    minSalary: 100000, maxSalary: 280000,
    majors: ['物流管理', '供应链管理'],
    eduReq: '本科'
  },
  '空乘人员': {
    minSalary: 80000, maxSalary: 200000,
    majors: ['航空服务', '旅游管理'],
    eduReq: '本科以下'
  },
  '食品研发工程师': {
    minSalary: 100000, maxSalary: 250000,
    majors: ['食品科学与工程', '生物技术'],
    eduReq: '本科'
  },
  '兽医': {
    minSalary: 90000, maxSalary: 220000,
    majors: ['动物医学'],
    eduReq: '硕士'
  },
  '保险顾问': {
    minSalary: 60000, maxSalary: 500000,
    majors: ['金融学', '市场营销'],
    eduReq: '本科以下'
  },
  '健身教练': {
    minSalary: 50000, maxSalary: 250000,
    majors: ['体育教育', '运动康复'],
    eduReq: '本科以下'
  },
  '碳排放管理员': {
    minSalary: 150000, maxSalary: 400000,
    majors: ['环境工程', '能源经济'],
    eduReq: '本科'
  },
  '企业家': {
    minSalary: 200000, maxSalary: 2000000,
    majors: [],
    eduReq: '本科'
  },
  '体力活': {
    minSalary: 25000, maxSalary: 25000,
    majors: [],
    eduReq: '本科以下'
  }
}

// 游戏状态管理
export const gameStore = reactive({
  // 游戏基础状态
  isGameStarted: false,
  currentYear: 0,
  gameSpeed: 3000, // 3秒 = 1年
  globalEconomy: 0,
  
  // 人物数据
  persons: [],
  
  // 世界状态（新增）
  worldState: {
    regionType: 'city',
    cityName: '合肥',
    economicCycle: 1.0,
    useNewEconomics: true // 默认启用新经济模式
  },
  
  // 家族资产系统
  familyAssets: {
    // 保留原有学区房系统（兼容）
    schoolDistrictHouse: {
      owned: false,
      purchasePrice: 0,
      purchaseYear: 0
    },
    // 新住房系统
    housing: {
      mode: 'none', // 'none' | 'own' | 'rent'
      regionType: 'city',
      cityName: '合肥',
      schoolTier: 'none', // 'none'|'avg'|'good'|'top'
      area: 80, // 面积
      buyYear: 0,
      currentPrice: 0, // 总价
      priceIndex: 1.0, // 用于年更新
      annualMortgage: 0 // 年供
    }
  },
  
  // 游戏控制
  isPaused: false,
  gameTimer: null,
  isGameOver: false,
  gameOverReason: '',
  
  // 事件系统
  currentEvent: null,
  isEventActive: false,
  
  // 新事件系统 v2.0 状态
  eventCooldowns: {}, // 记录各事件的冷却时间
  yearlyEventCount: { major: 0, normal: 0 }, // 本年已触发的事件数量
  currentEventQueue: [], // 当年随机事件队列（对象：{key, personId}）
  pendingNormalEvent: null, // 当前正在展示的普通事件
  isNormalSheetOpen: false, // 底部弹层是否显示
  
  // 初始化游戏
  initGame() {
    this.currentYear = 0
    this.globalEconomy = this.generateInitialWealth()
    this.persons = []
    // 新增 world 对象
    this.world = { industry: { multipliers: { macro: 1 } } }
    // 初始化世界状态
    this.worldState = {
      regionType: 'city',
      cityName: getRandomCity('city'),
      economicCycle: 1.0,
      useNewEconomics: true
    }
    // 重置住房状态
    this.familyAssets.housing = {
      mode: 'none',
      regionType: 'city',
      cityName: this.worldState.cityName,
      schoolTier: 'none',
      buyYear: 0,
      currentPrice: 0,
      priceIndex: 1.0
    }
    this.createInitialPerson()
    this.isGameStarted = true
    // 模块初始化
    decorateCareers(CAREERS)
    initIndustry(this.world)
    this.startGameTimer()
  },
  
  // 生成初始财富（以50万为中心的指数衰减分布）
  generateInitialWealth() {
    const baseWealth = 500000 // 50万基准
    const minWealth = 100000  // 10万最低
    const maxWealth = 10000000 // 1000万最高
    
    // 使用指数分布生成财富
    const lambda = 2 // 衰减系数，越大衰减越快
    const randomValue = Math.random()
    
    let wealth
    if (randomValue < 0.5) {
      // 50%概率生成40-60万的中等收入
      wealth = baseWealth * (0.8 + Math.random() * 0.4)
    } else if (randomValue < 0.8) {
      // 30%概率生成10-40万的较低收入
      const factor = Math.pow(Math.random(), lambda)
      wealth = minWealth + factor * (baseWealth * 0.8 - minWealth)
    } else {
      // 20%概率生成60万以上的较高收入，指数衰减
      const factor = Math.pow(Math.random(), lambda * 2)
      wealth = baseWealth * 1.2 + factor * (maxWealth - baseWealth * 1.2)
    }
    
    return Math.floor(wealth)
  },
  
  // 生成正态分布随机数（属性用，限制0-100）
  generateNormalDistribution(mean, stdDev) {
    let u = 0, v = 0
    while(u === 0) u = Math.random() // 避免0
    while(v === 0) v = Math.random()
    
    const z = Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v)
    const result = z * stdDev + mean
    
    // 限制在0-100范围内
    return Math.max(0, Math.min(100, Math.round(result)))
  },
  
  // 生成正态分布随机数（经济支出用，不限制范围）
  generateNormalDistributionForExpense(mean, stdDev) {
    let u = 0, v = 0
    while(u === 0) u = Math.random() // 避免0
    while(v === 0) v = Math.random()
    
    const z = Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v)
    const result = z * stdDev + mean
    
    // 只确保不是负数，不限制上限
    return Math.max(0, Math.round(result))
  },
  
  // 生成婴儿属性：50%概率继承父母均值，50%概率随机生成
  generateBabyAttribute(parentAttr1, parentAttr2) {
    if (Math.random() < 0.5) {
      // 50%概率：继承父母均值（加一些随机变化）
      const mean = (parentAttr1 + parentAttr2) / 2
      return Math.floor(mean + (Math.random() - 0.5) * 10) // ±5的随机变化
    } else {
      // 50%概率：完全随机生成
      return this.generateNormalDistribution(50, 15)
    }
  },
  
  // 高考算法：根据智力生成大学档次（增强版，兼容旧调用）
  calculateGaokaoResult(intelligence, hasLove = false, personRef = null) {
    if (personRef) {
      const score = calcGaokaoScore(personRef)
      const band = bandByScore(score)
      return band
    }
    // 兼容旧调用：没传 personRef 就走旧逻辑
    const mean = intelligence - 10
    const stdDev = hasLove ? 20 : 15
    const score = this.generateNormalDistribution(mean, stdDev)
    if (score >= 75) return '985'
    if (score >= 50) return '211'
    if (score >= 25) return '双非'
    return '二本'
  },
  
  // 随机选择专业（4个选择）
  generateMajorOptions() {
    const shuffled = [...MAJORS].sort(() => 0.5 - Math.random())
    return shuffled.slice(0, 4)
  },
  
  // 生成工作选择（3个）
  generateJobOptions(person) {
    const availableJobs = Object.keys(CAREERS).filter(job => {
      const career = CAREERS[job]
      // 检查学历要求
      if (career.eduReq === '硕士' && person.education !== '硕士') return false
      if (career.eduReq === '本科' && !person.education.includes('大学') && person.education !== '硕士') return false
      return true
    })
    
    const options = []
    
    // 1. 体力活必然出现
    options.push('体力活')
    
    // 2. 专业对口的工作必然出现（如果有）
    if (person.major) {
      const majorMatchJobs = availableJobs.filter(job => {
        const career = CAREERS[job]
        return career.majors.includes(person.major) && job !== '体力活'
      })
      if (majorMatchJobs.length > 0) {
        const randomMajorJob = majorMatchJobs[Math.floor(Math.random() * majorMatchJobs.length)]
        options.push(randomMajorJob)
      }
    }
    
    // 3. 填充到3个选项
    const remainingJobs = availableJobs.filter(job => !options.includes(job))
    while (options.length < 3 && remainingJobs.length > 0) {
      const randomIndex = Math.floor(Math.random() * remainingJobs.length)
      options.push(remainingJobs.splice(randomIndex, 1)[0])
    }
    
    return options
  },
  
  // 计算入职成功率
  calculateJobSuccessRate(person, jobName) {
    const career = CAREERS[jobName]
    let successRate = 0.5 // 基础成功率
    
    // 体力活特殊处理 - 90%成功率
    if (jobName === '体力活') {
      return 0.9
    }
    
    // 辍学特殊处理
    if (person.education === '初中') {
      // 初中辍学：(智力+魅力)/20
      successRate = (person.intelligence + person.charm) / 2000
    } else if (person.education === '高中') {
      // 高中辍学：(智力+魅力)/10
      successRate = (person.intelligence + person.charm) / 1000
    } else {
      // 正常学历的成功率计算
      // 学历加成
      if (person.schoolLevel === '211') successRate += 0.1
      if (person.schoolLevel === '985') successRate += 0.2
      if (person.education === '硕士' && career.eduReq !== '硕士') successRate += 0.1
      
      // 专业匹配检查
      const isMajorMatch = career.majors.length === 0 || career.majors.includes(person.major)
      if (!isMajorMatch) successRate -= 0.15
    }
    
    return Math.max(0.01, Math.min(1, successRate)) // 最低1%成功率
  },
  
  // 计算升职成功率
  calculatePromotionRate(person, jobName) {
    // const career = CAREERS[jobName] // 暂未使用
    const specialJobs = ['保险顾问', '健身教练', '销售代表', '空乘人员']
    
    if (specialJobs.includes(jobName)) {
      // 特殊职业的升职算法
      return (person.intelligence / 10 + person.charm / 1.5) / 100
    } else {
      // 普通职业的升职算法
      let rate = (person.intelligence / 5 + person.charm / 3) / 100
      
      if (person.schoolLevel === '211') rate += 0.05
      if (person.schoolLevel === '985') rate += 0.08
      if (person.education === '硕士') rate += 0.05
      
      return Math.max(0, Math.min(1, rate))
    }
  },
  
  // 计算择偶成功率
  calculateMarriageSuccessRate(person, target) {
    const targetScore = Math.max(target.health, target.charm, target.intelligence) + (target.income / 10000) * 2
    return Math.min(1, person.charm / targetScore)
  },
  
  // 创建初始人物（婴儿）
  createInitialPerson() {
    const person = {
      id: this.generateId(),
      name: this.generateRandomName(),
      age: 0,
      gender: Math.random() > 0.5 ? '男' : '女',
      health: this.generateNormalDistribution(50, 15), // 正态分布，均值50
      charm: this.generateNormalDistribution(50, 15),   // 正态分布，均值50
      intelligence: this.generateNormalDistribution(50, 15), // 正态分布，均值50
      // 新增属性
      stability: this.generateNormalDistribution(50, 15),
      motivation: this.generateNormalDistribution(50, 15),
      creativity: this.generateNormalDistribution(50, 15),
      stress: 0,
      cumStudyHours: 0,
      satisfaction: 50,
      // 新经济系统属性
      psyche: 50, // 心理健康
      strain: 30, // 生活压力
      competitiveness: 0, // 竞争力（自动计算）
      ambition: 50, // 野心 0-100
      // 求职偏好 0-1 累积
      prefGov: 0, // 体制偏好
      prefCorp: 0, // 企业偏好
      prefStartup: 0, // 创业偏好
      // 原有属性
      economicContribution: 0,
      income: 0,
      isAlive: true,
      partner: null,
      children: [],
      occupation: null,
      education: '未入学',
      schoolLevel: null, // 学历档次：二本、双非、211、985
      major: null, // 专业
      workYears: 0, // 工作年限
      jobSeeking: false, // 是否在找工作
      lastPromotionYear: 0, // 上次升职年份
      isRetired: false, // 是否退休
      flags: {
        internTier: 0, // 实习层级 0-2
        researchTier: 0, // 科研层级 0-2
        leaderTier: 0, // 干部层级 0-2
        jobFailCount: 0 // 求职失败次数
      }
    }
    this.persons.push(person)
  },
  
  // 开始游戏时间
  startGameTimer() {
    if (this.gameTimer) clearInterval(this.gameTimer)
    this.gameTimer = setInterval(() => {
      if (!this.isPaused && !this.isEventActive) {
        this.advanceYear()
      }
    }, this.gameSpeed)
  },
  
  // 推进一年（集成新系统）
  advanceYear() {
    this.currentYear++
    
    // A. 重置年度事件计数
    this.yearlyEventCount = { major: 0, normal: 0 }
    
    // B. 行业周期推进
    tickIndustry(this.world, this.currentYear)
    
    // C. 房价年度更新（新经济系统）
    if (this.familyAssets.housing?.mode !== 'none') {
      const housing = this.familyAssets.housing
      housing.priceIndex = nextHousePrice(housing.priceIndex, housing.regionType, housing.schoolTier)
      housing.currentPrice = calculateHousePrice(housing.regionType, housing.schoolTier, housing.priceIndex)
      
      // 房贷利率重定价（如果有房贷且已标记）
      if (housing.mode === 'own' && housing.annualMortgage && this.persons.some(p => p.flags?.considerRefinance)) {
        // 模拟利率微调：±0.2%
        const rateAdjust = (Math.random() - 0.5) * 0.004 // ±0.2%
        const newRate = Math.max(0.02, 0.046 + rateAdjust) // 基准4.6% ± 调整
        const remainingPrincipal = housing.currentPrice * 0.65 * (1 - (this.currentYear - housing.buyYear) * 0.03) // 简化余额计算
        housing.annualMortgage = annuityPayment(Math.max(0, remainingPrincipal), newRate, Math.max(1, 30 - (this.currentYear - housing.buyYear)))
        
        // 清除重定价标记
        this.persons.forEach(p => {
          if (p.flags?.considerRefinance) {
            delete p.flags.considerRefinance
          }
        })
      }
    }
    
    this.persons.forEach(person => {
      if (person.isAlive) {
        person.age++
        
        // 有工作的人工作年限+1
        if (person.occupation && !person.jobSeeking) {
          person.workYears = (person.workYears || 0) + 1
        }
        
        // 企业家每年收入增长
        if (person.occupation === '企业家' && person.flags?.entrepreneurYears !== undefined) {
          person.flags.entrepreneurYears++
          person.income += 10000
        }
        
        // 渐进退休处理（半工时）
        if (person.flags?.phasedRetire && !person.isRetired) {
          person.income = Math.round(person.income * 0.6)
          person.strain = Math.max(0, (person.strain || 50) - 2)
        }
        
        // 返聘补贴
        if (person.flags?.rehired && person.isRetired) {
          person.income += 20000
          person.strain = Math.min(100, (person.strain || 10) + 1)
        }
        
        this.updatePersonEconomics(person)
        
        // B. 对每个在职人员：更新满意度、可能主动离职
        const job = person.occupation && CAREERS[person.occupation]
        if (job) {
          const careerMatch = !job.majors?.length || (person.major && job.majors.includes(person.major))
          updateSatisfaction(person, careerMatch, person.stress || 0)
          if (maybeVoluntaryQuit(person)) {
            this.showEventResult(person, '主动离职', `由于满意度较低，${person.name}选择离职并开始找工作`, false)
          }
        }
        
        // C. 年度压力恢复 & 倦怠
        maybeBurnout(person) // 可能触发今年的倦怠标记（影响学习/升职表现）
        annualStressRecovery(person)
        
        // D. 新事件系统检查
        this.checkNewEventSystem(person)
        
        this.checkMortality(person)
        this.checkLifeEvents(person)
        this.checkLifeEnd(person)
      }
    })
    
    // 年度家庭总支出（新财务系统）
    try {
      const annualExpense = computeFamilyAnnualExpense(this)
      this.globalEconomy -= annualExpense
      
      // 处理住房年度支出
      payHousingForYear(this)
      
      // 检查房贷违约风险
      this.checkMortgageArrears()
      
      // 可选：显示支出详情（每5年一次）
      if (this.currentYear % 5 === 0) {
        console.log(`第${this.currentYear}年家庭支出: ${annualExpense.toLocaleString()}元`)
      }
    } catch (error) {
      console.error('计算年度支出失败:', error)
    }
    
    // 检查破产
    this.checkBankruptcy()
    
    // 处理年度随机事件队列（新事件系统v2.0）
    this.buildAndQueueRandomEvents()
    this.processEventQueueHead()
    
    // 检查游戏结束条件
    this.checkGameOver()
  },
  
  // 更新个人经济贡献（使用新经济模型）
  updatePersonEconomics(person) {
    // 计算竞争力（基于多维属性）
    person.competitiveness = Math.min(100, 
      (person.intelligence * 0.4 + person.charm * 0.3 + person.stability * 0.3)
    )
    
    // 使用新经济模型
    const { effectiveIncome, totalExpense, contribution } = computeAnnualEconomics(person, this, CAREERS)
    
    // 修复：将计算结果正确赋值给person.economicContribution
    person.economicContribution = contribution
    
    // 可选：记录详细信息用于调试
    if (this.currentYear % 5 === 0) {
      console.log(`${person.name} 经济状况: 收入${effectiveIncome}, 支出${totalExpense}, 贡献${contribution}`)
    }
    
    return { effectiveIncome, totalExpense, contribution }
  },
  
  // 获取职业工资范围
  getJobSalaryRange(jobName) {
    return CAREERS[jobName] || { minSalary: 50000, maxSalary: 100000 }
  },
  
  // 显示事件结果提醒窗口
  showEventResult(person, eventName, resultText, isSuccess = true) {
    const icon = isSuccess ? '✅' : '❌'
    // 暂停游戏直到用户确认
    this.isPaused = true
    uni.showModal({
      title: `${icon} ${eventName}`,
      content: `${person.name}\n\n${resultText}`,
      showCancel: false,
      confirmText: '继续',
      confirmColor: isSuccess ? '#007AFF' : '#FF3B30',
      success: (res) => {
        if (res.confirm) {
          // 用户确认后恢复游戏
          this.isPaused = false
        }
      }
    })
  },
  
  // 检查家族是否拥有学区房
  hasSchoolDistrictHouse() {
    return this.familyAssets.schoolDistrictHouse.owned
  },
  
  // 购买学区房
  purchaseSchoolDistrictHouse(price) {
    this.familyAssets.schoolDistrictHouse = {
      owned: true,
      purchasePrice: price,
      purchaseYear: this.currentYear
    }
  },
  
  // 出售学区房（危机时）
  sellSchoolDistrictHouse() {
    if (!this.familyAssets.schoolDistrictHouse.owned) return 0
    
    const originalPrice = this.familyAssets.schoolDistrictHouse.purchasePrice
    const sellPrice = Math.max(50000, this.generateNormalDistributionForExpense(originalPrice - 50000, (originalPrice - 50000) * 0.15))
    
    this.familyAssets.schoolDistrictHouse = {
      owned: false,
      purchasePrice: 0,
      purchaseYear: 0
    }
    
    return Math.floor(sellPrice)
  },
  
  // 处理升职（集成行业与倦怠系统）
  handlePromotion(person) {
    const career = CAREERS[person.occupation]
    const salesLike = ['保险顾问','健身教练','销售代表','空乘人员'].includes(person.occupation)
    const baseProb = calcPromotionProb(person, person.occupation, salesLike) // 已经做过clamp
    const industryMul = getMultiplier(career.cycleCategory, this.world) // 行业景气影响

    // 倦怠年：降 20% 表现（在 stress.maybeBurnout 设置了 flags）
    const burnoutMul = person.flags?.burnoutThisYear ? 0.8 : 1
    const finalProb = Math.max(0.01, Math.min(0.95, baseProb * Math.max(0.5, industryMul) * burnoutMul))
    
    if (Math.random() < finalProb) {
      const salaryCap = Math.round(career.maxSalary * Math.max(0.7, industryMul)) // 不让行业暴跌直接归零
      const salaryIncrease = Math.floor((career.maxSalary - career.minSalary) * 0.10)
      const newSalary = Math.min(person.income + salaryIncrease, salaryCap)
      person.income = newSalary
      person.health = Math.max(0, person.health - 2)
      person.lastPromotionYear = this.currentYear
      
      this.showEventResult(person, '升职成功', 
        `恭喜升职！\n💰 薪资增加：${salaryIncrease.toLocaleString()}元\n💼 新薪资：${person.income.toLocaleString()}元/年\n⚠️ 健康-2（工作压力增加）`, true)
    } else {
      person.lastPromotionYear = this.currentYear
      this.showEventResult(person, '升职失败', 
        `很遗憾，这次升职机会没有把握住\n💡 继续努力，三年后还有机会！`, false)
    }
    
    // 清除今年的倦怠标记（避免跨年持续）
    if (person.flags?.burnoutThisYear) person.flags.burnoutThisYear = false
  },
  
  // 检查人生事件
  checkLifeEvents(person) {
    // 检查重要事件（必然触发）
    const importantEvents = this.getImportantEvents(person.age, person)
    if (importantEvents.length > 0) {
      const event = importantEvents[0] // 只取第一个重要事件
      this.triggerEvent(person, event)
      return
    }
    
    // 随机事件现在由buildAndQueueRandomEvents和EVENT_POOL系统统一处理
    // 不再在这里单独处理随机事件
  },
  
  // 获取重要事件（必然触发）
  getImportantEvents(age, person) {
    const events = []
    
    // 高考（18岁，且没有辍学）
    if (age === 18 && !person.schoolLevel && person.education !== '初中' && person.education !== '高中') {
      const { score, percentile, tier: band } = calcGaokaoResult(person, this)
      const majorOptions = this.generateMajorOptions()
      
      // 根据档次给一个倾向的地域（985更偏 mega/city；二本偏 county/rural）
      const band2Region = (band, home) => {
        const rnd = Math.random()
        if (band==='985') return rnd<0.65 ? 'mega' : 'city'
        if (band==='211') return rnd<0.6 ? 'city' : (rnd<0.8 ? 'mega' : home)
        if (band==='双非') return rnd<0.6 ? 'county' : 'city'
        return rnd<0.6 ? 'county' : 'rural'
      }
      
      const homeRegion = this.familyAssets?.housing?.regionType || this.familyAssets?.housing?.region || 'city'
      
      const choices = [
        { text: '不上大学，直接工作', cost: 0, effects: {}, special: 'noCollege' },
        ...majorOptions.map(m => {
          const targetRegion = band2Region(band, homeRegion)
          return {
            text: `${band} - ${m}（城市：${randomCityName(targetRegion)}）`,
            cost: COLLEGE_COST_BY_BAND[band],
            effects: { 
              competitiveness: +(COLLEGE_COMP_BONUS[band]), 
              psyche: +(COLLEGE_PSY_BONUS[band]) 
            },
            special: 'college',
            majorData: { schoolLevel: band, major: m, studyRegion: targetRegion }
          }
        })
      ]
      this.currentEvent = { 
        person, 
        type: '高考', 
        ui: 'modal', 
        title: '高考出分', 
        icon: '🎓',
        text: `成绩：${score}`, 
        options: choices, 
        choices 
      }
      this.isEventActive = true
      return ['高考']
    }
    
    // 读研选择（22岁，双非及以上）
    if (age === 22 && person.schoolLevel && person.schoolLevel !== '二本' && !person.education.includes('硕士') && !person.jobSeeking) {
      events.push('读研选择')
    }
    
    // 二本学生22岁自动进入求职状态
    if (age === 22 && person.schoolLevel === '二本' && !person.jobSeeking && !person.occupation) {
      person.jobSeeking = true
      events.push('找工作')
    }
    
    // 研究生两年后毕业
    if (person.education === '硕士在读' && person.flags?.gradSchoolStartYear && 
        this.currentYear - person.flags.gradSchoolStartYear >= 2) {
      person.education = '硕士'
      person.jobSeeking = true
      events.push('找工作')
      this.showEventResult(person, '研究生毕业', 
        `🎓 恭喜硕士毕业！\n📚 获得硕士学位\n💼 开始寻找工作机会\n💰 硕士学历求职薪资+3万/年`, true)
      return events // 毕业处理完成后立即返回
    }
    
    // 辍学选择（12岁和16岁）
    if ((age === 12 || age === 16) && person.education === '未入学') {
      // 不直接触发，需要在其他事件中添加辍学选项
    }
    
    // 找工作（毕业后或辍学后）
    if (person.jobSeeking && !person.occupation) {
      events.push('找工作')
    }
    
    // 辍学后自动进入找工作状态
    if ((person.education === '初中' || person.education === '高中') && age >= 16 && !person.occupation && !person.jobSeeking) {
      person.jobSeeking = true
      events.push('找工作')
    }
    
    // 升职（工作3年后每3年一次，自动触发，体力活不能升职，退休后不再升职）
    if (person.occupation && person.occupation !== '体力活' && !person.isRetired && person.workYears >= 3 && person.workYears % 3 === 0 && person.lastPromotionYear < this.currentYear) {
      this.handlePromotion(person)
      return events // 升职处理完成后立即返回，避免同一年触发其他事件
    }
    
    // 择偶（25岁后未婚人士）
    if (age >= 25 && !person.partner && Math.random() < 0.3) {
      events.push('择偶')
    }
    
    // 结婚后住房选择
    if (person.flags?.needHousingAfterMarriage) {
      events.push('结婚住房选择')
    }
    
    // 生育（结婚一年后，女性40岁以下）
    if (person.partner && person.flags.marriageYear && this.currentYear - person.flags.marriageYear >= 1 && 
        ((person.gender === '女' && person.age < 40) || (person.partner.gender === '女' && person.partner.age < 45)) && 
        Math.random() < 0.2) {
      events.push('生育')
    }
    
    // 提前退休申请（55-60岁）
    if (age >= 55 && age <= 60 && person.occupation && !person.isRetired && Math.random() < 0.15) {
      events.push('提前退休申请')
    }
    
    // 渐进退休/返聘（62-65岁）
    if (age >= 62 && age < 65 && person.occupation && !person.isRetired && Math.random() < 0.2) {
      events.push('渐进退休')
    }
    
    // 65岁强制退休 + 返聘机会
    if (age === 65 && !person.isRetired && person.occupation) {
      const region = this.familyAssets?.housing?.regionType || this.familyAssets?.housing?.region || 'city'
      const base = PENSION.base * (PENSION.regionK[region] || 1)
      person.isRetired = true
      person.income = Math.round(Math.min(PENSION.cap, Math.max(PENSION.floor, base)))
      person.workYears = 0
      person.lastPromotionYear = 0
      
      // 返聘机会弹窗
      this.currentEvent = {
        person, type:'返聘', ui:'modal', icon:'🧑‍🏫',
        title:'退休返聘邀请',
        text:'单位希望你以顾问身份返聘，工时较低、收入少量补贴。',
        options: [
          { text:'接受返聘', cost:0, effects:{ flag:{ rehired:true } }, special:'rehire_accept' },
          { text:'婉拒', cost:0, effects:{} }
        ]
      }
      this.isEventActive = true
      return events // 退休处理完成后立即返回，避免同一年触发其他事件
    }
    
    return events
  },
  
  // 获取随机事件（已弃用，使用EVENT_POOL系统）
  getRandomEvents() {
    // 此方法已弃用，所有事件现在由EVENT_POOL统一管理
    // 保留方法以维持兼容性，但返回空数组
    console.warn('getRandomEvents已弃用，所有事件现在由EVENT_POOL统一管理')
    return []
  },
  
  // 触发事件（已弃用，使用EVENT_POOL系统）
  triggerEvent(person, eventType) {
    // 尝试从EVENT_POOL中找到对应事件
    const event = EVENT_POOL.find(e => e.title === eventType || e.id === eventType)
    if (event) {
      // 使用新的事件系统
      this.triggerNewEvent(event, person)
    } else {
      console.warn(`事件 ${eventType} 未在EVENT_POOL中找到，将被忽略`)
    }
  },
  
  
  // 生成高考大学选项
  generateCollegeOptions(person) {
    const majorOptions = this.generateMajorOptions()
    const schoolLevel = this.calculateGaokaoResult(person.intelligence, person.flags?.youngLove, person)
    
    const options = []
    majorOptions.forEach(major => {
      let cost = 20000
      let effects = { intelligence: 2 }
      
      if (schoolLevel === '985') {
        cost = 5000
        effects = { intelligence: 8, charm: 2 }
      } else if (schoolLevel === '211') {
        cost = 5000
        effects = { intelligence: 6, charm: 1 }
      } else if (schoolLevel === '双非') {
        cost = 30000
        effects = { intelligence: 4 }
      }
      
      options.push({
        text: `${schoolLevel}大学 - ${major}`,
        cost: cost,
        effects: effects,
        special: 'college',
        majorData: { schoolLevel, major }
      })
    })
    
    return options
  },
  
  // 生成工作事件选项（使用新就业系统）
  generateJobEventOptions(person) {
    const jobs = generateJobOffersNew(person, CAREERS) // 返回 [{job, region}]
    
    return jobs.map(({job, region}) => {
      const p = calcJobSuccessNew(person, job, CAREERS)
      return { 
        text: `应聘${job} @${region} (成功率${Math.round(p * 100)}%)`, 
        cost: 0, 
        effects: {}, 
        special: 'applyJob', 
        jobData: { jobName: job, successRate: p, targetRegion: region } 
      }
    })
  },
  
  // 生成结婚住房选项
  generateMarriageHousingOptions() {
    const regionType = this.worldState.regionType
    const options = []
    
    // 从constants.js获取价格参数
    const unitPrice = REGION_UNIT_PRICE[regionType] || 25000
    const rentBase = REGION_RENT_BASE[regionType] || 2400
    
    // 租房选项（学区等级不同）
    options.push({
      text: `租普通住房 (年租金${Math.round(rentBase * 12).toLocaleString()}元)`,
      cost: 0,
      effects: { psyche: -2 },
      special: 'rentHouse',
      housingData: { mode: 'rent', schoolTier: 'none' }
    })
    
    options.push({
      text: `租学区房 (年租金${Math.round(rentBase * 12 * 1.3).toLocaleString()}元)`,
      cost: 0,
      effects: { psyche: -1 },
      special: 'rentHouse', 
      housingData: { mode: 'rent', schoolTier: 'avg' }
    })
    
    // 买房选项（需要首付）
    const area = 80 // 默认80平
    const nonePrice = Math.round(unitPrice * area)
    const avgPrice = Math.round(unitPrice * area * SCHOOL_ZONE_PREMIUM)
    const goodPrice = Math.round(unitPrice * area * SCHOOL_ZONE_PREMIUM * 1.4)
    
    options.push({
      text: `买普通住房 (总价${Math.round(nonePrice/10000)}万，首付${Math.round(nonePrice * DOWNPAY_DEFAULT/10000)}万)`,
      cost: Math.round(nonePrice * DOWNPAY_DEFAULT),
      effects: { psyche: +3 },
      special: 'buyHouse',
      housingData: { mode: 'own', schoolTier: 'none' }
    })
    
    if (this.globalEconomy >= avgPrice * DOWNPAY_DEFAULT - 200000) {
      options.push({
        text: `买学区房 (总价${Math.round(avgPrice/10000)}万，首付${Math.round(avgPrice * DOWNPAY_DEFAULT/10000)}万)`,
        cost: Math.round(avgPrice * DOWNPAY_DEFAULT),
        effects: { psyche: +5 },
        special: 'buyHouse',
        housingData: { mode: 'own', schoolTier: 'avg' }
      })
    }
    
    if (this.globalEconomy >= goodPrice * DOWNPAY_DEFAULT - 100000) {
      options.push({
        text: `买优质学区房 (总价${Math.round(goodPrice/10000)}万，首付${Math.round(goodPrice * DOWNPAY_DEFAULT/10000)}万)`,
        cost: Math.round(goodPrice * DOWNPAY_DEFAULT),
        effects: { psyche: +8 },
        special: 'buyHouse',
        housingData: { mode: 'own', schoolTier: 'good' }
      })
    }
    
    return options
  },

  // 生成城市迁移选项
  generateCityMigrationOptions() {
    const currentRegion = this.worldState.regionType
    const options = []
    
    // 如果当前在非一线城市，提供一线城市选项
    if (currentRegion !== 'mega') {
      options.push({
        text: '迁移到一线城市 (高收入机会，高生活成本)',
        cost: 80000, // 搬家成本
        effects: { strain: +8, ambition: +2 },
        special: 'relocateToMega'
      })
    }
    
    // 如果当前在一线城市，提供回流选项
    if (currentRegion === 'mega') {
      options.push({
        text: '回到二三线城市 (生活压力小，发展受限)',
        cost: 50000,
        effects: { strain: -5, psyche: +3 },
        special: 'relocateToStable',
        targetRegion: 'city'
      })
    }
    
    // 如果在城市，提供县城选项
    if (currentRegion === 'city') {
      options.push({
        text: '回到家乡县城 (安逸生活，收入降低)',
        cost: 30000,
        effects: { strain: -8, psyche: +5 },
        special: 'relocateToStable',
        targetRegion: 'county'
      })
    }
    
    // 保持现状选项
    options.push({
      text: '不迁移，继续留在当地',
      cost: 0,
      effects: { stability: +1 }
    })
    
    return options
  },

  // 生成住房升级选项
  generateHousingUpgradeOptions() {
    const housing = this.familyAssets.housing
    const currentRegion = this.worldState.regionType
    const options = []
    
    if (housing.mode === 'rent') {
      // 租房转买房
      const unitPrice = REGION_UNIT_PRICE[currentRegion] || 25000
      const area = 80
      const price = Math.round(unitPrice * area * 1.2) // 稍好的房子
      const downPayment = Math.round(price * DOWNPAY_DEFAULT)
      
      options.push({
        text: `租转买：购买住房 (总价${Math.round(price/10000)}万，首付${Math.round(downPayment/10000)}万)`,
        cost: downPayment,
        effects: { psyche: +5, strain: +3 },
        special: 'upgradeRentToBuy'
      })
    }
    
    if (housing.mode === 'own') {
      // 学区升级
      if (housing.schoolTier === 'none' || housing.schoolTier === 'avg') {
        const targetTier = housing.schoolTier === 'none' ? 'avg' : 'good'
        const upgradeCost = housing.schoolTier === 'none' ? 800000 : 1200000
        
        options.push({
          text: `学区升级：换到${targetTier === 'avg' ? '普通' : '优质'}学区房 (换房成本${Math.round(upgradeCost/10000)}万)`,
          cost: upgradeCost,
          effects: { psyche: +3, strain: +8 },
          special: 'upgradeSchoolTier',
          targetTier: targetTier
        })
      }
      
      // 面积升级
      if (housing.area < 120) {
        options.push({
          text: `面积升级：换大房子 (换房成本50万)`,
          cost: 500000,
          effects: { psyche: +2, strain: +5 },
          special: 'upgradeArea'
        })
      }
    }
    
    // 保持现状
    options.push({
      text: '满足现状，不升级住房',
      cost: 0,
      effects: { stability: +1 }
    })
    
    return options
  },

  // 生成择偶选项
  generateMarriageOptions(person) {
    const options = []
    
    // 生成3个候选对象
    for (let i = 0; i < 3; i++) {
      const target = this.generateRandomPerson(person.age + Math.floor((Math.random() - 0.5) * 6))
      const successRate = this.calculateMarriageSuccessRate(person, target)
      const weddingCost = Math.floor(Math.random() * 150000) + 50000
      
      options.push({
        text: `${target.name} (魅力${target.charm}, 收入${Math.floor(target.income/10000)}万, 成功率${Math.round(successRate * 100)}%)`,
        cost: weddingCost,
        effects: {},
        special: 'marry',
        partnerData: target
      })
    }
    
    options.push({
      text: '暂不结婚',
      cost: 0,
      effects: {}
    })
    
    return options
  },
  
  // 生成随机人物
  generateRandomPerson(age) {
    const jobNames = Object.keys(CAREERS)
    const randomJob = jobNames[Math.floor(Math.random() * jobNames.length)]
    const career = CAREERS[randomJob]
    const income = career.minSalary + Math.random() * (career.maxSalary - career.minSalary)
    
    return {
      name: this.generateRandomName(),
      age: age,
      gender: Math.random() > 0.5 ? '男' : '女',
      health: this.generateNormalDistribution(50, 15),
      charm: this.generateNormalDistribution(50, 15),
      intelligence: this.generateNormalDistribution(50, 15),
      income: Math.floor(income),
      occupation: randomJob
    }
  },
  
  // 处理事件选择（集成学习压力注入与新事件系统）
  handleEventChoice(option) {
    const person = this.currentEvent.person
    const isNewEventSystem = !!this.currentEvent.eventData
    
    // 检查是否有足够经济（允许负债30万内继续选择）
    const cost = option.cost || 0
    if (this.globalEconomy - cost < -300000) {
      uni.showToast({ 
        title: '此选择将导致破产，无法选择', 
        icon: 'none',
        duration: 3000
      })
      return
    }
    
    // 扣除费用
    this.globalEconomy -= cost
    
    // 应用基础属性效果
    if (isNewEventSystem) {
      // 新事件系统的效果处理
      this.applyNewEventEffects(person, option.effects)
    } else {
      // 原有事件系统的效果处理
      Object.keys(option.effects).forEach(key => {
        if (['health', 'charm', 'intelligence'].includes(key)) {
          person[key] = Math.min(100, Math.max(0, person[key] + option.effects[key]))
        } else if (key === 'occupation') {
          person[key] = option.effects[key]
        }
      })
    }
    
    // 学习类事件：注入学习压力（补习、奥数等）
    if (this.isStudyEvent(option, this.currentEvent.type)) {
      const hours = this.getStudyHours(option)
      if (hours > 0) {
        applyStudyStress(person, hours)
      }
    }
    
    // 处理特殊效果
    if (option.special) {
      this.handleSpecialEffects(person, option.special, option)
    }
    
    this.isEventActive = false
    this.currentEvent = null
  },
  
  // 新事件系统效果应用器
  applyNewEventEffects(person, effects) {
    Object.keys(effects).forEach(key => {
      const value = effects[key]
      
      switch (key) {
        // 基础属性
        case 'health':
        case 'charm':
        case 'intelligence':
        case 'stability':
        case 'motivation':
        case 'creativity':
          person[key] = Math.min(100, Math.max(0, (person[key] || 50) + value))
          break
          
        // 新经济系统属性
        case 'psyche':
          person.psyche = Math.min(100, Math.max(0, (person.psyche || 50) + value))
          break
        case 'strain':
          person.strain = Math.min(100, Math.max(0, (person.strain || 0) + value))
          break
        case 'competitiveness':
          person.competitiveness = Math.min(100, Math.max(0, (person.competitiveness || 0) + value))
          break
        case 'ambition':
          person.ambition = Math.min(100, Math.max(0, (person.ambition || 50) + value))
          break
          
        // 求职偏好属性 (0-1累积)
        case 'prefGov':
          person.prefGov = Math.min(1, Math.max(0, (person.prefGov || 0) + value))
          break
        case 'prefCorp':
          person.prefCorp = Math.min(1, Math.max(0, (person.prefCorp || 0) + value))
          break
        case 'prefStartup':
          person.prefStartup = Math.min(1, Math.max(0, (person.prefStartup || 0) + value))
          break
          
        // 经济效果
        case 'cash':
          this.globalEconomy += value
          break
        case 'income':
          if (typeof value === 'number' && value > 0 && value < 1) {
            // 百分比增长
            person.income = Math.round((person.income || 0) * (1 + value))
          } else {
            // 绝对值增长
            person.income = Math.max(0, (person.income || 0) + value)
          }
          break
          
        // 状态标记
        case 'unemployed':
          if (value === true) {
            person.occupation = null
            person.income = 0
            person.jobSeeking = true
            person.workYears = 0
          }
          break
          
        // 自定义标记
        case 'flag':
          if (!person.flags) person.flags = {}
          // 支持履历层级的累积逻辑
          Object.keys(value).forEach(flagKey => {
            if (['internTier', 'researchTier', 'leaderTier'].includes(flagKey)) {
              // 履历层级使用Math.max逻辑，不会倒退
              person.flags[flagKey] = Math.max(person.flags[flagKey] || 0, value[flagKey])
            } else if (flagKey === 'gamingHours') {
              // 游戏时间累积或减少
              const currentHours = person.flags[flagKey] || 0
              person.flags[flagKey] = Math.max(0, currentHours + value[flagKey])
            } else {
              // 其他标记直接赋值
              person.flags[flagKey] = value[flagKey]
            }
          })
          break
          
        // 特殊处理
        case 'special':
          this.handleSpecialNewEventEffects(person, value)
          break
          
        default:
          // 其他未知属性直接赋值
          person[key] = value
          break
      }
    })
  },
  
  // 新事件系统特殊效果处理
  handleSpecialNewEventEffects(person, special) {
    switch (special) {
      case 'layoffChance':
        // 裁员风险：50%概率保住工作
        if (Math.random() < 0.5) {
          this.showEventResult(person, '内部转岗', 
            `🎯 成功转岗避免裁员！\\n💼 保住工作但薪资略降\\n💪 危机中展现韧性`, true)
        } else {
          person.occupation = null
          person.income = 0
          person.jobSeeking = true
          person.workYears = 0
          person.strain = Math.min(100, (person.strain || 0) + 12)
          this.showEventResult(person, '裁员', 
            `😢 不幸被裁员\\n💔 失去工作和收入\\n🔍 需要重新找工作\\n📈 压力大幅上升`, false)
        }
        break
        
      case 'probationTest':
        // 试用期测试：基于能力判断
        const passRate = Math.min(0.8, (person.competitiveness || 0) / 100 + (person.motivation || 0) / 150)
        if (Math.random() < passRate) {
          this.showEventResult(person, '试用期转正', 
            `✅ 成功通过试用期！\\n🎉 正式转正\\n📈 工作稳定性提升`, true)
        } else {
          person.occupation = null
          person.income = 0
          person.jobSeeking = true
          person.psyche = Math.max(0, (person.psyche || 50) - 8)
          this.showEventResult(person, '试用期失败', 
            `😞 试用期未能转正\\n💼 需要重新找工作\\n😔 心理健康受挫`, false)
        }
        break
        
      default:
        console.log(`未知的新事件特殊效果: ${special}`)
        break
    }
  },
  
  // 判断是否为学习类事件
  isStudyEvent(option, eventType) {
    const studyEvents = ['课外补习']
    const studyOptions = ['常规补习', '奥数', '兴趣班', '一对一私教']
    return studyEvents.includes(eventType) && studyOptions.some(opt => option.text.includes(opt))
  },
  
  // 获取学习小时数
  getStudyHours(option) {
    if (option.text.includes('奥数')) return CONFIG.study.tutoring.olympiad
    if (option.text.includes('常规补习')) return CONFIG.study.tutoring.regular
    if (option.text.includes('兴趣班')) return CONFIG.study.tutoring.hobby
    if (option.text.includes('一对一私教')) return CONFIG.study.tutoring.private
    return 0
  },
  
  // 处理特殊效果
  handleSpecialEffects(person, special, option) {
    if (!person.flags) person.flags = {}
    
    switch (special) {
      case 'earlyEducation':
        person.flags.earlyEducation = true
        break
      case 'internationalKG':
        person.flags.internationalKG = true
        break
      case 'schoolDistrict':
        // 购买学区房，成为全家族资产
        this.purchaseSchoolDistrictHouse(300000)
        uni.showToast({ 
          title: '学区房已购买，全家族未成年人受益！', 
          icon: 'success',
          duration: 3000
        })
        break
      case 'talentShow':
        if (person.intelligence > 60) person.intelligence += 1
        else if (Math.random() < 0.3) person.health -= 1 // 失败概率
        break
      case 'privateMiddle':
        if (this.globalEconomy < 200000) {
          // 借贷利息
          person.flags.debt = 10000
        }
        break
      case 'gaming':
        person.flags.gaming = true
        break
      case 'international':
        person.flags.international = true
        person.education = '国际高中'
        break
      case 'youngLove':
        if (person.charm < 50 && Math.random() < 0.5) {
          person.health -= 1 // 分手
        }
        break
      case 'gapYear':
        person.flags.gapYear = true
        break
      case 'collegeStartup':
        if (Math.random() < 0.5) {
          person.income += 50000
        } else {
          this.globalEconomy -= 30000
          person.intelligence -= 1
        }
        break
      case 'stocks':
        if (Math.random() < 0.5) {
          this.globalEconomy += 200000
          this.showEventResult(person, '炒股', 
            `📈 投资成功！\n💰 获得收益：20万元\n🎯 总投入10万，净赚10万`, true)
        } else {
          this.showEventResult(person, '炒股', 
            `📉 投资失败\n💸 血本无归\n💔 10万元打了水漂`, false)
        }
        break
      case 'teaShop':
        if (Math.random() < 0.25) {
          person.flags.teaShop = true
          person.passiveIncome = 25000
          this.showEventResult(person, '奶茶店投资', 
            `🧋 投资成功！\n🏪 奶茶店开业\n💰 年被动收入：2.5万元\n📊 投资15万，年回报率17%`, true)
        } else {
          this.showEventResult(person, '奶茶店投资', 
            `📉 投资失败\n💸 奶茶店经营不善倒闭\n💔 15万元投资损失`, false)
        }
        break
      case 'lottery':
        if (Math.random() < 0.01) {
          this.globalEconomy += 5000000 // 中奖500万
          // 显著的中奖特效
          uni.showModal({
            title: '🎉 天选之子！🎉',
            content: `🎊恭喜${person.name}中得彩票大奖500万元！🎊\n\n💰 家庭财富瞬间暴增！\n🌟 人生巅峰时刻！`,
            showCancel: false,
            confirmText: '太棒了！',
            success: () => {
              uni.showToast({ 
                title: '💸 500万到账！💸', 
                icon: 'success',
                duration: 3000
              })
            }
          })
        }
        break
      case 'midlifeStartup':
        if (Math.random() < 0.3) {
          person.occupation = '企业家'
          const newIncome = person.income + 100000
          person.income = newIncome
          person.flags.entrepreneurYears = 0 // 设置企业家年限标记
          this.showEventResult(person, '中年创业', 
            `🚀 创业成功！\n💼 转型为企业家\n💰 收入增加：10万元\n📈 年收入：${newIncome.toLocaleString()}元`, true)
        } else {
          const oldIncome = person.income
          person.income = 0
          person.occupation = null
          this.showEventResult(person, '中年创业', 
            `💔 创业失败\n😰 失业了\n💸 损失原收入：${oldIncome.toLocaleString()}元\n🔍 需要重新找工作`, false)
        }
        break
      case 'stagnant':
        const decreaseAmount = Math.min(50000, person.income * 0.2)
        person.income = Math.max(0, person.income - decreaseAmount)
        this.showEventResult(person, '中年危机', 
          `😴 选择混日子\n📉 收入下降：${decreaseAmount.toLocaleString()}元\n💼 新年收入：${person.income.toLocaleString()}元\n⏰ 职业生涯停滞不前`, false)
        break
      // 退休处理已移到 getImportantEvents 中自动执行
      case 'baby1':
        this.createBaby(person, 1)
        break
      case 'baby2':
        this.createBaby(person, 2)
        break
      case 'college2':
        person.education = '二本'
        break
      case 'college1':
        person.education = '双非一本'
        break
      case 'college211':
        person.education = '211大学'
        break
      case 'college985':
        person.education = '985大学'
        break
      case 'artCollege':
        person.education = '艺术院校'
        person.occupation = '艺术家'
        break
      case 'noCollege':
        person.education = '高中'
        break
      case 'factory':
        person.income = 40000
        break
      case 'stateEnterprise':
        person.income = 80000
        break
      case 'bigTech':
        person.income = 150000
        break
      case 'civilServant':
        person.income = 100000
        person.flags.civilServant = true
        break
      case 'startup':
        if (Math.random() < 0.6) {
          person.income = 200000
        } else {
          person.income = 20000 // 创业失败
        }
        break
      case 'marry':
        // 验证择偶成功率
        if (option.partnerData) {
          const successRate = this.calculateMarriageSuccessRate(person, option.partnerData)
          if (Math.random() < successRate) {
            this.createPartner(person, option.partnerData)
          } else {
            this.showEventResult(person, '求婚', 
              `💔 求婚失败\n😢 对方拒绝了求婚\n💪 不要气馁，缘分还在等待`, false)
          }
        }
        break
        
      // 辍学处理
      case 'dropout12':
        person.education = '初中'
        person.jobSeeking = true
        uni.showToast({ title: '已辍学，开始找工作', icon: 'none' })
        break
      case 'dropout16':
        person.education = '高中'
        person.jobSeeking = true
        uni.showToast({ title: '已辍学，开始找工作', icon: 'none' })
        break
        
      // 新的事件处理
      case 'noCollege':
        person.education = '高中'
        person.jobSeeking = true
        break
      case 'college':
        if (option.majorData) {
          const { schoolLevel, major, studyRegion } = option.majorData
          person.schoolLevel = schoolLevel
          person.major = major
          person.education = schoolLevel + '大学'
          // 个人学习地域（影响后续校招/实习与第一份工作地区偏好）
          person.region = studyRegion
          // 可提示：已被外地院校录取/在本地上大学
          this.showEventResult(person, '录取', `前往 ${studyRegion} 上大学（不影响家庭常住地）`, true)
        }
        break
      case 'startJobSeeking':
        person.jobSeeking = true
        break
      case 'gradSchool':
        // 基于 competitiveness / 科研 / 干部 / 压力 / 学校层级
        const gradBase = 0.15 + (person.competitiveness - 50) / 200
        const tier = (person.flags?.researchTier || 0) * 0.12 + (person.flags?.leaderTier || 0) * 0.05
        const band = person.schoolLevel === '985' ? 0.28 : person.schoolLevel === '211' ? 0.16 : person.schoolLevel === '双非' ? 0.06 : 0
        const stressPenalty = Math.max(0, person.strain - 70) / 200
        const finalSuccessRate = Math.max(0, Math.min(0.95, gradBase + tier + band - stressPenalty))
        if (Math.random() < finalSuccessRate) {
          person.education = '硕士在读'
          person.intelligence += 3
          // 记录入学年份，用于两年后毕业
          if (!person.flags) person.flags = {}
          person.flags.gradSchoolStartYear = this.currentYear
          this.showEventResult(person, '考研', 
            `🎓 考研成功！\n📚 开始硕士学习\n🧠 智力+3\n📖 两年后将毕业求职`, true)
        } else {
          person.jobSeeking = true
          this.showEventResult(person, '考研', 
            `📖 考研失败\n💼 开始找工作\n💪 虽然遗憾，但人生还有很多机会！`, false)
        }
        break
      case 'applyJob':
        if (option.jobData) {
          const { jobName, successRate, targetRegion } = option.jobData
          const career = CAREERS[jobName]
          // 行业景气度影响求职成功率
          const industryMul = getMultiplier(career.cycleCategory, this.world)
          const adjustedSuccessRate = Math.max(0.01, Math.min(0.95, successRate * Math.max(0.6, industryMul)))
          
          if (Math.random() < adjustedSuccessRate) {
            person.occupation = jobName
            person.jobSeeking = false
            const region = targetRegion || (this.familyAssets?.housing?.regionType || 'city')
            person.income = calcStartingSalaryNew(person, jobName, region, CAREERS)
            person.workYears = 0

            // 个人工作地域更新（先改个人）
            person.region = region

            // 若已婚并与家庭常住地不同 -> 弹"是否全家迁移？"
            const familyRegion = this.familyAssets?.housing?.regionType || 'city'
            if (person.partner && region !== familyRegion){
              this.currentEvent = {
                person, type:'就业异地', ui:'modal', icon:'🧭',
                title:'异地工作选择',
                text:`你获得了 ${region} 的岗位机会。是否全家一起迁移？`,
                options: [
                  { text:'我先去，家庭不动', cost:0, effects:{ psyche:-1, strain:+2 }, special:'job_relocate_self' },
                  { text:'全家一起迁移',     cost:0, effects:{}, special:'job_relocate_family', targetRegion:region },
                  { text:'放弃机会',         cost:0, effects:{ unemployed:true }, special:'job_relocate_decline' }
                ]
              }
              this.isEventActive = true
            } else {
              // 正常结果提示
              this.showEventResult(person, '求职', `🎉 入职 ${jobName} @${region}\n年薪：${person.income.toLocaleString()} 元`, true)
            }
          } else {
            person.flags.jobFailCount = (person.flags.jobFailCount || 0) + 1
            person.psyche = Math.max(0, (person.psyche || 50) - 3)
            person.strain = Math.min(100, (person.strain || 50) + 2)
            this.showEventResult(person, '求职', '😔 求职失败，继续加油', false)
          }
        }
        break
      case 'haveBaby':
        if (person.partner) {
          const birthSuccess = (person.health + person.partner.health) / 200
          if (Math.random() < birthSuccess) {
            this.createBaby(person, 1)
            if (person.gender === '女') person.health -= 5
            this.showEventResult(person, '生育', 
              `👶 成功生育！\n💕 家庭新成员诞生\n🎉 家族人口增加\n${person.gender === '女' ? '🩺 母亲健康-5' : ''}`, true)
          } else {
            this.showEventResult(person, '生育', 
              `😢 生育失败\n💙 虽然这次没有成功，但可以继续尝试\n🏥 建议注意身体健康`, false)
          }
        }
        break
      case 'collegeStartup':
        const startupSuccess = (person.intelligence + person.charm) / 4 / 100
        if (Math.random() < startupSuccess) {
          person.occupation = '企业家'
          person.income = 200000
          person.flags.entrepreneurYears = 0
          this.showEventResult(person, '大学创业', 
            `🚀 创业成功！\n💼 成为企业家\n💰 年收入：20万元\n📈 每年收入+1万元`, true)
        } else {
          this.showEventResult(person, '大学创业', 
            `💔 创业失败\n💡 积累了宝贵经验\n🎓 继续专心学业`, false)
        }
        break
      // 新经济系统住房事件处理
      case 'buyHouse':
        if (option.housingData) {
          const { schoolTier } = option.housingData
          const regionType = this.worldState.regionType
          const unitPrice = REGION_UNIT_PRICE[regionType] || 25000
          const area = 80
          const multiplier = schoolTier === 'avg' ? SCHOOL_ZONE_PREMIUM : 
                            schoolTier === 'good' ? SCHOOL_ZONE_PREMIUM * 1.4 : 1.0
          const totalPrice = Math.round(unitPrice * area * multiplier)
          
          // 使用住房系统的购买逻辑
          const result = buyHouse(this, regionType, area, schoolTier !== 'none')
          if (result.ok) {
            person.psyche = Math.min(100, (person.psyche || 50) + 3)
            
            // 清除结婚住房选择标记
            if (person.flags?.needHousingAfterMarriage) {
              delete person.flags.needHousingAfterMarriage
            }
            
            this.showEventResult(person, '购房成功', 
              `🏠 成功购买住房！\n📍 位置：${this.worldState.cityName}\n🎓 学区等级：${schoolTier}\n💰 总价：${Math.round(totalPrice/10000)}万元\n🏦 开始月供生活`, true)
          } else {
            this.showEventResult(person, '购房失败', result.reason, false)
          }
        }
        break
        
      case 'rentHouse':
        if (option.housingData) {
          const { schoolTier } = option.housingData
          const regionType = this.worldState.regionType
          
          // 使用住房系统的租房逻辑
          setupRent(this, regionType, 80)
          
          // 更新学区信息
          this.familyAssets.housing.schoolTier = schoolTier
          
          person.psyche = Math.max(0, (person.psyche || 50) - 1)
          
          // 清除结婚住房选择标记
          if (person.flags?.needHousingAfterMarriage) {
            delete person.flags.needHousingAfterMarriage
          }
          
          const rentBase = REGION_RENT_BASE[regionType] || 2400
          const multiplier = schoolTier === 'avg' ? 1.3 : 1.0
          const yearlyRent = Math.round(rentBase * 12 * multiplier)
          
          this.showEventResult(person, '租房成功', 
            `🏠 成功租赁住房！\n📍 位置：${this.worldState.cityName}\n🎓 学区等级：${schoolTier}\n💰 年租金：${yearlyRent.toLocaleString()}元`, true)
        }
        break
        
      case 'relocateToMega':
        this.worldState.regionType = 'mega'
        this.worldState.cityName = getRandomCity('mega')
        // 迁居后需要重新安排住房
        if (this.familyAssets.housing.mode !== 'none') {
          this.familyAssets.housing.regionType = 'mega'
          this.familyAssets.housing.cityName = this.worldState.cityName
          // 房价重新计算
          this.familyAssets.housing.currentPrice = calculateHousePrice('mega', this.familyAssets.housing.schoolTier, 1.0)
        }
        this.persons.forEach(p => {
          p.strain = Math.min(100, (p.strain || 50) + 10)
        })
        this.showEventResult(person, '城市迁移', 
          `🌆 成功迁移到${this.worldState.cityName}！\n💼 收入机会增加，生活成本上升\n📈 全家压力+10`, true)
        break
        
      case 'relocateToStable':
        const relocateTargetRegion = option.targetRegion || 'city'
        this.worldState.regionType = relocateTargetRegion
        this.worldState.cityName = getRandomCity(relocateTargetRegion)
        if (this.familyAssets.housing.mode !== 'none') {
          this.familyAssets.housing.regionType = relocateTargetRegion
          this.familyAssets.housing.cityName = this.worldState.cityName
          this.familyAssets.housing.currentPrice = calculateHousePrice(relocateTargetRegion, this.familyAssets.housing.schoolTier, 1.0)
        }
        this.persons.forEach(p => {
          p.strain = Math.max(0, (p.strain || 50) - 5)
          p.psyche = Math.min(100, (p.psyche || 50) + 3)
        })
        this.showEventResult(person, '城市迁移', 
          `🏡 成功迁移到${this.worldState.cityName}！\n😌 生活压力降低，追求稳定发展\n📈 全家压力-5，心理健康+3`, true)
        break
        
      case 'upgradeSchoolTier':
        if (option.targetTier) {
          const housing = this.familyAssets.housing
          housing.schoolTier = option.targetTier
          housing.currentPrice = calculateHousePrice(housing.regionType, option.targetTier, housing.priceIndex)
          this.showEventResult(person, '学区升级', 
            `🎓 学区升级成功！\n📚 新学区等级：${option.targetTier}\n👶 有利于子女教育发展`, true)
        }
        break
        
      case 'downgradeSchoolTier':
        if (option.targetTier !== undefined) {
          const housing = this.familyAssets.housing
          housing.schoolTier = option.targetTier
          housing.currentPrice = calculateHousePrice(housing.regionType, option.targetTier, housing.priceIndex)
          if (option.cashBack) {
            this.globalEconomy += option.cashBack
          }
          this.showEventResult(person, '学区调整', 
            `💰 学区调整完成！\n💵 获得现金：${option.cashBack?.toLocaleString() || 0}元\n📚 学区等级调整为：${option.targetTier}`, true)
        }
        break
        
      case 'investmentProperty':
        // 简化处理：增加年度被动收入
        person.passiveIncome = (person.passiveIncome || 0) + Math.round(option.cost * 0.03) // 3%年收益
        this.showEventResult(person, '投资房产', 
          `🏢 投资房产成功！\n💰 预期年租金收益：${Math.round(option.cost * 0.03).toLocaleString()}元\n📈 增加被动收入来源`, true)
        break
        
      case 'upgradeRentToBuy':
        // 租转买
        const regionType2 = this.worldState.regionType
        const result2 = buyHouse(this, regionType2, 80, false)
        if (result2.ok) {
          this.showEventResult(person, '租转买成功', 
            `🏠 成功从租房转为购房！\n💰 告别房租，开始月供\n📈 房产资产增加`, true)
        } else {
          this.showEventResult(person, '租转买失败', result2.reason, false)
        }
        break
        
      case 'upgradeArea':
        // 面积升级
        if (this.familyAssets.housing.mode === 'own') {
          this.familyAssets.housing.area = Math.min(150, (this.familyAssets.housing.area || 80) + 30)
          this.showEventResult(person, '房屋扩容', 
            `🏠 成功升级到更大面积住房！\n📐 新面积：${this.familyAssets.housing.area}平米\n😌 居住体验显著提升`, true)
        }
        break
        
      // 就业异地迁移处理
      case 'job_relocate_self':
        // 已在上一步把 person.region 改到工作城市；家庭不动，仅提示
        this.showEventResult(person, '异地', '你选择先异地工作（心理-1 压力+2）', true)
        break
        
      case 'job_relocate_family':
        // 触发家庭迁移流程
        const jobTargetRegion = option.targetRegion || (this.familyAssets?.housing?.regionType || 'city')
        try {
          proposeFamilyMove(this, '工作机会', jobTargetRegion)
        } catch (error) {
          console.error('家庭迁移失败:', error)
        }
        break
        
      case 'job_relocate_decline':
        person.occupation = null
        person.jobSeeking = true
        this.showEventResult(person, '选择', '你放弃了异地机会，继续寻找本地岗位', false)
        break
        
      // 家庭迁移执行
      case 'move_rent':
      case 'move_sell':
      case 'move_bridge':
      case 'move_cancel':
        const moveTarget = option.target // region
        try {
          applyFamilyMove(this, special, moveTarget)
        } catch (error) {
          console.error('家庭迁移应用失败:', error)
        }
        if (special === 'move_cancel'){
          this.showEventResult(person,'迁移','已取消本次迁移', false)
        } else {
          this.showEventResult(person,'迁移','家庭居住地已更新/设置', true)
        }
        break
        
      // 迁移相关事件处理
      case 'mig_return':
        const currentRegion = this.familyAssets?.housing?.regionType || this.familyAssets?.housing?.region || 'city'
        const targetReturn = suggestTargetRegion(currentRegion, 'return') || currentRegion
        try {
          proposeFamilyMove(this, '养老回流', targetReturn)
        } catch (error) {
          console.error('养老回流迁移失败:', error)
        }
        break
        
      case 'mig_cost_consider':
        const current2 = this.familyAssets?.housing?.regionType || this.familyAssets?.housing?.region || 'city'
        // 反向选择成本更低一级的地区
        const map = { mega:'city', city:'county', county:'rural', rural:'rural' }
        const targetCost = map[current2] || current2
        try {
          proposeFamilyMove(this, '生活成本压力', targetCost)
        } catch (error) {
          console.error('成本压力迁移失败:', error)
        }
        break
        
      // 弹性退休系统
      case 'retire_early_confirm':
        // 提前退休：立刻退休，养老金按年龄折减（60岁前最多-20%）
        const age = person.age
        const k = Math.max(0.8, 1 - Math.max(0, (60 - age))*0.04) // 60→1.0, 55→0.8
        const pensionRegion = this.familyAssets?.housing?.regionType || this.familyAssets?.housing?.region || 'city'
        const pensionBase = PENSION.base * (PENSION.regionK[pensionRegion]||1)
        person.isRetired = true
        person.income = Math.round(Math.min(PENSION.cap, Math.max(PENSION.floor, pensionBase*k)))
        person.workYears = 0
        this.showEventResult(person, '提前退休',
          `从今年起领取养老金：${person.income.toLocaleString()} 元/年（系数×${k.toFixed(2)}）`, true)
        break
        
      case 'retire_phased':
        if (!person.flags) person.flags = {}
        person.flags.phasedRetire = true
        this.showEventResult(person, '渐进退休', '已切换到半工时模式，压力减轻', true)
        break
        
      case 'rehire_accept':
        if (!person.flags) person.flags = {}
        person.flags.rehired = true
        this.showEventResult(person, '返聘', '接受返聘，将获得额外收入补贴', true)
        break
        
      // 老年健康事件处理（新增）
      case 'chronic_active':
        if (!person.flags) person.flags = {}
        person.flags.chronicCare = 'active'
        this.showEventResult(person, '慢性疾病', 
          `📋 选择积极治疗方案\n🏥 定期复查和用药\n💪 生活质量相对较好\n💰 医疗费用较高`, true)
        break
        
      case 'chronic_conservative':
        if (!person.flags) person.flags = {}
        person.flags.chronicCare = 'conservative'
        this.showEventResult(person, '慢性疾病', 
          `🏠 选择保守治疗\n💊 基础药物控制\n😌 减少医疗负担\n⚠️ 病情进展相对较快`, true)
        break
        
      case 'fracture_surgery':
        if (!person.flags) person.flags = {}
        person.flags.fractureStatus = 'surgery'
        this.showEventResult(person, '骨折治疗', 
          `🏥 手术治疗完成\n🦴 骨折修复良好\n🚶 恢复期需要康复训练\n💰 医疗费用较高但效果好`, true)
        break
        
      case 'fracture_conservative':
        if (!person.flags) person.flags = {}
        person.flags.fractureStatus = 'conservative'
        this.showEventResult(person, '骨折治疗', 
          `🛏️ 选择保守治疗\n⏰ 恢复时间较长\n😔 可能留下功能障碍\n💸 费用相对较低`, false)
        break
        
      case 'hospice_home':
        if (!person.flags) person.flags = {}
        person.flags.hospiceCare = 'home'
        person.strain = Math.max(0, (person.strain || 50) - 10)
        this.showEventResult(person, '安宁疗护', 
          `🏠 选择居家安宁疗护\n👨‍👩‍👧‍👦 家人陪伴\n😌 在熟悉环境中度过\n💕 心理慰藉效果最佳`, true)
        break
        
      case 'hospice_hospital':
        if (!person.flags) person.flags = {}
        person.flags.hospiceCare = 'hospital'
        this.showEventResult(person, '安宁疗护', 
          `🏥 选择医院安宁疗护\n👨‍⚕️ 专业医护团队\n💊 症状控制较好\n🩺 医疗保障充分`, true)
        break
        
      case 'hospice_basic':
        if (!person.flags) person.flags = {}
        person.flags.hospiceCare = 'basic'
        this.showEventResult(person, '安宁疗护', 
          `🏠 选择基础护理\n💰 费用可控\n😐 护理水平有限\n😔 心理支持不足`, false)
        break
        
      // 退休相关的case已删除，现在自动处理
    }
    
    // 企业家增长逻辑已移到 advanceYear()
  },
  
  // 创建伴侣
  createPartner(person, partnerData) {
    const partner = {
      id: this.generateId(),
      name: this.generateRandomName(),
      age: person.age + Math.floor((Math.random() - 0.5) * 6),
      gender: person.gender === '男' ? '女' : '男',
      health: partnerData.health,
      charm: partnerData.charm,
      intelligence: partnerData.intelligence,
      // 新增属性
      stability: this.generateNormalDistribution(50, 15),
      motivation: this.generateNormalDistribution(50, 15),
      creativity: this.generateNormalDistribution(50, 15),
      stress: 0,
      cumStudyHours: 0,
      satisfaction: 50,
      // 新经济系统属性
      psyche: 50, // 心理健康
      strain: 30, // 生活压力
      competitiveness: 0, // 竞争力（自动计算）
      // 原有属性
      economicContribution: 0,
      income: Math.floor(Math.random() * 80000) + 40000,
      isAlive: true,
      partner: person,
      children: [],
      occupation: ['工人', '白领', '国企员工'][Math.floor(Math.random() * 3)],
      education: '大学',
      schoolLevel: ['双非', '二本'][Math.floor(Math.random() * 2)], // 随机学历档次
      major: null, // 专业
      workYears: Math.floor(Math.random() * 5) + 1, // 工作年限1-5年
      jobSeeking: false, // 是否在找工作
      lastPromotionYear: 0, // 上次升职年份
      isRetired: false, // 是否退休
      flags: {}
    }
    
    person.partner = partner
    this.persons.push(partner)
    
    // 设置结婚年份标记，用于生育事件触发
    if (!person.flags) person.flags = {}
    if (!partner.flags) partner.flags = {}
    person.flags.marriageYear = this.currentYear
    partner.flags.marriageYear = this.currentYear
    
    // 结婚后自动触发住房选择
    if (this.familyAssets.housing.mode === 'none') {
      person.flags.needHousingAfterMarriage = true
    }
    
    uni.showToast({
      title: `${person.name}结婚了！`,
      icon: 'success'
    })
  },
  
  // 获取高考选项（基于智力）
  getGaoKaoOptions(person) {
    const intelligence = person.intelligence
    const options = []
    
    // 二本（智力要求低）
    options.push({
      text: '二本大学',
      cost: 40000,
      effects: { intelligence: 2 },
      special: 'college2'
    })
    
    // 双非一本
    if (intelligence >= 60) {
      options.push({
        text: '双非一本',
        cost: 20000,
        effects: { intelligence: 4 },
        special: 'college1'
      })
    }
    
    // 211
    if (intelligence >= 75) {
      options.push({
        text: '211大学',
        cost: 5000,
        effects: { intelligence: 6, charm: 1 },
        special: 'college211'
      })
    }
    
    // 985
    if (intelligence >= 85) {
      options.push({
        text: '985大学',
        cost: 5000,
        effects: { intelligence: 8, charm: 2 },
        special: 'college985'
      })
    }
    
    // 艺术院校（基于魅力）
    if (person.charm >= 70) {
      options.push({
        text: '艺术院校',
        cost: 80000,
        effects: { charm: 5, intelligence: 2 },
        special: 'artCollege'
      })
    }
    
    // 直接工作
    options.push({
      text: '不上大学，直接工作',
      cost: 0,
      effects: { occupation: '工人' },
      special: 'noCollege'
    })
    
    return options
  },
  
  // 获取工作选项（基于教育和智力）
  getJobOptions(person) {
    const options = []
    const intelligence = person.intelligence
    const education = person.education || '高中'
    
    // 基础工作
    options.push({
      text: '进工厂',
      cost: 0,
      effects: { occupation: '工人' },
      special: 'factory'
    })
    
    // 需要一定智力的工作
    if (intelligence >= 60 || education.includes('大学')) {
      options.push({
        text: '国企',
        cost: 0,
        effects: { occupation: '国企员工', health: 1, charm: -1 },
        special: 'stateEnterprise'
      })
      
      options.push({
        text: '互联网大厂',
        cost: 0,
        effects: { occupation: '程序员', health: -2 },
        special: 'bigTech'
      })
    }
    
    // 高智力或985/211背景
    if (intelligence >= 80 || education.includes('985') || education.includes('211')) {
      options.push({
        text: '公务员',
        cost: 20000, // 考试培训费
        effects: { occupation: '公务员', health: 1, charm: 1 },
        special: 'civilServant'
      })
    }
    
    // 创业选项
    if (intelligence >= 70 && person.charm >= 60) {
      options.push({
        text: '创业',
        cost: 100000,
        effects: { occupation: '创业者' },
        special: 'startup'
      })
    }
    
    return options
  },
  
  // 获取婚恋选项（基于魅力）
  getMarriageOptions(person) {
    const charm = person.charm
    const options = []
    
    // 根据魅力值生成3个候选伴侣
    for (let i = 0; i < 3; i++) {
      const partnerCharm = Math.max(30, Math.min(100, charm + (Math.random() - 0.5) * 30))
      const partnerIntelligence = Math.floor(Math.random() * 40) + 60
      const partnerHealth = Math.floor(Math.random() * 30) + 70
      
      options.push({
        text: `候选${i + 1}: ${this.generateRandomName()} (魅力${Math.floor(partnerCharm)})`,
        cost: Math.floor(Math.random() * 150000) + 50000, // 婚礼费用5-20万
        effects: {},
        special: 'marry',
        partnerData: {
          charm: Math.floor(partnerCharm),
          intelligence: Math.floor(partnerIntelligence),
          health: Math.floor(partnerHealth)
        }
      })
    }
    
    options.push({
      text: '暂不结婚',
      cost: 0,
      effects: {},
      special: 'single'
    })
    
    return options
  },
  
  // 创建婴儿
  createBaby(parent, count) {
    for (let i = 0; i < count; i++) {
      const partner = parent.partner
      if (!partner) continue
      
      const baby = {
        id: this.generateId(),
        name: this.generateRandomName(),
        age: 0,
        gender: Math.random() > 0.5 ? '男' : '女',
        health: this.generateBabyAttribute(parent.health, partner.health),
        charm: this.generateBabyAttribute(parent.charm, partner.charm),
        intelligence: this.generateBabyAttribute(parent.intelligence, partner.intelligence),
        // 新增属性
        stability: this.generateBabyAttribute(parent.stability || 50, partner.stability || 50),
        motivation: this.generateBabyAttribute(parent.motivation || 50, partner.motivation || 50),
        creativity: this.generateBabyAttribute(parent.creativity || 50, partner.creativity || 50),
        stress: 0,
        cumStudyHours: 0,
        satisfaction: 50,
        // 新经济系统属性
        psyche: 60, // 婴儿心理健康较好
        strain: 0, // 婴儿无压力
        competitiveness: 0,
        ambition: this.generateBabyAttribute(parent.ambition || 50, partner.ambition || 50),
        // 求职偏好初始为0
        prefGov: 0,
        prefCorp: 0,
        prefStartup: 0,
        // 原有属性
        economicContribution: 0,
        income: 0,
        isAlive: true,
        partner: null,
        children: [],
        occupation: null,
        education: '未入学',
        schoolLevel: null,
        major: null,
        workYears: 0,
        jobSeeking: false,
        lastPromotionYear: 0,
        isRetired: false,
        parents: [parent, partner],
        flags: {
          internTier: 0,
          researchTier: 0,
          leaderTier: 0,
          jobFailCount: 0
        }
      }
      
      // 确保属性在合理范围内
      baby.health = Math.max(60, Math.min(100, baby.health))
      baby.charm = Math.max(60, Math.min(100, baby.charm))
      baby.intelligence = Math.max(60, Math.min(100, baby.intelligence))
      baby.stability = Math.max(30, Math.min(100, baby.stability))
      baby.motivation = Math.max(30, Math.min(100, baby.motivation))
      baby.creativity = Math.max(30, Math.min(100, baby.creativity))
      
      // 添加到父母的孩子列表
      parent.children.push(baby)
      partner.children.push(baby)
      
      // 添加到游戏人物列表
      this.persons.push(baby)
      
      uni.showToast({
        title: `${parent.name}生了个${baby.gender}孩子！`,
        icon: 'success'
      })
    }
    
    // 子女抚养费系统已删除
  },
  
  // 检查生命终结
  checkLifeEnd(person) {
    if (person.health <= 0) {
      person.isAlive = false
    }
  },
  
  
  // 检查年度死亡概率
  checkMortality(person) {
    if (!person.isAlive) return
    const age = person.age
    const h = person.health
    // 现有：健康<=0 直接死亡
    if (h <= 0) { 
      person.isAlive = false
      this.handleDeath(person, 'health_zero')
      return 
    }
    // 新增：按年龄×健康修正概率死亡
    const pAge = MORTALITY.baseAge(age)
    const pH   = MORTALITY.healthFactor(h)
    const pAcc = MORTALITY.accident || 0
    const pYear = pAge * pH + pAcc
    if (Math.random() < pYear){
      person.isAlive = false
      const cause = (Math.random() < pAcc/(pYear+1e-9)) ? 'accident' : 'natural'
      this.handleDeath(person, cause)
    }
  },

  // 处理死亡：现金流、心理打击、家族延续
  handleDeath(person, cause = 'natural') {
    if (!person) return
    try {
      // 1) 丧葬支出（取家庭居住地域）
      const region = this.familyAssets?.housing?.regionType || this.familyAssets?.housing?.region || 'city'
      const funeral = FUNERAL_COST?.[region] || 20000
      this.globalEconomy = (this.globalEconomy || 0) - funeral

      // 2) 家人心理影响（伴侣/子女）
      const impact = { psycheDrop: cause==='accident' ? 12 : 8, strainUp: cause==='accident' ? 6 : 4 }
      this.persons.forEach(p => {
        if (!p.isAlive) return
        if (p.partner && p.partner.id === person.id){
          p.psyche = Math.max(0, (p.psyche||50) - impact.psycheDrop)
          p.strain = Math.min(100, (p.strain||10) + impact.strainUp)
          p.partner = null
        }
        if ((p.parents||[]).some(pp=>pp.id===person.id)){
          p.psyche = Math.max(0, (p.psyche||50) - Math.floor(impact.psycheDrop*0.6))
          p.strain = Math.min(100, (p.strain||10) + Math.floor(impact.strainUp*0.5))
        }
      })

      // 3) 处理遗嘱：你已有"立遗嘱"事件，若 person.flags.will === 'inheritHouseToChild' 等，可在此兑现
      if (person.flags?.will==='inheritHouseToChild'){
        // 家庭资产是公有模型，默认不拆分；可做一个"给长子教育基金"象征性转账
        const grant = 20000
        this.globalEconomy -= grant
        const heir = (person.children||[])[0]
        if (heir){ 
          if (!heir.flags) heir.flags = {}
          heir.flags.eduGrant = (heir.flags?.eduGrant||0) + grant 
        }
      }

      // 4) 移除（或保留在 persons 标记 isAlive=false）
      person.isAlive = false
      person.occupation = null
      person.income = 0

      // 5) 弹窗
      this.showEventResult(person, '讣告',
        `🕯️ ${person.name || '未知'}（${person.age || 0}岁）已离世。\n`+
        `原因：${cause==='accident'?'意外':'自然'}。\n`+
        `丧葬支出：${funeral.toLocaleString()} 元。`, false)
    } catch (error) {
      console.error('处理死亡失败:', error)
      // 即使出错也要确保人物死亡状态
      if (person) person.isAlive = false
    }
  },

  // 检查房贷违约风险
  checkMortgageArrears() {
    const housing = this.familyAssets?.housing
    if (!housing || housing.mode !== 'own' || !housing.mortgage) return
    
    const arrears = housing.mortgage.arrears || 0
    if (arrears >= 3) { // 连续3年逾期触发法拍
      this.triggerForeclosure()
    } else if (arrears >= 1) {
      // 逾期1-2年给出警告
      const mainPerson = this.persons.find(p => p.isAlive) || {}
      this.showEventResult(mainPerson, '房贷逾期警告', 
        `⚠️ 房贷已逾期${arrears}年\n💳 请尽快缴清欠款\n🏠 连续逾期3年将面临法拍风险\n📞 建议联系银行协商还款计划`, false)
    }
  },

  // 触发房屋法拍
  triggerForeclosure() {
    const housing = this.familyAssets.housing
    const mainPerson = this.persons.find(p => p.isAlive) || {}
    
    // 法拍价格通常为市场价70-85%
    const currentMarketPrice = housing.price || housing.currentPrice || 2000000
    const foreclosurePrice = Math.round(currentMarketPrice * (0.70 + Math.random() * 0.15))
    const remainingDebt = (housing.mortgage?.principal || 0) * ((housing.mortgage?.years || 25) / (MORTGAGE_YEARS || 25))
    const netProceeds = Math.max(0, foreclosurePrice - remainingDebt)
    
    // 房屋被收回，获得净收益（如果有的话）
    this.globalEconomy += netProceeds
    
    // 重置住房状态
    this.familyAssets.housing = {
      mode: 'none',
      regionType: housing.regionType,
      cityName: housing.cityName,
      schoolTier: 'none',
      area: 80,
      buyYear: 0,
      currentPrice: 0,
      priceIndex: 1.0
    }
    
    // 对所有家庭成员造成心理冲击
    this.persons.forEach(p => {
      if (p.isAlive) {
        p.psyche = Math.max(0, (p.psyche || 50) - 15)
        p.strain = Math.min(100, (p.strain || 50) + 20)
      }
    })
    
    this.showEventResult(mainPerson, '房屋法拍', 
      `🏠 房屋因连续逾期被法院拍卖\n💰 拍卖价：${Math.round(foreclosurePrice/10000)}万元\n💵 净得：${Math.round(netProceeds/10000)}万元\n😰 全家心理健康-15，压力+20\n🏘️ 需要重新安排住房`, false)
  },

  // 检查破产
  checkBankruptcy() {
    if (this.globalEconomy <= -300000) { // 负债30万破产
      // 如果有学区房，提供出售选项
      if (this.hasSchoolDistrictHouse()) {
        const sellPrice = this.sellSchoolDistrictHouse()
        this.globalEconomy += sellPrice
        
        uni.showModal({
          title: '紧急出售资产',
          content: `家庭财务危机！\n学区房已紧急出售，获得${sellPrice.toLocaleString()}元现金。\n当前资产：${this.globalEconomy.toLocaleString()}元`,
          showCancel: false,
          confirmText: '继续游戏'
        })
        
        // 出售后重新检查破产状态
        if (this.globalEconomy <= -300000) {
          this.triggerBankruptcy()
        }
      } else {
        this.triggerBankruptcy()
      }
    }
  },
  
  // 检查游戏结束条件
  checkGameOver() {
    const alivePersons = this.persons.filter(p => p.isAlive)
    
    if (alivePersons.length === 0 && !this.isGameOver) {
      // 所有人都死亡
      this.isGameOver = true
      this.gameOverReason = '所有家族成员都已离世'
      this.showGameOverScreen()
    }
  },
  
  // 触发破产
  triggerBankruptcy() {
    this.isGameOver = true
    this.gameOverReason = `家庭负债${Math.abs(this.globalEconomy).toLocaleString()}元，宣告破产！`
    this.showGameOverScreen()
  },
  
  // 显示游戏结束屏幕
  showGameOverScreen() {
    this.isPaused = true
    
    if (this.gameTimer) {
      clearInterval(this.gameTimer)
    }
    
    // 计算统计信息
    const maxWealth = Math.max(this.globalEconomy, this.getHistoricalMaxWealth())
    const totalPersons = this.persons.length
    const survivedPersons = this.persons.filter(p => p.isAlive).length
    
    const statsText = `游戏时长：${this.currentYear}年\n最高资产：${maxWealth.toLocaleString()}元\n家族成员：${totalPersons}人\n幸存人数：${survivedPersons}人`
    
    uni.showModal({
      title: '🎮 游戏结束',
      content: `${this.gameOverReason}\n\n📊 游戏统计\n${statsText}`,
      showCancel: false,
      confirmText: '再来一局',
      success: (res) => {
        if (res.confirm) {
          this.restartGame()
        }
      }
    })
  },
  
  // 获取历史最高财富值（简化版本，实际应该在每年更新时记录）
  getHistoricalMaxWealth() {
    return Math.max(this.globalEconomy, 500000) // 至少返回初始财富
  },
  
  // 重新开始游戏
  restartGame() {
    if (this.gameTimer) {
      clearInterval(this.gameTimer)
    }
    this.isGameStarted = false
    this.isGameOver = false
    this.gameOverReason = ''
    this.currentYear = 0
    this.globalEconomy = 0
    this.persons = []
    this.isPaused = false
    this.isEventActive = false
    this.currentEvent = null
    
    // 重置家族资产
    this.familyAssets = {
      schoolDistrictHouse: {
        owned: false,
        purchasePrice: 0,
        purchaseYear: 0
      },
      housing: {
        mode: 'none',
        regionType: 'city',
        cityName: '合肥',
        schoolTier: 'none',
        buyYear: 0,
        currentPrice: 0,
        priceIndex: 1.0
      }
    }
    
    // 重置世界状态
    this.worldState = {
      regionType: 'city',
      cityName: getRandomCity('city'),
      economicCycle: 1.0,
      useNewEconomics: true
    }
    
    // 重新初始化
    this.initGame()
  },
  

  // 新事件系统 v2.0 核心处理方法
  checkNewEventSystem(person) {
    
    const regionType = this.worldState.regionType || 'city'
    const candidates = []
    
    // 扫描所有事件池中的事件
    EVENT_POOL.forEach(event => {
      // 检查受众和年龄限制
      if (!fitsAudience(event, person) || !fitsAge(event, person)) return
      
      // 检查触发条件
      if (!event.when(person, this)) return
      
      // 检查冷却时间
      const lastTrigger = this.eventCooldowns[event.id] || 0
      if (this.currentYear - lastTrigger < event.cooldownYears) return
      
      // 计算修正后概率
      const baseProb = EVENT_BASE_PROBABILITIES[event.id] || 0.1
      const adjustedProb = applyAdjustments(event.id, baseProb, person, this, regionType)
      
      candidates.push({
        event: event,
        probability: adjustedProb
      })
    })
    
    // 按重要性分组处理
    const majorCandidates = candidates.filter(c => c.event.importance === 'major')
    const normalCandidates = candidates.filter(c => c.event.importance === 'normal')
    
    // 限流：同年最多1个重要事件 + 2个普通事件
    if (this.yearlyEventCount.major < 1 && majorCandidates.length > 0) {
      this.processCandidates(majorCandidates, person, 'major')
    }
    
    if (this.yearlyEventCount.normal < 2 && normalCandidates.length > 0) {
      this.processCandidates(normalCandidates, person, 'normal')
    }
  },
  
  // 处理候选事件
  processCandidates(candidates, person, importance) {
    // 简单抽取：按概率随机选择一个
    for (const candidate of candidates) {
      if (Math.random() < candidate.probability) {
        this.triggerNewEvent(candidate.event, person)
        this.yearlyEventCount[importance]++
        break // 每次只触发一个
      }
    }
  },
  
  // 触发新事件
  triggerNewEvent(event, person) {
    // 记录冷却时间
    this.eventCooldowns[event.id] = this.currentYear
    
    // 设置当前事件状态
    this.currentEvent = {
      person: person,
      type: event.title,
      eventData: event, // 保存完整事件数据
      options: event.choices.map(choice => ({
        text: choice.text,
        effects: choice.effects,
        special: choice.special || null
      }))
    }
    this.isEventActive = true
    
    // 根据UI类型显示不同界面
    if (event.ui === 'modal') {
      this.showEventModal(event, person)
    } else {
      this.showEventSheet(event, person)
    }
  },
  
  // 显示重要事件模态框
  showEventModal(event, person) {
    // 暂停游戏
    this.isPaused = true
    
    // 显示模态框 (uni.showModal 只能显示确认/取消，需要自定义处理)
    uni.showModal({
      title: `${event.icon} ${event.title}`,
      content: `${person.name}\n\n${event.text}\n\n请在游戏界面选择具体选项`,
      showCancel: false,
      confirmText: '查看选项',
      success: () => {
        // 用户点击确认后，事件选择界面已经显示
        // 这里不需要额外处理，因为 currentEvent 已经设置
      }
    })
  },
  
  // 显示普通事件底部弹层
  showEventSheet(event, person) {
    // 对于普通事件，直接显示在 EventModal 组件中
    // 不暂停游戏，允许用户稍后处理
    console.log(`普通事件触发: ${event.title} for ${person.name}`)
  },
  
  // 暂停/继续游戏
  togglePause() {
    this.isPaused = !this.isPaused
  },
  
  // 生成随机姓名
  generateRandomName() {
    const surnames = ['张', '李', '王', '刘', '陈', '杨', '赵', '黄', '周', '吴']
    const names = ['伟', '芳', '娜', '敏', '静', '秀', '丽', '强', '磊', '军', '洁', '勇', '艳', '杰', '娟']
    const surname = surnames[Math.floor(Math.random() * surnames.length)]
    const name = names[Math.floor(Math.random() * names.length)]
    return surname + name
  },
  
  // 生成唯一ID
  generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substring(2)
  },
  
  // 保存游戏到云端
  async saveToCloud(saveName = null) {
    try {
      const gameData = {
        saveName: saveName || `存档_${this.currentYear}年`,
        currentYear: this.currentYear,
        globalEconomy: this.globalEconomy,
        persons: this.persons
      }
      
      const result = await uniCloud.callFunction({
        name: 'game-save',
        data: {
          action: 'save',
          data: gameData
        }
      })
      
      if (result.result.success) {
        uni.showToast({
          title: '保存成功',
          icon: 'success'
        })
        return result.result
      } else {
        throw new Error(result.result.message)
      }
    } catch (error) {
      uni.showToast({
        title: '保存失败: ' + error.message,
        icon: 'none'
      })
      throw error
    }
  },
  
  // 从云端加载游戏
  async loadFromCloud(saveId) {
    try {
      const result = await uniCloud.callFunction({
        name: 'game-save',
        data: {
          action: 'load',
          data: { saveId }
        }
      })
      
      if (result.result.success) {
        const saveData = result.result.data
        this.currentYear = saveData.current_year
        this.globalEconomy = saveData.global_economy
        this.persons = saveData.persons
        this.isGameStarted = true
        this.startGameTimer()
        
        uni.showToast({
          title: '加载成功',
          icon: 'success'
        })
        return result.result
      } else {
        throw new Error(result.result.message)
      }
    } catch (error) {
      uni.showToast({
        title: '加载失败: ' + error.message,
        icon: 'none'
      })
      throw error
    }
  },
  
  // 获取存档列表
  async getSaveList() {
    try {
      const result = await uniCloud.callFunction({
        name: 'game-save',
        data: {
          action: 'list'
        }
      })
      
      if (result.result.success) {
        return result.result.data
      } else {
        throw new Error(result.result.message)
      }
    } catch (error) {
      uni.showToast({
        title: '获取存档失败: ' + error.message,
        icon: 'none'
      })
      throw error
    }
  },
  
  // 获取户主（家庭级事件的触发者）
  getHouseholdHead() {
    const alive = this.persons.filter(p => p.isAlive)
    const working = alive.filter(p => p.occupation)
    if (working.length) return working.sort((a,b) => b.age - a.age)[0]
    return alive.sort((a,b) => b.age - a.age)[0]
  },

  // 构建并入队当年随机事件
  buildAndQueueRandomEvents() {
    const regionType = this.worldState?.regionType || 'city'
    const majors = []
    const normals = []

    // 家庭级事件处理（只对户主触发一次）
    const head = this.getHouseholdHead()
    if (head) {
      const familyEligible = EVENT_POOL.filter(e => 
        FAMILY_LEVEL.has(e.id) &&
        fitsAudience(e, head) &&
        fitsAge(e, head) &&
        e.when(head, this) &&
        (!this.eventCooldowns[e.id] || this.currentYear - this.eventCooldowns[e.id] >= (e.cooldownYears || 1))
      )

      if (familyEligible.length) {
        const pick = familyEligible[Math.floor(Math.random() * familyEligible.length)]
        // 直接应用概率修正
        const baseProb = EVENT_BASE_PROBABILITIES[pick.id] || 0.1
        const adjustedProb = applyAdjustments(pick.id, baseProb, head, this, regionType)
        
        if (Math.random() < adjustedProb) {
          this.currentEventQueue.push({ key: pick.id, personId: head.id })
          this.eventCooldowns[pick.id] = this.currentYear
        }
      }
    }

    // 为每个活着的人，生成候选随机事件（排除家庭级事件）
    this.persons.filter(p => p.isAlive).forEach(person => {
      // 从 EVENT_POOL 里找满足 when 的，但排除家庭级事件
      const eligible = EVENT_POOL.filter(e => 
        e.when && 
        fitsAudience(e, person) &&
        fitsAge(e, person) &&
        e.when(person, this) && 
        !FAMILY_LEVEL.has(e.id)
      )

      // 计算修正后概率并抽样
      const sampled = eligible.filter(evt => {
        // 检查冷却时间
        const lastTrigger = this.eventCooldowns[evt.id] || 0
        if (this.currentYear - lastTrigger < (evt.cooldownYears || 1)) return false
        
        const baseProb = EVENT_BASE_PROBABILITIES[evt.id] || 0.1
        const p = applyAdjustments(evt.id, baseProb, person, this, regionType)
        return Math.random() < p
      })

      // 根据重要度分组
      sampled.forEach(evt => {
        const item = { key: evt.id, personId: person.id }
        if (evt.importance === 'major') majors.push(item)
        else normals.push(item)
      })
    })

    // 限流：1 个重要 + 2 个普通
    const picked = []
    if (majors.length > 0) {
      const randomMajor = majors[Math.floor(Math.random() * majors.length)]
      picked.push(randomMajor)
    }
    
    // 选择最多2个普通事件
    for (let i = 0; i < 2 && normals.length > 0; i++) {
      const randomIndex = Math.floor(Math.random() * normals.length)
      picked.push(normals.splice(randomIndex, 1)[0])
    }

    // 写入队列（去重：按 key+personId）
    const seen = new Set(this.currentEventQueue.map(e => e.key + '@' + e.personId))
    picked.forEach(e => {
      const sig = e.key + '@' + e.personId
      if (!seen.has(sig)) {
        this.currentEventQueue.push(e)
      }
    })
  },

  // 处理事件队列头部
  processEventQueueHead() {
    if (this.isEventActive) return // 已有事件阻塞判定
    if (this.pendingNormalEvent || this.isNormalSheetOpen) return
    if (this.currentEventQueue.length === 0) return

    const item = this.currentEventQueue.shift() // {key, personId}
    const person = this.persons.find(p => p.id === item.personId)
    if (!person || !person.isAlive) return

    const evt = EVENT_POOL.find(e => e.id === item.key)
    if (!evt) return

    // 标记冷却
    this.eventCooldowns[evt.id] = this.currentYear

    // 分重要度走不同 UI
    if (evt.importance === 'major') {
      // 重要事件：modal（阻塞）
      this.triggerMajorEvent(evt, person)
    } else {
      // 普通事件：交给 bottom-sheet
      this.triggerNormalEvent(evt, person)
    }
  },

  // 触发重要事件（使用Modal）
  triggerMajorEvent(evt, person) {
    this.isEventActive = true
    
    // 动态选项生成
    if (evt.dynamicChoices === "employment_offers") {
      this.handleEmploymentOffersEvent(evt, person)
      return
    }
    
    const primary = evt.choices[0]
    const secondary = evt.choices[1]
    
    uni.showModal({
      title: `${evt.icon || '🔴'} ${evt.title}`,
      content: `${person.name}\n\n${evt.text || ''}`,
      cancelText: secondary ? secondary.text : '取消',
      confirmText: primary ? primary.text : '确定',
      success: (res) => {
        const picked = res.confirm ? primary : secondary
        if (picked) {
          // 使用新的效果应用器
          this.applyNewEventEffects(person, picked.effects)
        }
        
        // 特殊处理高考事件
        if (evt.id === 'hs_gaokao') {
          this.handleGaokaoResult(person)
        }
        
        this.isEventActive = false
        // 继续处理队列
        setTimeout(() => this.processEventQueueHead(), 100)
      }
    })
  },

  // 触发普通事件（使用底部弹层）
  triggerNormalEvent(evt, person) {
    this.pendingNormalEvent = {
      ...evt,
      personId: person.id,
      personName: person.name
    }
    this.isNormalSheetOpen = true
  },

  // 处理普通事件选择
  handleNormalEventChoice(choiceIndex) {
    const evt = this.pendingNormalEvent
    if (!evt) return
    
    const person = this.persons.find(p => p.id === evt.personId)
    if (!person) return
    
    const choice = evt.choices[choiceIndex]
    if (choice) {
      // 使用新的效果应用器
      this.applyNewEventEffects(person, choice.effects)
      
      // 事件动作钩子
      if (choice?.meta?.action) {
        this.handleEventAction(choice.meta.action, {
          person,
          choice,
          event: evt
        })
      }
    }
    
    this.pendingNormalEvent = null
    this.isNormalSheetOpen = false
    
    // 继续处理队列
    setTimeout(() => this.processEventQueueHead(), 100)
  },

  // 关闭普通事件（未选择）
  closeNormalEvent() {
    this.pendingNormalEvent = null
    this.isNormalSheetOpen = false
    
    // 继续处理队列
    setTimeout(() => this.processEventQueueHead(), 100)
  },

  // 处理高考结果
  handleGaokaoResult(person) {
    try {
      const { score, percentile, tier } = calcGaokaoResult(person, this)
      
      // 落地：schoolLevel、education
      person.schoolLevel = tier
      person.education = tier + '大学'
      
      // 显示结果并进入专业选择
      uni.showModal({
        title: `🎓 高考结果：${tier}`,
        content: `模拟分数：${score}（约第${percentile}百分位）\n可选择${tier}院校专业。`,
        showCancel: false,
        confirmText: '选择专业',
        success: () => {
          // 生成专业选择事件
          const majorOptions = this.generateCollegeOptions(person)
          this.currentEvent = { 
            person, 
            type: '高考', 
            options: majorOptions 
          }
          this.isEventActive = true
        }
      })
    } catch (error) {
      console.error('高考结果处理失败:', error)
      // 降级处理
      person.schoolLevel = '二本'
      person.education = '二本大学'
    }
  },

  // 处理动态求职事件：生成个性化工作选择
  handleEmploymentOffersEvent(evt, person) {
    const regionType = this.worldState?.regionType || 'city'
    
    // 生成个性化求职选项
    const jobOffers = generateJobOffers(person, regionType, CAREERS)
    
    // 生成选择列表，包含成功率和薪资预期
    const dynamicChoices = jobOffers.map(jobName => {
      const successRate = calcJobSuccess(person, jobName, regionType, CAREERS)
      const expectedSalary = calcStartingSalary(person, jobName, regionType, CAREERS)
      
      return {
        text: `申请${jobName} (成功率${Math.round(successRate * 100)}%, 预期薪资${Math.round(expectedSalary/10000)}万)`,
        effects: {},
        meta: { 
          action: 'apply_offer',
          jobName,
          successRate,
          expectedSalary
        }
      }
    })
    
    // 添加"再考虑"选项
    dynamicChoices.push({
      text: '再考虑一下',
      effects: { psyche: -1, strain: +1 },
      meta: null
    })
    
    // 设置到当前事件并显示
    this.currentEvent = {
      person: person,
      type: evt.title,
      eventData: { ...evt, choices: dynamicChoices },
      options: dynamicChoices
    }
    
    // 显示事件详情（uni.showModal只能显示两个按钮，实际选择在UI组件中处理）
    uni.showModal({
      title: `${evt.icon} ${evt.title}`,
      content: `${person.name}\n\n根据你的履历，共生成${jobOffers.length}个求职机会\n请在界面中选择具体申请的岗位`,
      showCancel: false,
      confirmText: '查看选项',
      success: () => {
        // 选项已设置到currentEvent，UI组件会处理选择
      }
    })
  },

  // 事件动作钩子处理器
  handleEventAction(actionType, context) {
    const { person, choice } = context
    
    switch (actionType) {
      case 'buy_house_view': {
        // 住房购买决策：查看房源
        const regionType = this.worldState.regionType
        const schoolTiers = ['none', 'avg', 'good', 'top']
        
        let content = `🏠 ${this.worldState.cityName}地区房源：\n\n`
        schoolTiers.forEach(tier => {
          const price = calculateHousePrice(regionType, tier, 1.0)
          const tierName = { 'none': '无学区', 'avg': '普通学区', 'good': '优质学区', 'top': '顶级学区' }[tier]
          content += `${tierName}：${price.toLocaleString()}万元\n`
        })
        content += `\n当前家庭现金：${this.globalEconomy.toLocaleString()}元`
        
        this.showEventResult(person, '房源查看', content, true)
        break
      }
      
      case 'buy_house_contract': {
        // 购房合同签订：实际执行购买
        const housing = this.familyAssets.housing
        const targetTier = choice.meta.schoolTier || 'avg'
        const regionType = this.worldState.regionType
        const housePrice = calculateHousePrice(regionType, targetTier, 1.0)
        const downPayment = housePrice * 0.35 // 35%首付
        
        if (this.globalEconomy >= downPayment) {
          this.globalEconomy -= downPayment
          housing.mode = 'own'
          housing.regionType = regionType
          housing.cityName = this.worldState.cityName
          housing.schoolTier = targetTier
          housing.buyYear = this.currentYear
          housing.currentPrice = housePrice
          housing.priceIndex = 1.0
          housing.annualMortgage = annuityPayment(housePrice * 0.65, 0.046, 30) // 30年房贷
          
          person.psyche = Math.min(100, (person.psyche || 50) + 5)
          this.showEventResult(person, '购房成功', 
            `🎉 成功购买${housePrice.toLocaleString()}万元住房！\n🏦 年供：${housing.annualMortgage.toLocaleString()}元\n🎓 学区：${targetTier}`, true)
        } else {
          this.showEventResult(person, '购房失败', '资金不足，无法完成购房', false)
        }
        break
      }
      
      case 'rent_sign': {
        // 租房签约
        const housing = this.familyAssets.housing
        const targetTier = choice.meta.schoolTier || 'none'
        const regionType = this.worldState.regionType
        
        housing.mode = 'rent'
        housing.regionType = regionType
        housing.cityName = this.worldState.cityName
        housing.schoolTier = targetTier
        housing.buyYear = this.currentYear
        const baseRent = CFG.REGIONS[regionType].rentBase * (targetTier === 'top' ? 1.5 : targetTier === 'good' ? 1.2 : 1.0)
        housing.currentPrice = baseRent * 12 // 年租金
        
        person.psyche = Math.max(0, (person.psyche || 50) - 1)
        this.showEventResult(person, '租房成功', 
          `🏠 成功租赁住房\n💰 年租金：${housing.currentPrice.toLocaleString()}元`, true)
        break
      }
      
      case 'house_upgrade_init': {
        // 住房升级初始化
        person.flags.isSwitchingHouse = true
        const currentPrice = this.familyAssets.housing.currentPrice || 0
        this.showEventResult(person, '换房准备', 
          `🔄 开始换房流程\n💡 当前房产价值：${currentPrice.toLocaleString()}元\n⚠️ 需要协调买卖时间`, true)
        break
      }
      
      case 'house_chain_break': {
        // 换房断链处理
        if (person.flags.isSwitchingHouse) {
          delete person.flags.isSwitchingHouse
          const bridgeCost = rand(8000, 25000)
          this.globalEconomy -= bridgeCost
          person.strain = Math.min(100, (person.strain || 50) + 8)
          this.showEventResult(person, '断链处理', 
            `💸 支付过桥费用：${bridgeCost.toLocaleString()}元\n📈 压力增加，但换房继续`, false)
        }
        break
      }
      
      case 'marry_bind_partner': {
        // 结婚绑定伴侣：从候选人创建完整人物卡
        const partnerData = choice.meta.partnerCandidate
        if (partnerData && !person.partner) {
          this.createPartnerFromCandidate(person, partnerData)
        }
        break
      }
      
      case 'birth_try': {
        // 生育尝试
        if (person.partner) {
          const motherHealth = person.gender === '女' ? person.health : person.partner.health
          const fatherHealth = person.gender === '男' ? person.health : person.partner.health
          const avgHealth = (motherHealth + fatherHealth) / 2
          const successRate = Math.max(0.3, Math.min(0.9, avgHealth / 100))
          
          if (Math.random() < successRate) {
            this.createBaby(person, 1)
            if (person.gender === '女') person.health -= 3
            if (person.partner.gender === '女') person.partner.health -= 3
            this.showEventResult(person, '生育成功', 
              `👶 恭喜喜得贵子！\n💕 家庭人口增加\n🩺 产妇健康-3`, true)
          } else {
            person.psyche = Math.max(0, (person.psyche || 50) - 3)
            if (person.partner) person.partner.psyche = Math.max(0, (person.partner.psyche || 50) - 3)
            this.showEventResult(person, '生育暂缓', 
              `😔 这次尝试未成功\n💙 继续调养身体\n😟 心理健康-3`, false)
          }
        }
        break
      }
      
      case 'apply_offer': {
        // 求职申请：处理动态生成的工作申请
        const { jobName, successRate, expectedSalary } = choice.meta
        if (!jobName) return
        
        // 使用employment.js中的成功率计算（允许覆盖）
        const regionType = this.worldState?.regionType || 'city'
        const finalSuccessRate = successRate || calcJobSuccess(person, jobName, regionType, CAREERS)
        const finalSalary = expectedSalary || calcStartingSalary(person, jobName, regionType, CAREERS)
        
        if (Math.random() < finalSuccessRate) {
          // 求职成功
          person.occupation = jobName
          person.jobSeeking = false
          person.income = finalSalary
          person.workYears = 0
          person.satisfaction = 50
          person.psyche = Math.min(100, (person.psyche || 50) + 5)
          
          this.showEventResult(person, '求职成功', 
            `🎉 成功入职${jobName}！\n💰 年薪：${finalSalary.toLocaleString()}元\n📈 心理健康+5\n🚀 职业生涯开始！`, true)
        } else {
          // 求职失败
          person.flags.jobFailCount = (person.flags.jobFailCount || 0) + 1
          person.psyche = Math.max(0, (person.psyche || 50) - 3)
          person.strain = Math.min(100, (person.strain || 50) + 2)
          
          this.showEventResult(person, '求职失败', 
            `😔 ${jobName}求职失败\n💼 继续寻找工作机会\n😟 心理健康-3，压力+2\n💪 不要放弃，坚持就是胜利！`, false)
        }
        break
      }
      
      default:
        console.log(`未知的事件动作：${actionType}`)
        break
    }
  },

  // 从候选人数据创建完整伴侣人物卡
  createPartnerFromCandidate(person, candidateData) {
    const partner = {
      id: this.generateId(),
      name: candidateData.name || this.generateRandomName(),
      age: candidateData.age || (person.age + Math.floor((Math.random() - 0.5) * 6)),
      gender: person.gender === '男' ? '女' : '男',
      health: candidateData.health || this.generateNormalDistribution(50, 15),
      charm: candidateData.charm || this.generateNormalDistribution(50, 15),
      intelligence: candidateData.intelligence || this.generateNormalDistribution(50, 15),
      // 新增属性
      stability: this.generateNormalDistribution(50, 15),
      motivation: this.generateNormalDistribution(50, 15),
      creativity: this.generateNormalDistribution(50, 15),
      stress: 0,
      cumStudyHours: 0,
      satisfaction: 50,
      // 新经济系统属性
      psyche: 50, 
      strain: 30, 
      competitiveness: 0,
      ambition: this.generateNormalDistribution(50, 15),
      // 求职偏好 0-1 累积
      prefGov: 0,
      prefCorp: 0, 
      prefStartup: 0,
      // 原有属性
      economicContribution: 0,
      income: candidateData.income || (Math.floor(Math.random() * 80000) + 40000),
      isAlive: true,
      partner: person,
      children: [],
      occupation: candidateData.occupation || ['工人', '白领', '国企员工'][Math.floor(Math.random() * 3)],
      education: candidateData.education || '大学',
      schoolLevel: candidateData.schoolLevel || ['双非', '二本'][Math.floor(Math.random() * 2)],
      major: null,
      workYears: Math.floor(Math.random() * 5) + 1,
      jobSeeking: false,
      lastPromotionYear: 0,
      isRetired: false,
      flags: {
        internTier: Math.floor(Math.random() * 3), // 随机0-2实习经历
        researchTier: Math.floor(Math.random() * 2), // 随机0-1科研经历
        leaderTier: Math.floor(Math.random() * 2), // 随机0-1领导经历
        jobFailCount: 0
      }
    }
    
    person.partner = partner
    this.persons.push(partner)
    
    // 设置结婚年份标记
    if (!person.flags) person.flags = {}
    if (!partner.flags) partner.flags = {}
    person.flags.marriageYear = this.currentYear
    partner.flags.marriageYear = this.currentYear
    
    this.showEventResult(person, '喜结良缘', 
      `💕 ${person.name}与${partner.name}结婚了！\n💰 伴侣收入：${partner.income.toLocaleString()}元/年\n🎉 家庭人口增加`, true)
  },

})

// 计算属性
export const gameComputed = {
  // 活着的人数
  alivePersonsCount: computed(() => 
    gameStore.persons.filter(p => p.isAlive).length
  ),
  
  // 总经济贡献
  totalEconomicContribution: computed(() =>
    gameStore.persons
      .filter(p => p.isAlive)
      .reduce((sum, p) => sum + p.economicContribution, 0)
  )
}