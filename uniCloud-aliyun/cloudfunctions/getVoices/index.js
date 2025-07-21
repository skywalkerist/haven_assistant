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
	
	console.log('开始执行 getVoices 云函数...');
	
	try {
		const result = await fileUtils.requestFileOperation('get_voices_config', {}, context);
		
		if (result.success) {
			console.log('成功从客户端获取到 voices.json 内容');
			// 客户端返回的应该是JSON字符串，这里需要解析
			try {
				const voicesConfig = JSON.parse(result.data.fileContent);
				return {
					success: true,
					data: voicesConfig
				};
			} catch (e) {
				console.error('解析从客户端返回的JSON时出错:', e);
				return { success: false, message: '无法解析客户端返回的配置文件' };
			}
		} else {
			console.error('调用 requestFileOperation 失败:', result.message);
			return {
				success: false,
				message: result.message || '获取音色配置失败'
			};
		}
	} catch (e) {
		console.error('getVoices 云函数执行时发生严重错误:', e);
		return {
			success: false,
			message: '服务器内部错误',
			error: e.message
		};
	}
};
