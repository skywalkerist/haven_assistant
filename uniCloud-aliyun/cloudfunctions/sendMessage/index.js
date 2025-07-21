'use strict';

// 获取数据库引用
const db = uniCloud.database();

exports.main = async (event, context) => {
  // event 包含前端调用时传入的参数
  const { text } = event;

  if (!text) {
    return {
      success: false,
      message: 'Text cannot be empty',
    };
  }

  try {
    // 向 'messages' 集合中添加一条新记录
    const addRes = await db.collection('messages').add({
      content: text,
      status: 'pending', // 初始状态为“待处理”
      create_time: Date.now() // 记录当前时间戳
    });

    // 检查是否成功添加
    if (addRes.id) {
      // 返回成功响应和新记录的ID
      return {
        success: true,
        message: 'Message successfully saved to database.',
        id: addRes.id
      };
    } else {
      throw new Error('Failed to get ID from database response.');
    }

  } catch (error) {
    console.error('Error saving message to database:', error);
    return {
      success: false,
      message: 'Failed to save message.',
      error: error.message
    };
  }
};
