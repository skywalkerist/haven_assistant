'use strict';

const db = uniCloud.database()
const collection = db.collection('game_saves')

exports.main = async (event, context) => {
  const { action, data } = event
  
  // 获取用户信息
  const { uid } = context
  if (!uid) {
    return {
      success: false,
      message: '用户未登录'
    }
  }
  
  try {
    switch (action) {
      case 'save':
        return await saveGame(uid, data)
      case 'load':
        return await loadGame(uid, data.saveId)
      case 'list':
        return await getSaveList(uid)
      case 'delete':
        return await deleteSave(uid, data.saveId)
      default:
        return {
          success: false,
          message: '未知操作'
        }
    }
  } catch (error) {
    return {
      success: false,
      message: error.message
    }
  }
}

// 保存游戏
async function saveGame(userId, gameData) {
  const saveData = {
    user_id: userId,
    save_name: gameData.saveName || `存档_${new Date().getTime()}`,
    current_year: gameData.currentYear,
    global_economy: gameData.globalEconomy,
    persons: gameData.persons,
    create_time: new Date(),
    update_time: new Date()
  }
  
  if (gameData.saveId) {
    // 更新现有存档
    const result = await collection.doc(gameData.saveId).update(saveData)
    return {
      success: true,
      data: result,
      message: '游戏保存成功'
    }
  } else {
    // 创建新存档
    const result = await collection.add(saveData)
    return {
      success: true,
      data: result,
      message: '游戏保存成功'
    }
  }
}

// 加载游戏
async function loadGame(userId, saveId) {
  const result = await collection.doc(saveId).get()
  
  if (result.data.length === 0) {
    return {
      success: false,
      message: '存档不存在'
    }
  }
  
  const saveData = result.data[0]
  
  // 验证是否是用户的存档
  if (saveData.user_id !== userId) {
    return {
      success: false,
      message: '无权限访问此存档'
    }
  }
  
  return {
    success: true,
    data: saveData,
    message: '游戏加载成功'
  }
}

// 获取存档列表
async function getSaveList(userId) {
  const result = await collection
    .where({
      user_id: userId
    })
    .orderBy('update_time', 'desc')
    .limit(20)
    .get()
  
  return {
    success: true,
    data: result.data,
    message: '获取存档列表成功'
  }
}

// 删除存档
async function deleteSave(userId, saveId) {
  // 先验证权限
  const checkResult = await collection.doc(saveId).get()
  if (checkResult.data.length === 0) {
    return {
      success: false,
      message: '存档不存在'
    }
  }
  
  if (checkResult.data[0].user_id !== userId) {
    return {
      success: false,
      message: '无权限删除此存档'
    }
  }
  
  const result = await collection.doc(saveId).remove()
  return {
    success: true,
    data: result,
    message: '删除存档成功'
  }
}