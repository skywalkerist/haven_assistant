// 高考系统 - 基于竞争力的现代化计算
import { clamp01 } from './util.js'

export function calcGaokao(person) {
  const comp = person.competitiveness ?? 50
  const psy = person.psyche ?? 50
  const st = person.strain ?? 45
  const bonus = (person.flags?.earlyEducation ? 2 : 0) + 
                (person.flags?.internationalKG ? 1 : 0)
  const noise = (Math.random() * 10 - 5)

  let raw = 0.7 * comp + 0.15 * psy - 0.2 * Math.max(0, st - 60) + bonus + noise
  raw = Math.max(0, Math.min(100, Math.round(raw)))

  let band = '二本'
  if (raw >= 75) band = '985'
  else if (raw >= 55) band = '211'
  else if (raw >= 35) band = '双非'
  
  return { score: raw, band }
}