<template>
	<view class="chat-container">
		<scroll-view :scroll-y="true" class="message-list" :scroll-top="scrollTop">
			<view v-for="(message, index) in messages" :key="index" class="message-item" :class="message.sender">
				<image :src="message.avatar" class="avatar"></image>
				<view class="message-content">
					<view class="message-bubble">
						<text>{{ message.text }}</text>
					</view>
				</view>
			</view>
		</scroll-view>

		<view class="input-area">
			<image :src="isVoiceMode ? '/static/keyboard.png' : '/static/microphone.png'" class="mode-switch-icon" @click="toggleInputMode"></image>
			
			<input v-if="!isVoiceMode" type="text" v-model="inputValue" placeholder="请输入..." class="input-field" @confirm="sendTextMessage" />
			<button v-if="!isVoiceMode" @click="sendTextMessage" class="send-button">发送</button>
			
			<button v-if="isVoiceMode" class="voice-button" @longpress="startRecording" @touchend="stopRecording">
				{{ isRecording ? '松开结束' : '按住说话' }}
			</button>
		</view>
	</view>
</template>

<script>
const recorderManager = uni.getRecorderManager();

export default {
	data() {
		return {
			inputValue: '',
			scrollTop: 0,
			messages: [{
				sender: 'robot',
				avatar: '/static/robot.png',
				text: '你好！有什么可以帮你的吗？'
			}],
			isVoiceMode: false,
			isRecording: false,
		};
	},
	onLoad() {
		this.initRecorder();
		// 监听推送消息，用于接收AI回复
		uni.onPushMessage((res) => {
			console.log("收到推送消息:", res);
			if (res.type === 'receive') {
				this.handlePushPayload(res.data);
			}
		});
	},
	methods: {
		initRecorder() {
			recorderManager.onStop((res) => {
				this.isRecording = false;
				uni.hideLoading();
				console.log('录音停止', res);
				this.uploadAudio(res.tempFilePath);
			});
			recorderManager.onError((err) => {
				this.isRecording = false;
				uni.hideLoading();
				uni.showToast({ title: '录音失败', icon: 'none' });
				console.error('录音失败', err);
			});
		},
		toggleInputMode() {
			this.isVoiceMode = !this.isVoiceMode;
		},
		sendTextMessage() {
			if (!this.inputValue.trim()) {
				uni.showToast({ title: '消息不能为空', icon: 'none' });
				return;
			}
			const text = this.inputValue;
			this.addMessage('user', text);
			this.inputValue = '';
			
			// 调用云函数发送文字指令
			this.postDialogueCommand(text);
		},
		startRecording() {
			this.isRecording = true;
			uni.showLoading({ title: '正在录音...' });
			recorderManager.start({
				sampleRate: 16000,
				numberOfChannels: 1,
				format: 'pcm'
			});
		},
		stopRecording() {
			if (this.isRecording) {
				recorderManager.stop();
			}
		},
		uploadAudio(filePath) {
			uni.getFileSystemManager().readFile({
				filePath: filePath,
				encoding: 'base64',
				success: (res) => {
					uni.showLoading({ title: '识别中...' });
					uniCloud.callFunction({
						name: 'uploadAudioForASR',
						data: {
							audioBase64: res.data
						}
					}).then(() => {
						uni.hideLoading();
						uni.showToast({ title: '语音已发送', icon: 'success' });
					}).catch(err => {
						uni.hideLoading();
						uni.showToast({ title: '语音发送失败', icon: 'none' });
					});
				},
				fail: (err) => {
					uni.showToast({ title: '读取文件失败', icon: 'none' });
				}
			});
		},
		postDialogueCommand(text) {
			uniCloud.callFunction({
				name: 'postCommand',
				data: {
					task: 'dialogue',
					params: { text: text }
				}
			}).catch(err => {
				uni.showToast({ title: '指令发送失败', icon: 'none' });
			});
		},
		addMessage(sender, text) {
			const avatar = sender === 'user' ? '/static/icon_user.png' : '/static/robot.png';
			this.messages.push({ sender, text, avatar });
			this.scrollToBottom();
		},
		handlePushPayload(payload) {
			if (typeof payload === 'string') {
				try {
					payload = JSON.parse(payload);
				} catch (e) {
					console.error("解析推送payload失败:", e);
					return;
				}
			}
			if (payload.type === 'dialogue_response' && payload.text) {
				this.addMessage('robot', payload.text);
			}
		},
		scrollToBottom() {
			this.$nextTick(() => {
				this.scrollTop = this.messages.length * 1000;
			});
		}
	}
};
</script>

<style scoped>
.chat-container {
	display: flex;
	flex-direction: column;
	height: 100vh;
	background-color: #f4f4f4;
}
.message-list {
	flex: 1;
	padding: 20rpx;
	box-sizing: border-box;
	overflow-y: auto;
}
.message-item {
	display: flex;
	margin-bottom: 30rpx;
}
.message-item.user {
	flex-direction: row-reverse;
}
.avatar {
	width: 80rpx;
	height: 80rpx;
	border-radius: 50%;
	margin: 0 20rpx;
}
.message-content {
	max-width: 70%;
}
.message-bubble {
	background-color: #ffffff;
	padding: 20rpx;
	border-radius: 15rpx;
	word-wrap: break-word;
}
.message-item.user .message-bubble {
	background-color: #a0e959;
}
.input-area {
	display: flex;
	align-items: center;
	padding: 20rpx;
	background-color: #ffffff;
	border-top: 1rpx solid #e0e0e0;
}
.mode-switch-icon {
	width: 60rpx;
	height: 60rpx;
	margin-right: 20rpx;
}
.input-field {
	flex: 1;
	height: 70rpx;
	background-color: #f4f4f4;
	border-radius: 35rpx;
	padding: 0 30rpx;
	font-size: 28rpx;
}
.send-button {
	width: 120rpx;
	height: 70rpx;
	line-height: 70rpx;
	margin-left: 20rpx;
	background-color: #007aff;
	color: white;
	border: none;
	border-radius: 35rpx;
	font-size: 28rpx;
	text-align: center;
}
.voice-button {
	flex: 1;
	height: 70rpx;
	line-height: 70rpx;
	background-color: #007aff;
	color: white;
	border-radius: 35rpx;
	text-align: center;
}
</style>
