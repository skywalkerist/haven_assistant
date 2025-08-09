import { CONFIG } from './config.js'
import { normal } from './random.js'
import { computeStudyEfficiency } from './stress.js'

export function calcGaokaoScore(person) {
  const mu = person.intelligence * 1.2
  const sigma = person.flags?.youngLove ? CONFIG.gaokao.loveSigma : CONFIG.gaokao.baseSigma
  const base = normal(mu, sigma)
  const eff = computeStudyEfficiency(person)
  const effAdj = Math.max(CONFIG.gaokao.effCap[0], Math.min(CONFIG.gaokao.effCap[1], eff/5))
  const state = 
    (person.stress>CONFIG.gaokao.stateMods.stressThreshold ? CONFIG.gaokao.stateMods.highStress : 0) +
    (person.motivation>CONFIG.gaokao.stateMods.motivationThreshold ? CONFIG.gaokao.stateMods.highMotivation : 0)
  return Math.round(base + effAdj + state)
}

export function bandByScore(score) {
  const b = CONFIG.gaokao.band.find(x => score>=x.min && score<=x.max)
  return b ? b.name : '二本'
}