<template>
	<view class="page-container">
		<!-- 全屏加载动画 -->
		<view v-if="isLoading" class="loading-overlay">
			<view class="loading-spinner"></view>
			<text class="loading-text">{{ loadingText }}</text>
		</view>

		<!-- 1. 自定义导航栏 -->
		<view class="custom-nav-bar">
			<text class="back-arrow" @click="goBack">&lt;</text>
			<text class="nav-title">人脸录入</text>
		</view>

		<!-- 2. 内容区域 -->
		<view class="content-wrapper">
			<text class="title">请面对摄像头，输入人员姓名</text>
			<input class="name-input" type="text" v-model="name" placeholder="在此输入姓名" />
			<button class="action-button" @click="startRegistration">开始注册人脸</button>
		</view>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				name: '',
				isLoading: false,
				loadingText: '',
				pollingInterval: null
			};
		},
		onUnload() {
			// 确保页面卸载时清除定时器
			if (this.pollingInterval) {
				clearInterval(this.pollingInterval);
			}
		},
		methods: {
			goBack() {
				uni.navigateBack();
			},

			async startRegistration() {
				if (!this.name.trim()) {
					uni.showToast({
						title: '请输入名字',
						icon: 'none'
					});
					return;
				}
				
				try {
					this.loadingText = '正在录入，请正视摄像头\n微微变换脸部角度...';
					await this.executeCommand('register_face', { name: this.name.trim() });
					uni.showToast({
						title: '人脸注册成功！',
						icon: 'success'
					});
				} catch (error) {
					uni.showToast({
						title: `注册失败: ${error.message}`,
						icon: 'none'
					});
				}
			},

			// 核心逻辑：提交任务并等待结果 (与点位设置页面相同)
			async executeCommand(task, params = {}) {
				this.isLoading = true;

				if (this.pollingInterval) {
					clearInterval(this.pollingInterval);
				}

				try {
					// 1. 提交指令
					const postRes = await uniCloud.callFunction({
						name: 'postCommand',
						data: { task, params }
					});

					if (!postRes.result.success) {
						throw new Error(postRes.result.errMsg || '提交指令失败');
					}
					const commandId = postRes.result.commandId;

					// 2. 轮询结果
					return new Promise((resolve, reject) => {
						const timeoutTimer = setTimeout(() => {
							clearInterval(this.pollingInterval);
							this.isLoading = false;
							reject(new Error('请求超时，请检查网络或机器人客户端状态'));
						}, 60000); // 人脸注册可能耗时较长，设置60秒超时

						this.pollingInterval = setInterval(async () => {
							try {
								const resultRes = await uniCloud.callFunction({
									name: 'getCommandResult',
									data: { commandId }
								});

								if (resultRes.result.success && resultRes.result.command) {
									const command = resultRes.result.command;
									if (command.status === 'completed') {
										clearTimeout(timeoutTimer);
										clearInterval(this.pollingInterval);
										this.isLoading = false;
										resolve(command.result);
									} else if (command.status === 'failed') {
										clearTimeout(timeoutTimer);
										clearInterval(this.pollingInterval);
										this.isLoading = false;
										reject(new Error(command.error_message || '任务执行失败'));
									}
								} else if (!resultRes.result.success) {
									throw new Error(resultRes.result.errMsg || '查询结果失败');
								}
							} catch (pollError) {
								clearTimeout(timeoutTimer);
								clearInterval(this.pollingInterval);
								this.isLoading = false;
								reject(pollError);
							}
						}, 3000); // 每3秒查询一次
					});
				} catch (error) {
					this.isLoading = false;
					uni.showToast({ title: error.message, icon: 'none' });
					return Promise.reject(error);
				}
			}
		}
	}
</script>

<style lang="scss">
	.page-container {
		display: flex;
		flex-direction: column;
		min-height: 100vh;
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

	.content-wrapper {
		flex: 1;
		width: 80%;
		margin: 0 auto;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 40rpx 0;
	}

	.title {
		font-size: 36rpx;
		font-weight: bold;
		margin-bottom: 60rpx;
		text-align: center;
		color: #333;
	}

	.name-input {
		width: 100%;
		height: 100rpx;
		background-color: #FFFFFF;
		border-radius: 20rpx;
		padding: 0 40rpx;
		font-size: 32rpx;
		text-align: center;
		margin-bottom: 60rpx;
		box-shadow: 0 2rpx 6rpx rgba(0,0,0,0.05);
		border: 1rpx solid #e0e0e0;
	}

	.action-button {
		width: 100%;
		height: 100rpx;
		line-height: 100rpx;
		font-size: 34rpx;
		color: #FFFFFF;
		background-color: #007aff;
		border-radius: 50rpx;
		font-weight: bold;
	}
	
	/* 加载动画样式 */
	.loading-overlay {
		position: fixed;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
		background-color: rgba(0, 0, 0, 0.6);
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
		text-align: center;
		white-space: pre-wrap; /* 支持换行 */
	}

	@keyframes spin {
		0% { transform: rotate(0deg); }
		100% { transform: rotate(360deg); }
	}
</style>
