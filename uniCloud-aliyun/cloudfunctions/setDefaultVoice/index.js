'use strict';

const fileUtils = require('file-utils');

exports.main = async (event, context) => {
	// 兼容HTTP POST的body
	if (event.body) {
		try {
			event = JSON.parse(event.body);
		} catch (e) {
			return { success: false, message: '无效的请求体' };
		}
	}
	
	const { voiceName } = event;
	
	if (!voiceName) {
		return { success: false, message: '缺少 voiceName 参数' };
	}
	
	console.log(`开始执行 setDefaultVoice 云函数, 设置默认音色为: ${voiceName}`);
	
	try {
		const result = await fileUtils.requestFileOperation('set_voices_config', { default_voice: voiceName }, context);
		
		if (result.success) {
			console.log('成功在客户端设置了默认音色');
			return { success: true, message: '设置成功' };
		} else {
			console.error('调用 requestFileOperation 失败:', result.message);
			return {
				success: false,
				message: result.message || '设置默认音色失败'
			};
		}
	} catch (e) {
		console.error('setDefaultVoice 云函数执行时发生严重错误:', e);
		return {
			success: false,
			message: '服务器内部错误',
			error: e.message
		};
	}
};
