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
			<text class="nav-title">物品配送</text>
		</view>

		<!-- 2. 当前区域 -->
		<view class="current-area-section">
			<text class="area-label">当前区域</text>
			<text class="area-name">老年活动室</text>
		</view>

		<!-- 3. 目的地设置 -->
		<view class="point-management-section">
			<text class="section-title">目的地设置</text>
			<view v-if="points.length === 0 && !isLoading" class="empty-prompt">
				<text>暂无点位信息，请先在点位设置中添加点位</text>
			</view>
			<view v-else class="point-grid">
				<view class="point-card" v-for="(point, index) in points" :key="index">
					<image src="/static/icon_positon.png" class="point-icon" mode="aspectFit"></image>
					<view class="point-info">
						<text class="point-name">{{ point.name }}</text>
						<text class="point-location">{{ point.location }}</text>
						<button class="delivery-button" @click.stop="sendDelivery(index)">配送</button>
					</view>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				points: [],
				isLoading: false,
				loadingText: '加载中...',
				pollingInterval: null
			};
		},
		onShow() {
			this.loadPoints();
		},
		onUnload() {
			// 页面卸载时清除定时器
			if (this.pollingInterval) {
				clearInterval(this.pollingInterval);
			}
		},
		methods: {
			goBack() {
				uni.navigateBack();
			},
			
			// 核心逻辑：提交任务并等待结果（参考点位设置页面）
			async executeCommand(task, params = {}, loadingText = '处理中...') {
				this.isLoading = true;
				this.loadingText = loadingText;

				// 清除上一个定时器，防止多个定时器同时运行
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
						}, 20000); // 20秒超时

						this.pollingInterval = setInterval(async () => {
							try {
								const resultRes = await uniCloud.callFunction({
									name: 'getCommandResult',
									data: {
										commandId
									}
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
									// 如果是 pending 或 processing，则继续轮询
								} else if (!resultRes.result.success) {
									// 查询本身失败
									throw new Error(resultRes.result.errMsg || '查询结果失败');
								}
							} catch (pollError) {
								clearTimeout(timeoutTimer);
								clearInterval(this.pollingInterval);
								this.isLoading = false;
								reject(pollError);
							}
						}, 2000); // 每2秒查询一次
					});
				} catch (error) {
					this.isLoading = false;
					uni.showToast({ title: error.message, icon: 'none' });
					return Promise.reject(error);
				}
			},
			
			// 从云端获取点位列表
			async loadPoints() {
				try {
					const result = await this.executeCommand('get_marker_list', {}, '正在获取点位列表...');
					// 将结果转换为数组格式
					this.points = result ? Object.keys(result).map(key => ({ 
						name: key, 
						location: key, // 使用点位名称作为位置显示
						...result[key] 
					})) : [];
					
					// 如果没有点位，显示提示
					if (this.points.length === 0) {
						uni.showToast({ title: '暂无点位，请先在点位设置中添加', icon: 'none' });
					}
				} catch (error) {
					console.error('获取点位列表失败:', error);
					// 如果获取失败，尝试从本地存储获取（备用方案）
					const storedPoints = uni.getStorageSync('points');
					if (storedPoints) {
						this.points = storedPoints;
					} else {
						uni.showToast({ title: `获取点位失败: ${error.message}`, icon: 'none' });
					}
				}
			},
			
			async sendDelivery(index) {
				const point = this.points[index];
				try {
					// 发送移动到指定点位的任务
					await this.executeCommand('move_to_point', { marker_name: point.name }, `正在移动至 ${point.name}...`);
					uni.showToast({
						title: `已成功配送至 ${point.name}`,
						icon: 'success'
					});
				} catch (error) {
					console.error('配送失败:', error);
					uni.showToast({
						title: `配送失败: ${error.message}`,
						icon: 'none'
					});
				}
			}
		}
	}
</script>

<style>
	page {
		height: 100%;
	}
	
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
	
	.page-container {
		display: flex;
		flex-direction: column;
		background-image: url('/static/background.png');
		background-size: cover;
		background-repeat: no-repeat;
		background-position: center;
		height: 100vh;
		color: #333;
	}

	/* 自定义导航栏 */
	.custom-nav-bar {
		position: relative;
		display: flex;
		justify-content: center;
		align-items: center;
		height: 90rpx;
		padding-top: var(--status-bar-height); /* 适配状态栏 */
	}
	.back-arrow {
		position: absolute;
		left: 40rpx;
		top: 50%;
		transform: translateY(-50%);
		font-size: 48rpx;
		font-weight: bold;
		color: #000000;
	}
	.nav-title {
		font-size: 36rpx;
		font-weight: bold;
		color: #000000;
	}

	/* 当前区域 */
	.current-area-section {
		display: flex;
		flex-direction: column;
		align-items: center;
		padding: 40rpx;
		text-align: center;
	}
	.area-label {
		font-size: 30rpx;
		color: #FFFFFF;
		opacity: 0.9;
	}
	.area-name {
		font-size: 60rpx;
		font-weight: bold;
		color: #FFFFFF;
		margin-top: 10rpx;
	}

	/* 目的地设置 */
	.point-management-section {
		flex: 1;
		background-color: #F4F4F4;
		border-top-left-radius: 40rpx;
		border-top-right-radius: 40rpx;
		padding: 40rpx;
		padding-bottom: calc(40rpx + var(--safe-area-inset-bottom)); /* 适配底部安全区 */
		overflow-y: auto; /* 内容溢出时可滚动 */
		min-height: 0; /* 解决flex布局在某些情况下的溢出问题 */
	}
	.section-title {
		font-size: 36rpx;
		font-weight: bold;
		margin-bottom: 30rpx;
	}
	.empty-prompt {
		display: flex;
		justify-content: center;
		align-items: center;
		height: 200rpx;
		color: #999;
		text-align: center;
	}
	.point-grid {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		gap: 30rpx;
	}
	.point-card {
		background-color: #FFFFFF;
		border-radius: 20rpx;
		padding: 30rpx;
		display: flex;
		align-items: center;
	}
	.point-icon {
		width: 80rpx;
		height: 80rpx;
		margin-right: 20rpx;
	}
	.point-info {
		display: flex;
		flex-direction: column;
	}
	.point-name {
		font-size: 32rpx;
		font-weight: bold;
	}
	.point-location {
		font-size: 24rpx;
		color: #999;
		margin-top: 5rpx;
	}
	.delivery-button {
		margin-top: 10rpx;
		background-color: #28a745; /* Green color */
		color: #FFFFFF;
		font-size: 24rpx;
		padding: 5rpx 20rpx;
		border-radius: 30rpx;
		line-height: 1.5;
		border: none;
		text-align: center;
		display: inline-block;
		width: auto;
		height: auto;
	}
</style>