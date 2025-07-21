'use strict';

const db = uniCloud.database();
const commandsCollection = db.collection('robot_commands');

exports.main = async (event, context) => {
	// **关键修复**：
	// 兼容来自 Python HTTP 请求 (event.body) 和来自前端 App 调用 (event) 的参数
	let params = event;
	if (event.body) {
		try {
			// 如果是 HTTP 调用，参数在 body 的 JSON 字符串里
			params = JSON.parse(event.body);
		} catch (e) {
			return { success: false, message: '无效的请求体' };
		}
	}

	// Part 1: 更新指令状态
	// 如果传入了 commandId，说明是树莓派客户端来更新任务状态的
	if (params.commandId) {
		const { commandId, status, result, errorMessage } = params;
		try {
			await commandsCollection.doc(commandId).update({
				status: status,
				result: result || null,
				error_message: errorMessage || ''
			});
			return {
				success: true,
				message: `指令 ${commandId} 状态已更新为 ${status}`
			}
		} catch (e) {
			return {
				success: false,
				message: '更新指令状态失败',
				error: e.message
			}
		}
	}

	// Part 2: 获取新指令
	// 如果没有传入 commandId，说明是树莓派客户端来轮询新任务的
	try {
		const findRes = await commandsCollection
			.where({ status: 'pending' })
			.orderBy('created_at', 'asc')
			.limit(1)
			.get();

		if (findRes.data.length === 0) {
			return {
				success: true,
				command: null,
				message: '没有待处理的指令'
			};
		}

		const commandToProcess = findRes.data[0];

		const updateRes = await commandsCollection
			.where({
				_id: commandToProcess._id,
				status: 'pending'
			})
			.update({
				status: 'processing'
			});

		if (updateRes.updated === 1) {
			return {
				success: true,
				command: commandToProcess
			};
		} else {
			return {
				success: true,
				command: null,
				message: '任务已被其他客户端获取'
			};
		}

	} catch (e) {
		return {
			success: false,
			message: '轮询指令失败',
			error: e.message
		};
	}
};
