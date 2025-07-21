'use strict';

const db = uniCloud.database();
const dbCmd = db.command;
const commandsCollection = db.collection('robot_commands');

exports.main = async (event, context) => {
	// 定义超时时间，例如 60 秒
	const TIMEOUT_SECONDS = 60;
	
	// 计算过期的时间戳
	const expirationTime = Date.now() - TIMEOUT_SECONDS * 1000;

	try {
		// 查找所有创建时间早于过期时间，并且状态仍然是 'pending' 或 'processing' 的指令
		const updateResult = await commandsCollection.where({
			created_at: dbCmd.lt(expirationTime),
			status: dbCmd.in(['pending', 'processing'])
		}).update({
			status: 'failed',
			error_message: '任务执行超时'
		});

		const updatedCount = updateResult.updated;
		if (updatedCount > 0) {
			console.log(`成功清理了 ${updatedCount} 个过期任务。`);
		} else {
			console.log('没有发现需要清理的过期任务。');
		}

		return {
			success: true,
			cleaned_count: updatedCount
		};

	} catch (e) {
		console.error('清理过期任务时发生错误:', e);
		return {
			success: false,
			message: '清理任务失败',
			error: e.message
		};
	}
};
