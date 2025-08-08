import { reactive, computed } from 'vue'

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
  
  // 家族资产系统
  familyAssets: {
    schoolDistrictHouse: {
      owned: false,
      purchasePrice: 0,
      purchaseYear: 0
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
  
  // 初始化游戏
  initGame() {
    this.currentYear = 0
    this.globalEconomy = this.generateInitialWealth()
    this.persons = []
    this.createInitialPerson()
    this.isGameStarted = true
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
  
  // 高考算法：根据智力生成大学档次
  calculateGaokaoResult(intelligence, hasLove = false) {
    const mean = intelligence - 10
    const stdDev = hasLove ? 20 : 15 // 谈恋爱方差变大
    
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
    const career = CAREERS[jobName]
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
      flags: {}
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
  
  // 推进一年
  advanceYear() {
    this.currentYear++
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
        
        this.updatePersonEconomics(person)
        this.checkLifeEvents(person)
        this.checkLifeEnd(person)
      }
    })
    this.updateGlobalEconomy()
    
    // 检查破产
    this.checkBankruptcy()
    
    // 检查游戏结束条件
    this.checkGameOver()
  },
  
  // 更新个人经济贡献
  updatePersonEconomics(person) {
    let totalIncome = person.income || 0
    let expense = 0
    
    // 基础支出（正态分布+健康惩罚）
    if (person.age < 18) {
      // 未成年人：均值1.5万的正态分布
      expense = Math.max(5000, this.generateNormalDistributionForExpense(15000, 2250)) // 标准差为均值的15%
      if (person.health < 70) {
        expense += Math.pow(70 - person.health, 2) * 10
      }
    } else {
      // 成年人：均值2.8万的正态分布
      expense = Math.max(10000, this.generateNormalDistributionForExpense(28000, 4200)) // 标准差为均值的15%
      if (person.health < 70) {
        expense += Math.pow(70 - person.health, 2) * 10
      }
    }
    
    // 子女抚养费已删除
    
    // 70岁后每年自动损失健康
    if (person.age >= 70) {
      person.health = Math.max(0, person.health - 3)
    }
    
    // 全家族学区房增益（如果家族拥有学区房）
    if (this.hasSchoolDistrictHouse() && person.age < 18) {
      // 家族有学区房的未成年人每年获得智力加成
      person.intelligence = Math.min(100, person.intelligence + 1)
    }
    
    person.economicContribution = totalIncome - expense
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
  
  // 处理升职（自动触发）
  handlePromotion(person) {
    const promoteRate = this.calculatePromotionRate(person, person.occupation)
    const career = CAREERS[person.occupation]
    
    if (Math.random() < promoteRate) {
      const salaryIncrease = Math.floor((career.maxSalary - career.minSalary) * 0.1)
      const newSalary = person.income + salaryIncrease
      person.income = Math.min(newSalary, career.maxSalary)
      person.health = Math.max(0, person.health - 2)
      person.lastPromotionYear = this.currentYear
      
      this.showEventResult(person, '升职成功', 
        `恭喜升职！\n💰 薪资增加：${salaryIncrease.toLocaleString()}元\n💼 新薪资：${person.income.toLocaleString()}元/年\n⚠️ 健康-2（工作压力增加）`, true)
    } else {
      person.lastPromotionYear = this.currentYear
      this.showEventResult(person, '升职失败', 
        `很遗憾，这次升职机会没有把握住\n💡 继续努力，三年后还有机会！`, false)
    }
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
    
    // 检查随机事件
    const randomEvents = this.getRandomEvents(person.age, person)
    randomEvents.forEach(eventData => {
      if (Math.random() < eventData.probability) {
        this.triggerEvent(person, eventData.type)
      }
    })
  },
  
  // 获取重要事件（必然触发）
  getImportantEvents(age, person) {
    const events = []
    
    // 高考（18岁，且没有辍学）
    if (age === 18 && !person.schoolLevel && person.education !== '初中' && person.education !== '高中') {
      events.push('高考')
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
    
    // 升职（工作3年后每3年一次，自动触发，体力活不能升职）
    if (person.occupation && person.occupation !== '体力活' && person.workYears > 0 && person.workYears % 3 === 0 && person.lastPromotionYear < this.currentYear) {
      this.handlePromotion(person)
    }
    
    // 择偶（25岁后未婚人士）
    if (age >= 25 && !person.partner && Math.random() < 0.3) {
      events.push('择偶')
    }
    
    // 生育（结婚一年后，女性40岁以下）
    if (person.partner && person.flags.marriageYear && this.currentYear - person.flags.marriageYear >= 1 && 
        ((person.gender === '女' && person.age < 40) || (person.partner.gender === '女' && person.partner.age < 45)) && 
        Math.random() < 0.2) {
      events.push('生育')
    }
    
    // 退休（65岁）
    if (age === 65 && !person.isRetired) {
      events.push('退休')
    }
    
    return events
  },
  
  // 获取随机事件
  getRandomEvents(age, person) {
    const events = []
    
    // 早期教育事件
    if (age === 0) events.push({ type: '早教班', probability: 0.8 })
    if (age === 3) events.push({ type: '幼儿园择校', probability: 0.9 })
    
    // 小学阶段
    if (age === 6) events.push({ type: '小学择校', probability: 1.0 })
    if (age >= 7 && age <= 11 && age % 2 === 1) events.push({ type: '课外补习', probability: 0.6 })
    if (age === 8) events.push({ type: '才艺比赛', probability: 0.3 })
    
    // 初中阶段
    if (age === 12) events.push({ type: '小升初', probability: 0.8 })
    if (age === 13) events.push({ type: '青春发育', probability: 0.4 })
    if (age === 14) events.push({ type: '网瘾问题', probability: 0.3 })
    
    // 高中阶段
    if (age === 15) events.push({ type: '中考冲刺', probability: 0.7 })
    if (age === 15) events.push({ type: '高中选择', probability: 0.2 })
    if (age === 16) events.push({ type: '高中恋爱', probability: 0.5 })
    
    // 大学阶段
    if (age === 18) events.push({ type: '间隔年', probability: 0.1 })
    if (age === 20) events.push({ type: '大学创业', probability: 0.2 })
    
    // 职场阶段
    if (age === 32) events.push({ type: '副业投资', probability: 0.4 })
    if (age === 45) events.push({ type: '中年危机', probability: 0.8 })
    if (age === 50) events.push({ type: '父母养老', probability: 0.6 })
    
    // 老年阶段
    if (age === 65) events.push({ type: '环球旅行', probability: 0.3 })
    if (age === 70) events.push({ type: '立遗嘱', probability: 0.5 })
    
    // 普通随机事件
    if (age >= 15) events.push({ type: '健身年卡', probability: 0.02 })
    if (age >= 18) events.push({ type: '买彩票', probability: 0.03 })
    if (age >= 25) events.push({ type: '医美抗衰', probability: 0.04 })
    if (age >= 15) events.push({ type: '健康作息', probability: 0.05 })
    
    // 突发事件
    if (age >= 65) events.push({ type: '重病', probability: 0.05 })
    events.push({ type: '意外', probability: 0.0008 })
    
    return events
  },
  
  // 触发事件
  triggerEvent(person, eventType) {
    this.currentEvent = {
      person: person,
      type: eventType,
      options: this.getEventOptions(eventType, person)
    }
    this.isEventActive = true
  },
  
  // 获取事件选项
  getEventOptions(eventType, person) {
    const optionsMap = {
      // 重要事件
      '高考': [
        { text: '不上大学，直接工作', cost: 0, effects: {}, special: 'noCollege' },
        ...this.generateCollegeOptions(person)
      ],
      '读研选择': [
        { text: '不读研，直接就业', cost: 0, effects: {}, special: 'startJobSeeking' },
        { text: '考研', cost: 50000, effects: {}, special: 'gradSchool' }
      ],
      '找工作': this.generateJobEventOptions(person),
      '择偶': this.generateMarriageOptions(person),
      '生育': [
        { text: '暂不生育', cost: 0, effects: {} },
        { text: '生孩子', cost: 50000, effects: {}, special: 'haveBaby' }
      ],
      '退休': [
        { text: '正常退休', cost: 0, effects: {}, special: 'retire' },
        { text: '返聘工作', cost: 0, effects: { health: -1 }, special: 'keepWorking' }
      ],
      
      // 随机事件
      '早教班': [
        { text: '不去', cost: 0, effects: {} },
        { text: '去早教班', cost: 30000, effects: { intelligence: 1, charm: 1 } }
      ],
      '幼儿园择校': [
        { text: '公立幼儿园', cost: 1500, effects: {} },
        { text: '国际双语幼儿园', cost: 20000, effects: { intelligence: 2, charm: 2 }, special: 'internationalKG' }
      ],
      '小学择校': [
        { text: '普通小学', cost: 0, effects: {} },
        { text: '买学区房', cost: 300000, effects: {}, special: 'schoolDistrict' },
        { text: '国际小学', cost: 400000, effects: { intelligence: 8, charm: 4 } }
      ],
      '课外补习': [
        { text: '不上补习', cost: 0, effects: {} },
        { text: '常规补习', cost: 10000, effects: { intelligence: 2, health: -1 } },
        { text: '奥数', cost: 10000, effects: { intelligence: 5, charm: -3, health: -3 } },
        { text: '兴趣班', cost: 30000, effects: { intelligence: 1, charm: 3, health: -1 } }
      ],
      '才艺比赛': [
        { text: '不参加', cost: 0, effects: {} },
        { text: '参加比赛', cost: 5000, effects: { charm: 1 }, special: 'talentShow' }
      ],
      '小升初': [
        { text: '直升对口初中', cost: 0, effects: {} },
        { text: '民办牛校', cost: 150000, effects: { intelligence: 4 } },
        { text: '辍学就业', cost: 0, effects: {}, special: 'dropout12' }
      ],
      '青春发育': [
        { text: '顺其自然', cost: 0, effects: {} },
        { text: '医美/牙齿矫正', cost: 30000, effects: { charm: 3 } }
      ],
      '网瘾问题': [
        { text: '严格禁止', cost: 0, effects: { health: 1, charm: -1 } },
        { text: '适度放任', cost: 0, effects: { intelligence: -1, charm: 1 } }
      ],
      '中考冲刺': [
        { text: '普通复习', cost: 0, effects: {} },
        { text: '一对一私教', cost: 30000, effects: { intelligence: 3, health: -1 } }
      ],
      '高中选择': [
        { text: '普通高中', cost: 0, effects: {} },
        { text: '上国际高中', cost: 450000, effects: { intelligence: 3, charm: 6 } },
        { text: '上重点高中', cost: 10000, effects: { intelligence: 6, charm: 3 }, condition: person => person.intelligence > 70 },
        { text: '辍学就业', cost: 0, effects: {}, special: 'dropout16' }
      ],
      '高中恋爱': [
        { text: '专心学习', cost: 0, effects: {} },
        { text: '谈恋爱', cost: 0, effects: { intelligence: -1, charm: 2 }, special: 'youngLove' }
      ],
      '间隔年': [
        { text: '直接升学', cost: 0, effects: {} },
        { text: '环球旅行', cost: 50000, effects: { charm: 3, health: 2 } }
      ],
      '大学创业': [
        { text: '不参与创业', cost: 0, effects: {} },
        { text: '参与创业', cost: 150000, effects: {}, special: 'collegeStartup' }
      ],
      '第一份工作': this.getJobOptions(person),
      '婚恋市场': this.getMarriageOptions(person),
      '生娃': [
        { text: '暂不生育', cost: 0, effects: { charm: -2, health: 1 } },
        { text: '生1个孩子', cost: 50000, effects: {}, special: 'baby1' },
        { text: '生2个孩子', cost: 80000, effects: { health: -1 }, special: 'baby2' }
      ],
      '副业投资': [
        { text: '不做副业', cost: 0, effects: {} },
        { text: '炒股', cost: 100000, effects: {}, special: 'stocks' },
        { text: '奶茶店加盟', cost: 150000, effects: {}, special: 'teaShop' }
      ],
      '中年危机': [
        { text: '混日子', cost: 0, effects: {}, special: 'stagnant' },
        { text: '跳槽创业', cost: 300000, effects: {}, special: 'midlifeStartup' }
      ],
      '父母养老': [
        { text: '送养老院', cost: 60000, effects: { health: 1 }, special: 'nursingHome' },
        { text: '居家请护工', cost: 100000, effects: { charm: 2 }, special: 'homecare' }
      ],
      '退休': [
        { text: '正常退休', cost: 0, effects: {}, special: 'retire' },
        { text: '返聘工作', cost: 0, effects: { health: -1 }, special: 'workMore' }
      ],
      '环球旅行': [
        { text: '不去旅行', cost: 0, effects: {} },
        { text: '环球旅行', cost: 200000, effects: { charm: 3, health: 1 } }
      ],
      '立遗嘱': [
        { text: '不留遗产', cost: 0, effects: {}, special: 'noWill' },
        { text: '留房产给子女', cost: 0, effects: { charm: 1 }, special: 'inheritHouse' }
      ],
      '健身年卡': [
        { text: '不办健身卡', cost: 0, effects: {} },
        { text: '办健身年卡', cost: 10000, effects: { health: 1, charm: 1 } }
      ],
      '买彩票': [
        { text: '不买彩票', cost: 0, effects: {} },
        { text: '买彩票', cost: 200, effects: {}, special: 'lottery' }
      ],
      '医美抗衰': [
        { text: '不做医美', cost: 0, effects: {} },
        { text: '医美抗衰老', cost: 20000, effects: { charm: 2, health: -1 } }
      ],
      '健康作息': [
        { text: '不改变作息', cost: 0, effects: {} },
        { text: '健康作息', cost: 5000, effects: { health: 1 } }
      ],
      '重病': [
        { text: '不治疗', cost: 0, effects: { health: -30 } },
        { text: '一般治疗', cost: 200000, effects: { health: -15 } },
        { text: '优化治疗', cost: 500000, effects: { health: -5 } }
      ],
      '意外': [
        { text: '接受现实', cost: 0, effects: { health: -100 } }
      ]
    }
    return optionsMap[eventType] || []
  },
  
  // 生成高考大学选项
  generateCollegeOptions(person) {
    const majorOptions = this.generateMajorOptions()
    const schoolLevel = this.calculateGaokaoResult(person.intelligence, person.flags?.youngLove)
    
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
  
  // 生成工作事件选项
  generateJobEventOptions(person) {
    const jobOptions = this.generateJobOptions(person)
    const options = []
    
    jobOptions.forEach(jobName => {
      const successRate = this.calculateJobSuccessRate(person, jobName)
      const career = CAREERS[jobName]
      
      options.push({
        text: `应聘${jobName} (成功率${Math.round(successRate * 100)}%)`,
        cost: 0,
        effects: {},
        special: 'applyJob',
        jobData: { jobName, successRate }
      })
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
  
  // 处理事件选择
  handleEventChoice(option) {
    const person = this.currentEvent.person
    
    // 检查是否有足够经济（允许负债30万内继续选择）
    if (this.globalEconomy - option.cost < -300000) {
      uni.showToast({ 
        title: '此选择将导致破产，无法选择', 
        icon: 'none',
        duration: 3000
      })
      return
    }
    
    // 扣除费用
    this.globalEconomy -= option.cost
    
    // 应用基础属性效果
    Object.keys(option.effects).forEach(key => {
      if (['health', 'charm', 'intelligence'].includes(key)) {
        person[key] = Math.min(100, Math.max(0, person[key] + option.effects[key]))
      } else if (key === 'occupation') {
        person[key] = option.effects[key]
      }
    })
    
    // 处理特殊效果
    if (option.special) {
      this.handleSpecialEffects(person, option.special, option)
    }
    
    this.isEventActive = false
    this.currentEvent = null
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
      case 'retire':
        person.income = 50000 // 养老金
        break
      case 'workMore':
        person.income = 80000
        break
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
          const { schoolLevel, major } = option.majorData
          person.schoolLevel = schoolLevel
          person.major = major
          person.education = schoolLevel + '大学'
        }
        break
      case 'startJobSeeking':
        person.jobSeeking = true
        break
      case 'gradSchool':
        const successRate = person.schoolLevel === '双非' ? 0.4 : 
                           person.schoolLevel === '211' ? 0.65 : 
                           person.schoolLevel === '985' ? 0.9 : 0.3
        if (Math.random() < successRate) {
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
          const { jobName, successRate } = option.jobData
          if (Math.random() < successRate) {
            person.occupation = jobName
            person.jobSeeking = false
            const career = CAREERS[jobName]
            let baseSalary = career.minSalary + (person.education === '硕士' ? 30000 : 0)
            
            // 辍学薪资惩罚
            if (person.education === '初中') {
              baseSalary = baseSalary / 2
            } else if (person.education === '高中') {
              baseSalary = baseSalary / 1.5
            }
            
            person.income = Math.floor(baseSalary)
            person.workYears = 1
            this.showEventResult(person, '求职', 
              `🎉 成功入职${jobName}！\n💰 年薪：${person.income.toLocaleString()}元\n📈 职业生涯开始！`, true)
          } else {
            this.showEventResult(person, '求职', 
              `😔 求职失败\n💼 继续寻找工作机会\n🔥 不要放弃，坚持就是胜利！`, false)
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
      case 'retire':
        person.isRetired = true
        person.income = Math.floor(person.income / 4)
        break
      case 'keepWorking':
        person.income = Math.floor(person.income / 4)
        break
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
        economicContribution: 0,
        income: 0,
        isAlive: true,
        partner: null,
        children: [],
        occupation: null,
        education: '未入学',
        parents: [parent, partner],
        flags: {}
      }
      
      // 确保属性在合理范围内
      baby.health = Math.max(60, Math.min(100, baby.health))
      baby.charm = Math.max(60, Math.min(100, baby.charm))
      baby.intelligence = Math.max(60, Math.min(100, baby.intelligence))
      
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
  
  // 更新全局经济
  updateGlobalEconomy() {
    const totalContribution = this.persons
      .filter(p => p.isAlive)
      .reduce((sum, p) => sum + p.economicContribution, 0)
    this.globalEconomy += totalContribution
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
      }
    }
    
    // 重新初始化
    this.initGame()
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
    return Date.now().toString(36) + Math.random().toString(36).substr(2)
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