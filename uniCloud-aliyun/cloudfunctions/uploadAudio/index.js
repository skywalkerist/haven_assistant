'use strict';
exports.main = async (event, context) => {
	// 兼容 HTTP POST 的 body
	let params = event;
	if (event.body) {
		try {
			params = JSON.parse(event.body);
		} catch (e) {
			return { success: false, message: '无效的请求体' };
		}
	}

	const {
		fileContent, // base64 编码的文件内容
		fileName // 例如 'cloned_voice.wav'
	} = params;

	if (!fileContent || !fileName) {
		return {
			success: false,
			message: '缺少 fileContent 或 fileName 参数'
		}
	}

	try {
		// 1. 将 base64 转换为 Buffer
		const fileBuffer = Buffer.from(fileContent, 'base64');

		// 2. 上传文件到云存储
		const result = await uniCloud.uploadFile({
			cloudPath: `audio-cloning/${fileName}`, // 在云存储中创建一个专门的文件夹
			fileContent: fileBuffer,
			cloudPathAsRealPath: true, // 使用完整的云路径
			header: {
				'Content-Type': 'audio/wav'
			}
		});

		if (!result.fileID) {
			throw new Error('文件上传失败，未返回 fileID');
		}

		// 3. 获取文件的临时下载链接
		const tempUrlResult = await uniCloud.getTempFileURL({
			fileList: [result.fileID]
		});
		
		if (tempUrlResult.fileList.length === 0 || !tempUrlResult.fileList[0].tempFileURL) {
			throw new Error('获取文件临时链接失败');
		}

		// 4. 返回成功信息和URL
		return {
			success: true,
			message: '文件上传成功',
			url: tempUrlResult.fileList[0].tempFileURL,
			fileID: result.fileID
		}

	} catch (e) {
		console.error('Upload audio error:', e);
		return {
			success: false,
			message: '处理文件上传时发生错误',
			error: e.message
		}
	}
};
