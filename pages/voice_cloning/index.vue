<template>
	<view class="page-container">
		<!-- 1. 自定义导航栏 -->
		<view class="custom-nav-bar">
			<text class="back-arrow" @click="goBack">&lt;</text>
			<text class="nav-title">添加音色</text>
		</view>

		<!-- 2. 朗读文本区域 -->
		<view class="content-section">
			<text class="prompt-title">请朗读下面这段话</text>
			<view class="text-card">
				<text class="text-to-read">森林中有一棵魔法苹果树，据说吃了它结的苹果可以实现一个愿望，许多小动物都悄悄来到这里，希望愿望成真。</text>
			</view>
			<view class="status-bar" v-if="status !== 'idle'">
				<text class="status-text">{{ statusText }}</text>
			</view>
		</view>

		<!-- 3. 底部按钮区域 -->
		<view class="button-container">
			<!-- 底部按钮栏 -->
			<view class="button-bar">
				<button class="bar-button" @click="playRecording" :disabled="!hasRecording || status !== 'idle'">
					{{ status === 'playing' ? '播放中...' : '播放录音' }}
				</button>
				<button class="bar-button record-button" @click="handleRecord" :loading="status === 'recording'" :disabled="status !== 'idle'">
					录制声音
				</button>
				<button class="bar-button" @click="startTraining" :disabled="!hasRecording || status !== 'idle'">开始训练</button>
			</view>
		</view>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				status: 'idle', // idle, recording, playing, training
				audioUrl: null,
				audioPlayer: null,
				pollingTimer: null,
				hasRecording: false
			}
		},
		computed: {
			statusText() {
				switch(this.status) {
					case 'recording':
						return '正在录音中，请稍候...';
					case 'playing':
						return '正在播放...';
					case 'training':
						return '正在训练模型，这可能需要几分钟...';
					default:
						return '';
				}
			}
		},
		onReady() {
			this.audioPlayer = uni.createInnerAudioContext();
			this.audioPlayer.onEnded(() => {
				this.status = 'idle';
			});
			this.audioPlayer.onError((res) => {
				uni.showToast({ title: '播放失败', icon: 'error' });
				this.status = 'idle';
			});
		},
		onUnload() {
			if (this.pollingTimer) {
				clearInterval(this.pollingTimer);
			}
			if (this.audioPlayer) {
				this.audioPlayer.destroy();
			}
		},
		methods: {
			goBack() {
				uni.navigateBack();
			},

			async handleRecord() {
				this.status = 'recording';
				this.audioUrl = null; // 清除旧的录音
				this.hasRecording = false;

				try {
					const res = await uniCloud.callFunction({
						name: 'postCommand',
						data: { task: 'record_audio', params: {} }
					});

					if (res.result && res.result.success) {
						const commandId = res.result.commandId;
						this.startPolling(commandId);
					} else {
						throw new Error(res.result.message || '发送指令失败');
					}
				} catch (e) {
					uni.showToast({ title: e.message || '请求失败', icon: 'error' });
					this.status = 'idle';
				}
			},

			startPolling(commandId) {
				this.pollingTimer = setInterval(async () => {
					try {
						const res = await uniCloud.callFunction({
							name: 'getCommandResult',
							data: { commandId }
						});
						
						const command = res.result.command;
						if (command.status === 'completed') {
							clearInterval(this.pollingTimer);
							this.status = 'idle';
							if (command.task === 'record_audio') {
								this.audioUrl = command.result.audioUrl;
								this.hasRecording = true;
								uni.showToast({ title: '录音成功！', icon: 'success' });
							} else if (command.task === 'train_voice') {
								uni.showToast({ title: '声音训练成功！', icon: 'success' });
								// 创建新的音色对象并存储
								const newVoice = {
									id: Date.now(),
									name: this.currentVoiceName || '新音色',
									audioUrl: this.audioUrl
								};
								uni.setStorageSync('newly_added_voice', newVoice);
								// 跳转回音色管理页面
								uni.navigateBack();
							}
						} else if (command.status === 'failed') {
							clearInterval(this.pollingTimer);
							this.status = 'idle';
							const defaultMessage = command.task === 'record_audio' ? '录音失败' : '训练失败';
							uni.showToast({ title: command.errorMessage || defaultMessage, icon: 'error', duration: 3000 });
						}
						// if status is 'processing' or 'pending', do nothing and wait for next poll
					} catch (e) {
						clearInterval(this.pollingTimer);
						this.status = 'idle';
						uni.showToast({ title: '轮询结果失败', icon: 'error' });
					}
				}, 3000); // 每3秒轮询一次
			},

			playRecording() {
				if (!this.audioUrl) {
					uni.showToast({ title: '没有可播放的录音', icon: 'none' });
					return;
				}
				this.status = 'playing';
				this.audioPlayer.src = this.audioUrl;
				this.audioPlayer.play();
			},

			startTraining() {
				uni.showModal({
					title: '为新声音命名',
					content: '请输入一个名称，例如 "我的声音"。',
					editable: true,
					success: async (res) => {
						if (res.confirm && res.content) {
							const voiceName = res.content;
							this.currentVoiceName = voiceName;
							this.status = 'training';
							
							try {
								const postRes = await uniCloud.callFunction({
									name: 'postCommand',
									data: { 
										task: 'train_voice', 
										params: {
											voiceName: voiceName,
											audioUrl: this.audioUrl
										} 
									}
								});

								if (postRes.result && postRes.result.success) {
									this.startPolling(postRes.result.commandId);
								} else {
									throw new Error(postRes.result.message || '发送训练指令失败');
								}
							} catch (e) {
								uni.showToast({ title: e.message || '请求失败', icon: 'error' });
								this.status = 'idle';
							}
							
						} else if (res.confirm && !res.content) {
							uni.showToast({ title: '名称不能为空', icon: 'none' });
						}
					}
				});
			}
		}
	}
</script>

<style lang="scss">
	.page-container {
		display: flex;
		flex-direction: column;
		height: 100vh;
		/* background is now handled globally in App.vue */
	}

	/* 自定义导航栏 */
	.custom-nav-bar {
		position: relative;
		display: flex;
		justify-content: center;
		align-items: center;
		height: 90rpx;
		padding-top: var(--status-bar-height);
		flex-shrink: 0;
	}

	.back-arrow {
		position: absolute;
		left: 40rpx;
		font-size: 48rpx;
		font-weight: bold;
		color: #000000;
	}

	.nav-title {
		font-size: 36rpx;
		font-weight: bold;
		color: #000000;
	}

	/* 内容区域 */
	.content-section {
		flex: 1;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 40rpx;
	}

	.prompt-title {
		font-size: 36rpx;
		font-weight: bold;
		color: #333;
		margin-bottom: 40rpx;
	}

	.text-card {
		background-color: #FFFFFF;
		border-radius: 20rpx;
		padding: 40rpx;
		width: 100%;
		box-sizing: border-box;
	}

	.text-to-read {
		font-size: 32rpx;
		line-height: 1.8;
		color: #30A681;
		font-weight: bold;
	}

	.status-bar {
		margin-top: 40rpx;
		padding: 20rpx;
		background-color: #eef6ff;
		border-radius: 10rpx;
	}

	.status-text {
		color: #007aff;
		font-size: 28rpx;
	}

	/* 底部按钮 */
	.button-container {
		padding: 40rpx;
		background-color: transparent; /* Let the global background show through */
		flex-shrink: 0;
	}

	.button-bar {
		display: flex;
		justify-content: space-around;
		align-items: center;
		height: 140rpx;
		border-top: 1rpx solid #e7e7e7;
		background-color: #f8f8f8;
		border-radius: 20rpx;
	}

	.bar-button {
		font-size: 30rpx;
		background-color: #FFFFFF;
		border-radius: 40rpx;
		box-shadow: 0 2rpx 6rpx rgba(0,0,0,0.05);
		padding: 15rpx 30rpx;
		min-width: 160rpx;
		text-align: center;
	}

	.record-button {
		color: #FFFFFF;
		background-color: #007aff;
	}

	.bar-button[disabled] {
		background-color: #f0f0f0;
		color: #b0b0b0;
	}
</style>
