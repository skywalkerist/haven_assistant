import { CONFIG } from './config.js'
import { randInt } from './random.js'

export function initIndustry(world) {
  world.industry = world.industry || {}
  world.industry.multipliers = world.industry.multipliers || {}
  world.industry.lastTick = world.industry.lastTick || 0
}

export function getMultiplier(category, world) {
  if (!world?.industry?.multipliers) return 1
  const macro = world.industry.multipliers['macro'] ?? CONFIG.industry.baseMultiplier
  const cat   = world.industry.multipliers[category] ?? CONFIG.industry.baseMultiplier
  return macro * cat
}

export function tickIndustry(world, currentYear) {
  initIndustry(world)
  if (world.industry.lastTick === currentYear) return
  world.industry.lastTick = currentYear

  // 以"是否到期"判定周期触发（简单实现：用 year 取模）
  CONFIG.industry.cycles.forEach(cyc=>{
    const period = randInt(cyc.every[0], cyc.every[1])
    const due = (currentYear % period) === 0
    if (!due) return
    const impact = (Math.random()*(cyc.impact[1]-cyc.impact[0])) + cyc.impact[0] // [-x,+y]
    if (cyc.applyAll) {
      world.industry.multipliers['macro'] = (world.industry.multipliers['macro'] ?? 1) * (1+impact)
    } else {
      world.industry.multipliers[cyc.category] = (world.industry.multipliers[cyc.category] ?? 1) * (1+impact)
    }
  })
}