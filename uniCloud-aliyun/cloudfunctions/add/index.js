'use strict';

exports.main = async (event, context) => {
  // 从 event 对象中获取前端传来的 a 和 b
  const { a, b } = event;

  // 校验参数
  if (typeof a !== 'number' || typeof b !== 'number') {
    return {
      success: false,
      message: 'Parameters must be numbers.'
    }
  }

  // 计算总和
  const sum = a + b;

  // 返回结果
  return {
    success: true,
    sum: sum
  }
};
