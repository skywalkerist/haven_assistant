'use strict';
const db = uniCloud.database();
const commandsCollection = db.collection('robot_commands');

exports.main = async (event, context) => {
	const { audioBase64 } = event;
	const clientInfo = context.clientInfo;

	if (!audioBase64) {
		return {
			success: false,
			message: '缺少 audioBase64 参数'
		};
	}

	try {
		const command = {
			task: 'speech_to_text',
			params: {
				audioBase64: audioBase64
			},
			status: 'pending',
			createdAt: new Date(),
			clientId: clientInfo.clientId // 记录下发指令的客户端ID，用于后续推送
		};

		const res = await commandsCollection.add(command);

		return {
			success: true,
			message: '语音任务已创建',
			commandId: res.id
		};

	} catch (e) {
		console.error(e);
		return {
			success: false,
			message: '创建任务失败'
		};
	}
};
