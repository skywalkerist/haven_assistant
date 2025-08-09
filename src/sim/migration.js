// 迁移工具模块 - 地域迁移逻辑与家庭搬迁管理
import { MIGRATION_WEIGHTS, REGION_NAMES, MOVE_COST } from './constants.js'

function weightedPick(weights) {
  const entries = Object.entries(weights)
  const total = entries.reduce((s,[,w])=>s+w, 0)
  if (total<=0) return undefined
  let r = Math.random()*total
  for (const [k,w] of entries){
    if ((r-=w) <= 0) return k
  }
  return entries[entries.length-1][0]
}

export function suggestTargetRegion(current, scene) {
  const tbl = MIGRATION_WEIGHTS[scene] || {}
  const w = tbl[current] || {}
  const t = weightedPick(w)
  return t
}

export function randomCityName(region){
  const list = REGION_NAMES[region]
  const i = Math.floor(Math.random()*list.length)
  return list[i]
}

// === 家庭整体迁移（把居住地改到新region；租房：改租；有按揭：走"卖房/转租/暂缓"分支）===
export function proposeFamilyMove(store, reason, target){
  const h = store.familyAssets?.housing
  const current = h?.regionType || h?.region || 'city'
  if (current === target) return // 不必迁移

  const title = `是否全家搬去 ${target}（${randomCityName(target)}）？`
  const canSell = h?.mode==='own'
  const choices = []
  
  if (h?.mode==='rent'){
    choices.push(
      { text:`搬家-租房（搬家费约${MOVE_COST.rent}）`, cost:0, effects:{}, special:'move_rent', target }
    )
  }else if (canSell){
    choices.push(
      { text:`卖房搬走（税费约${MOVE_COST.own_sell}）`, cost:0, effects:{}, special:'move_sell', target },
      { text:`先过去租房，房子暂不卖（过桥费约${MOVE_COST.own_bridge}）`, cost:0, effects:{}, special:'move_bridge', target },
    )
  }
  choices.push({ text:'暂不搬家', cost:0, effects:{}, special:'move_cancel' })

  store.currentEvent = { person: store.persons[0], type:'家庭迁移', ui:'modal',
    title, icon:'🧳', text:`原因：${reason}。当前：${current} → 目标：${target}`,
    options: choices, choices }
  store.isEventActive = true
}

export function applyFamilyMove(store, action, target){
  const h = store.familyAssets?.housing
  if (!h) return
  
  switch(action){
    case 'move_rent': {
      store.globalEconomy -= MOVE_COST.rent
      h.regionType = target
      h.cityName = randomCityName(target)
      h.mode = 'rent' // 保持租
      break
    }
    case 'move_sell': {
      // 简化：卖房收入=原价*(0.95±0.03)，清偿按揭（若有），支付税费
      const price = h.price || h.currentPrice || 0
      const gain = Math.round(price * (0.92 + Math.random()*0.06))
      store.globalEconomy += gain
      if (h.mortgage?.principal){
        // 清偿本金（粗略）
        store.globalEconomy -= Math.round(h.mortgage.principal * 0.85)
      }
      store.globalEconomy -= MOVE_COST.own_sell
      // 变更为目标城市租房，默认80㎡
      store.familyAssets.housing = { 
        mode:'rent', 
        regionType: target,
        cityName: randomCityName(target), 
        area:80,
        schoolTier: 'none',
        monthlyRent: 2400 // 默认值，实际会被重新计算
      }
      break
    }
    case 'move_bridge': {
      store.globalEconomy -= MOVE_COST.own_bridge
      // 目标先租（不动原房）
      store.familyAssets.housing.tempRentRegion = target
      store.familyAssets.housing.regionType = target
      store.familyAssets.housing.cityName = randomCityName(target)
      break
    }
    case 'move_cancel':
    default: return
  }
}