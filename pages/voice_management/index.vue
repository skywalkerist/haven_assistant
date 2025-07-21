<template>
	<view class="page-container">
		<!-- 全屏加载动画 -->
		<view v-if="isLoading" class="loading-overlay">
			<view class="loading-spinner"></view>
			<text class="loading-text">{{ loadingText }}</text>
		</view>

		<!-- 错误状态 -->
		<view v-if="status === 'error'" class="status-handler">
			<text class="error-message">{{ errorMessage }}</text>
			<button class="retry-button" @click="fetchVoices">点击重试</button>
		</view>

		<!-- 主内容区 -->
		<view v-else class="content">
			<view class="tip">
				<text>轻点卡片，即可选择您喜欢的默认音色</text>
			</view>
			
			<view class="voice-grid">
				<view 
					v-for="voice in voiceList" 
					:key="voice.name" 
					class="voice-card"
					:class="{ 'is-default': voice.isDefault }"
					@click="selectVoice(voice)">
					
					<view v-if="voice.isDefault" class="default-badge">默认</view>
					
					<text class="voice-name">{{ voice.name }}</text>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				status: 'loading', // loading, success, error
				errorMessage: '',
				voiceList: [],
				isLoading: false,
				loadingText: '加载中...',
				pollingInterval: null
			};
		},
		onLoad() {
			this.fetchVoices();
		},
		onUnload() {
			if (this.pollingInterval) {
				clearInterval(this.pollingInterval);
			}
		},
		methods: {
			async executeCommand(task, params = {}, loadingText = '处理中...') {
				this.isLoading = true;
				this.loadingText = loadingText;

				if (this.pollingInterval) {
					clearInterval(this.pollingInterval);
				}

				try {
					const postRes = await uniCloud.callFunction({
						name: 'postCommand',
						data: { task, params }
					});

					if (!postRes.result.success) {
						throw new Error(postRes.result.errMsg || '提交指令失败');
					}
					const commandId = postRes.result.commandId;

					return new Promise((resolve, reject) => {
						const timeout = setTimeout(() => {
							clearInterval(this.pollingInterval);
							this.isLoading = false;
							reject(new Error('请求超时，请稍后重试'));
						}, 20000);

						this.pollingInterval = setInterval(async () => {
							try {
								const resultRes = await uniCloud.callFunction({
									name: 'getCommandResult',
									data: { commandId }
								});

								if (resultRes.result.success && resultRes.result.command) {
									const command = resultRes.result.command;
									if (command.status === 'completed') {
										clearInterval(this.pollingInterval);
										clearTimeout(timeout);
										this.isLoading = false;
										resolve(command.result);
									} else if (command.status === 'failed') {
										clearInterval(this.pollingInterval);
										clearTimeout(timeout);
										this.isLoading = false;
										reject(new Error(command.error_message || '任务执行失败'));
									}
								} else if (!resultRes.result.success) {
									throw new Error(resultRes.result.errMsg || '查询结果失败');
								}
							} catch (pollError) {
								clearInterval(this.pollingInterval);
								clearTimeout(timeout);
								this.isLoading = false;
								reject(pollError);
							}
						}, 2000);
					});
				} catch (error) {
					this.isLoading = false;
					uni.showToast({ title: error.message, icon: 'none' });
					return Promise.reject(error);
				}
			},

			async fetchVoices() {
				this.status = 'loading';
				try {
					const result = await this.executeCommand('get_voices_config', {}, '正在获取音色列表...');
					if (result && result.fileContent) {
						const config = JSON.parse(result.fileContent);
						const defaultVoiceId = config.default;
						let defaultVoiceName = '';

						// 找出默认音色的名字
						for (const name in config) {
							if (config[name] === defaultVoiceId && name !== 'default') {
								defaultVoiceName = name;
								break;
							}
						}

						// 转换数据结构用于渲染
						this.voiceList = Object.keys(config)
							.filter(key => key !== 'default')
							.map(name => ({
								name: name,
								res_id: config[name],
								isDefault: name === defaultVoiceName
							}));
							
						this.status = 'success';
					} else {
						throw new Error('未能获取到配置文件内容');
					}
				} catch (err) {
					this.status = 'error';
					this.errorMessage = err.message;
					console.error('fetchVoices error:', err);
				}
			},

			async selectVoice(voice) {
				if (voice.isDefault || this.isLoading) {
					return; // 如果已经是默认或者正在加载，则不执行任何操作
				}

				try {
					await this.executeCommand(
						'set_voices_config', 
						{ default_voice: voice.name }, 
						`正在将默认音色设为 ${voice.name}...`
					);
					
					uni.showToast({ title: '设置成功', icon: 'success' });

					// 更新本地列表的默认状态
					this.voiceList.forEach(v => {
						v.isDefault = (v.name === voice.name);
					});

				} catch (err) {
					uni.showToast({ title: `设置失败: ${err.message}`, icon: 'none' });
					console.error('selectVoice error:', err);
				}
			}
		}
	}
</script>

<style scoped>
	.page-container {
		padding: 30rpx;
		background-color: #f7f8fa;
		min-height: 100vh;
	}
	.status-handler {
		display: flex;
		flex-direction: column;
		justify-content: center;
		align-items: center;
		padding-top: 200rpx;
	}
	.error-message {
		color: #dd524d;
		margin-bottom: 40rpx;
	}
	.retry-button {
		width: 300rpx;
	}
	.tip {
		font-size: 28rpx;
		color: #666;
		margin-bottom: 40rpx;
		text-align: center;
	}
	
	.voice-grid {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		gap: 30rpx;
	}
	
	.voice-card {
		position: relative;
		display: flex;
		justify-content: center;
		align-items: center;
		height: 180rpx;
		background-color: #ffffff;
		border-radius: 20rpx;
		box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.08);
		border: 4rpx solid transparent;
		transition: all 0.2s ease-in-out;
	}
	
	.voice-card.is-default {
		border-color: #007AFF;
		box-shadow: 0 8rpx 20rpx rgba(0, 122, 255, 0.2);
	}
	
	.voice-name {
		font-size: 36rpx;
		font-weight: 500;
		color: #333;
	}
	
	.default-badge {
		position: absolute;
		top: 0;
		right: 0;
		background-color: #007AFF;
		color: white;
		padding: 4rpx 12rpx;
		border-top-right-radius: 20rpx;
		border-bottom-left-radius: 20rpx;
		font-size: 22rpx;
	}

	/* 加载动画样式 */
	.loading-overlay {
		position: fixed;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
		background-color: rgba(0, 0, 0, 0.5);
		display: flex;
		flex-direction: column;
		justify-content: center;
		align-items: center;
		z-index: 1000;
	}
	.loading-spinner {
		border: 4px solid #f3f3f3;
		border-top: 4px solid #3498db;
		border-radius: 50%;
		width: 40px;
		height: 40px;
		animation: spin 1s linear infinite;
	}
	.loading-text {
		color: white;
		margin-top: 15px;
		font-size: 16px;
	}
	@keyframes spin {
		0% { transform: rotate(0deg); }
		100% { transform: rotate(360deg); }
	}
</style>
