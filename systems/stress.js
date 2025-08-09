import { CONFIG } from './config.js'
import { clamp, randInt } from './random.js'

export function applyStudyStress(person, type) {
  const map = { tutoring:'tutoring', olympic:'olympic', hobby:'hobby' }
  const rule = CONFIG.study[ map[type] ]
  if (!rule) return
  person.cumStudyHours = (person.cumStudyHours||0) + rule.hours
  const [a,b] = rule.stress
  person.stress = clamp((person.stress||0) + randInt(a,b), ...CONFIG.stress.cap)
}

export function computeStudyEfficiency(person) {
  const w = CONFIG.study.effWeights
  const raw = (person.intelligence*w.intelligence + person.motivation*w.motivation + person.stability*w.stability)
  const dim = 1 - Math.pow(( (person.cumStudyHours||0) / CONFIG.study.diminishingHours ), CONFIG.study.diminishingPower)
  const healthMod = (person.health < CONFIG.study.healthPenaltyThreshold) ? CONFIG.study.healthPenaltyFactor : 1
  const stressMod = (person.stress > CONFIG.study.stressPenaltyThreshold) ? CONFIG.study.stressPenaltyFactor : 1
  const eff = raw * Math.max(0, dim) * healthMod * stressMod
  return Math.max(0, Math.min(200, eff))
}

export function annualStressRecovery(person) {
  person.stress = clamp((person.stress||0) - CONFIG.stress.annualRecovery, ...CONFIG.stress.cap)
}

export function maybeBurnout(person) {
  if ((person.stress||0) <= CONFIG.stress.burnoutThreshold) return false
  if (Math.random() < CONFIG.stress.burnoutProb) {
    person.motivation = Math.max(0, person.motivation + CONFIG.stress.burnoutEffects.motivation)
    person.flags = person.flags || {}
    person.flags.burnoutThisYear = true
    return true
  }
  return false
}