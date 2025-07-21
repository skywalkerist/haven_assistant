/**
 * file-utils.js
 * 一个用于通过轮询机制与客户端安全交换文件的公共模块
 */

const uniID = require('uni-id-common')

// 定义任务的默认超时时间（秒）
const COMMAND_TIMEOUT = 15; // 15秒超时

module.exports = {
	/**
	 * 请求客户端执行一个文件操作任务，并等待结果
	 * @param {string} taskName - 要执行的任务名称 (例如 'get_voices_config')
	 * @param {object} params - 传递给任务的参数
	 * @param {object} context - 云函数的上下文，用于获取用户信息
	 * @returns {object} 返回从客户端获取的结果
	 */
	async requestFileOperation(taskName, params = {}, context) {
		const db = uniCloud.database();
		const commandsCollection = db.collection('robot_commands');
		
		// 1. 获取当前登录用户的uid
		const clientInfo = context.clientInfo;
		const uniIDIns = uniID.createInstance({ clientInfo });
		const { uid } = await uniIDIns.checkToken(context.token);
		
		if (!uid) {
			return { success: false, message: '用户未登录或Token无效' };
		}

		// 2. 插入一条新指令到数据库
		const command = {
			uid: uid,
			task: taskName,
			params: params,
			status: 'pending', // pending, processing, completed, failed
			createdAt: Date.now(),
			expiredAt: Date.now() + COMMAND_TIMEOUT * 1000
		};
		const addRes = await commandsCollection.add(command);
		const commandId = addRes.id;

		if (!commandId) {
			return { success: false, message: '创建指令失败' };
		}

		// 3. 轮询等待指令结果
		for (let i = 0; i < COMMAND_TIMEOUT; i++) {
			await new Promise(resolve => setTimeout(resolve, 1000)); // 等待1秒

			const { data: [cmd] } = await commandsCollection.doc(commandId).get();

			if (cmd.status === 'completed') {
				return { success: true, data: cmd.result };
			}
			if (cmd.status === 'failed') {
				return { success: false, message: cmd.errorMessage || '客户端执行失败' };
			}
			// 如果还是 pending 或 processing，则继续轮询
		}

		// 4. 超时处理
		return { success: false, message: '等待客户端响应超时' };
	}
}
