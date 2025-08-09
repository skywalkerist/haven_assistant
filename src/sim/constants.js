// 统一常量配置 - 主线系统升级
export const REGION_UNIT_PRICE = { 
  rural: 6000, 
  county: 12000, 
  city: 30000, 
  mega: 60000 
}; // 元/㎡

export const REGION_RENT_BASE = { 
  rural: 800, 
  county: 1600, 
  city: 3200, 
  mega: 6500 
}; // 月租(基础)

export const REGION_COST_MULT = { 
  rural: 0.70, 
  county: 0.85, 
  city: 1.00, 
  mega: 1.35 
}; // 生活费倍率

export const REGION_SALARY_MULT = { 
  rural: 0.80, 
  county: 0.90, 
  city: 1.00, 
  mega: 1.25 
}; // 工资倍率

export const DEFAULT_HOUSING_REGION = 'city';

export const SCHOOL_ZONE_PREMIUM = 1.12; // 学区房单价溢价
export const DOWNPAY_DEFAULT = 0.30;
export const MORTGAGE_RATE = 0.045; // 年利率
export const MORTGAGE_YEARS = 25;

export const COLLEGE_COST_BY_BAND = { 
  '985': 5000, 
  '211': 5000, 
  '双非': 30000, 
  '二本': 40000 
};

export const COLLEGE_COMP_BONUS = { 
  '985': 8, 
  '211': 6, 
  '双非': 4, 
  '二本': 2 
};

export const COLLEGE_PSY_BONUS = { 
  '985': 2, 
  '211': 1, 
  '双非': 0, 
  '二本': 0 
};

export const YEARLY_RANDOM_LIMIT = { modal: 1, sheet: 1 }; // 单年最多弹窗数

// 4类地域的示例城市名（显示用；逻辑仍按 rural/county/city/mega 分）
export const REGION_NAMES = {
  rural:  ['豫东村','赣北乡','湘西镇','陕北镇','川西乡','皖北镇'],
  county: ['丹江口','仁怀','启东','海盐','寿光','博罗','玉山','射洪','瑞安','邳州'],
  city:   ['合肥','长沙','济南','福州','西安','郑州','厦门','苏州','大连','青岛'],
  mega:   ['北京','上海','深圳','广州','杭州','南京','成都','武汉']
}

// "去外地"的倾向（大学/工作/养老 回流）
export const MIGRATION_WEIGHTS = {
  uni:   { rural:{county:0.4,city:0.45,mega:0.15}, county:{city:0.55,mega:0.25}, city:{mega:0.4}, mega:{} },
  job:   { rural:{county:0.35,city:0.45,mega:0.20}, county:{city:0.50,mega:0.25}, city:{mega:0.35}, mega:{} },
  return:{ mega:{city:0.5,county:0.35,rural:0.15}, city:{county:0.45,rural:0.25}, county:{rural:0.35}, rural:{} }
}

// 迁移费用（显示/结算用，简化为一次性花费）
export const MOVE_COST = { rent: 8000, own_sell: 20000, own_bridge: 5000 } // 卖房税费/搬家等

// 死亡概率模型
export const MORTALITY = {
  // 年龄基线死亡率（年），拟合"50岁后缓慢上升，80+ 加速"
  baseAge: (age) => {
    if (age < 50) return 0.0005   // 0.05%
    if (age < 60) return 0.0015   // 0.15%
    if (age < 70) return 0.004    // 0.4%
    if (age < 80) return 0.012    // 1.2%
    if (age < 90) return 0.040    // 4.0%
    return 0.120                  // 12%
  },
  // 健康修正（健康低于70死亡风险升高，>70略降）
  healthFactor: (health) => {
    const d = 70 - health
    if (d <= -10) return 0.8      // 健康≥80 略降风险
    if (d <= 0) return 1.0
    // (70-health)^2 型放大，最大×3.5 限幅
    return Math.min(3.5, 1 + (d*d)/400)
  },
  // 重大意外基线（全龄），与已有0.0008兼容，可二选一；若保留你原本事件，这里可设0
  accident: 0.0006
}

export const FUNERAL_COST = { rural: 8000, county: 15000, city: 30000, mega: 50000 }

export const PENSION = {
  base: 50000,           // 现有基础养老金
  regionK: { rural:0.8, county:0.9, city:1.0, mega:1.1 }, // 地域调节系数（可选）
  floor: 40000, cap: 90000
}