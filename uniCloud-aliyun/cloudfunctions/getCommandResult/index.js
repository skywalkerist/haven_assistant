'use strict';

const db = uniCloud.database();
const commandsCollection = db.collection('robot_commands');

exports.main = async (event, context) => {
	const { commandId } = event;

	if (!commandId) {
		return {
			success: false,
			errCode: 'INVALID_PARAM',
			errMsg: '指令ID (commandId) 不能为空'
		}
	}

	try {
		const res = await commandsCollection.doc(commandId).get();

		if (!res.data || res.data.length === 0) {
			return {
				success: false,
				errCode: 'NOT_FOUND',
				errMsg: '找不到指定的指令'
			}
		}

		const command = res.data[0];

		return {
			success: true,
			command: command
		}

	} catch (e) {
		return {
			success: false,
			errCode: 'DB_ERROR',
			errMsg: '数据库查询失败',
			error: e
		}
	}
};
