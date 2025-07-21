'use strict';

const db = uniCloud.database();
const commandsCollection = db.collection('robot_commands');

exports.main = async (event, context) => {
	const { task, params } = event;

	if (!task) {
		return {
			success: false,
			errCode: 'INVALID_PARAM',
			errMsg: '任务名称 (task) 不能为空'
		}
	}

	try {
		const addRes = await commandsCollection.add({
			task: task,
			params: params || {},
			status: 'pending',
			created_at: Date.now()
		});

		return {
			success: true,
			commandId: addRes.id,
			errMsg: '指令已成功提交'
		}

	} catch (e) {
		return {
			success: false,
			errCode: 'DB_ERROR',
			errMsg: '数据库操作失败',
			error: e
		}
	}
};
