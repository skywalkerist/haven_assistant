'use strict';

const db = uniCloud.database()
const collection = db.collection('game_events')

exports.main = async (event, context) => {
  const { action, data } = event
  
  try {
    switch (action) {
      case 'getEvents':
        return await getEventsByAge(data.age)
      case 'getAllEvents':
        return await getAllEvents()
      case 'initEvents':
        return await initDefaultEvents()
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

// 根据年龄获取事件
async function getEventsByAge(age) {
  const result = await collection
    .where({
      trigger_age: age
    })
    .get()
  
  return {
    success: true,
    data: result.data
  }
}

// 获取所有事件
async function getAllEvents() {
  const result = await collection
    .orderBy('trigger_age', 'asc')
    .get()
  
  return {
    success: true,
    data: result.data
  }
}

// 初始化默认事件
async function initDefaultEvents() {
  const defaultEvents = [
    {
      event_type: '小学择校',
      trigger_age: 6,
      title: '小学择校',
      description: '选择合适的小学对孩子的成长很重要',
      probability: 0.8,
      options: [
        {
          text: '普通小学',
          cost: 0,
          effects: { intelligence: 0 }
        },
        {
          text: '重点小学',
          cost: 5000,
          effects: { intelligence: 5 }
        },
        {
          text: '私立小学',
          cost: 20000,
          effects: { intelligence: 10, charm: 5 }
        }
      ]
    },
    {
      event_type: '是否上补习班',
      trigger_age: 12,
      title: '是否上补习班',
      description: '补习班可以提高成绩但可能影响健康',
      probability: 0.6,
      options: [
        {
          text: '不上补习班',
          cost: 0,
          effects: { health: 5 }
        },
        {
          text: '上补习班',
          cost: 10000,
          effects: { intelligence: 10, health: -5 }
        }
      ]
    },
    {
      event_type: '高中择校',
      trigger_age: 15,
      title: '高中择校',
      description: '高中的选择影响大学入学',
      probability: 0.7,
      options: [
        {
          text: '普通高中',
          cost: 0,
          effects: { intelligence: 5 }
        },
        {
          text: '重点高中',
          cost: 15000,
          effects: { intelligence: 15 }
        },
        {
          text: '国际学校',
          cost: 50000,
          effects: { intelligence: 20, charm: 10 }
        }
      ]
    },
    {
      event_type: '大学选择',
      trigger_age: 18,
      title: '大学选择',
      description: '选择大学和专业决定未来发展',
      probability: 0.9,
      options: [
        {
          text: '不上大学，直接工作',
          cost: 0,
          effects: { occupation: '工人' }
        },
        {
          text: '普通大学',
          cost: 40000,
          effects: { intelligence: 15, education: '大学' }
        },
        {
          text: '名牌大学',
          cost: 80000,
          effects: { intelligence: 25, charm: 10, education: '名牌大学' }
        }
      ]
    },
    {
      event_type: '职业选择',
      trigger_age: 22,
      title: '职业选择',
      description: '选择第一份工作',
      probability: 0.8,
      options: [
        {
          text: '进工厂',
          cost: 0,
          effects: { occupation: '工人' }
        },
        {
          text: '办公室工作',
          cost: 0,
          effects: { occupation: '白领' }
        },
        {
          text: '创业',
          cost: 50000,
          effects: { occupation: '企业家' }
        }
      ]
    }
  ]
  
  // 批量插入事件
  const result = await collection.add(defaultEvents)
  
  return {
    success: true,
    data: result,
    message: '默认事件初始化成功'
  }
}