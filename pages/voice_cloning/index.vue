<template>
	<view class="page-container">
		<view class="content-wrapper">
			<text class="title">请朗读下面的话</text>
			<view class="text-box">
				<text class="paragraph">森林中有一棵魔法苹果树，据说吃了它结的苹果可以实现一个愿望，许多小动物都悄悄来到这里，希望愿望成真。</text>
			</view>
			<view class="status-bar" v-if="status !== 'idle'">
				<text class="status-text">{{ statusText }}</text>
			</view>
		</view>
		<view class="button-bar">
			<button class="bar-button" @click="play" :disabled="!audioUrl || status !== 'idle'">
				{{ status === 'playing' ? '播放中...' : '播放录音' }}
			</button>
			<button class="bar-button record-button" @click="record" :loading="status === 'recording'" :disabled="status !== 'idle'">
				录制声音
			</button>
			<button class="bar-button" @click="startTraining" :disabled="!audioUrl || status !== 'idle'">开始训练</button>
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
				pollingTimer: null
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
			async record() {
				this.status = 'recording';
				this.audioUrl = null; // 清除旧的录音

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
								uni.showToast({ title: '录音成功！', icon: 'success' });
							} else if (command.task === 'train_voice') {
								uni.showToast({ title: '声音训练成功！', icon: 'success' });
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
			play() {
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

<style>
	.page-container {
		display: flex;
		flex-direction: column;
		height: 100vh;
		background-color: #FFFFFF;
	}
	.content-wrapper {
		flex: 1;
		padding: 60rpx 40rpx;
		display: flex;
		flex-direction: column;
		align-items: center;
	}
	.title {
		font-size: 40rpx;
		font-weight: bold;
		margin-bottom: 40rpx;
	}
	.text-box {
		width: 100%;
		background-color: #f8f8f8;
		border-radius: 20rpx;
		padding: 40rpx;
	}
	.paragraph {
		font-size: 32rpx;
		line-height: 1.6;
		color: #333;
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
	.button-bar {
		display: flex;
		justify-content: space-around;
		align-items: center;
		height: 140rpx;
		border-top: 1rpx solid #e7e7e7;
		background-color: #f8f8f8;
	}
	.bar-button {
		font-size: 30rpx;
		background-color: #FFFFFF;
		border-radius: 40rpx;
		box-shadow: 0 2rpx 6rpx rgba(0,0,0,0.05);
	}
	.record-button {
		color: #FFFFFF;
		background-color: #007aff; /* A primary color for the main action */
	}
	.bar-button[disabled] {
		background-color: #f0f0f0;
		color: #b0b0b0;
	}
</style>
