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
			<text class="nav-title">添加路线</text>
		</view>

		<!-- 2. 新增路线区域 -->
		<view class="new-route-section">
			<text class="section-title">新增路线</text>
			<view v-if="selectedPoints.length === 0" class="empty-prompt">
				请至少添加两个点位
			</view>
			<view v-else class="selected-points-container">
				<view class="selected-point-card" v-for="(point, index) in selectedPoints" :key="index">
					<text class="point-order">{{ index + 1 }}</text>
					<view class="point-info">
						<text class="point-name">{{ point.name }}</text>
						<text class="point-location">{{ point.location }}</text>
					</view>
					<button class="delete-button" @click="removePointFromRoute(index)">删除</button>
				</view>
			</view>
		</view>

		<!-- 3. 点位选择区域 -->
		<view class="point-selection-section">
			<text class="section-title">点位选择</text>
			<view v-if="availablePoints.length === 0 && !isLoading" class="empty-points-prompt">
				<text>暂无可用点位，请先在点位设置中添加点位</text>
			</view>
			<view v-else class="available-points-grid">
				<view class="available-point-card" v-for="(point, index) in availablePoints" :key="index">
					<image src="/static/icon_positon.png" class="point-icon" mode="aspectFit"></image>
					<view class="point-info">
						<text class="point-name">{{ point.name }}</text>
						<text class="point-location">{{ point.location }}</text>
					</view>
					<button class="add-button" @click="addPointToRoute(index)">添加</button>
				</view>
			</view>
		</view>

		<!-- 4. 确认按钮 -->
		<view class="confirm-button-container">
			<button class="confirm-button" :disabled="selectedPoints.length < 2" @click="confirmAddRoute">确定添加</button>
		</view>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				availablePoints: [],
				selectedPoints: [],
				isLoading: false,
				loadingText: '加载中...',
				pollingInterval: null
			};
		},
		onLoad() {
			// 从云端获取可用点位
			this.loadAvailablePoints();
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
			
			// 从云端获取可用点位
			async loadAvailablePoints() {
				try {
					const result = await this.executeCommand('get_marker_list', {}, '正在获取点位列表...');
					// 将结果转换为数组格式
					this.availablePoints = result ? Object.keys(result).map(key => ({ 
						name: key, 
						location: key, // 使用点位名称作为位置显示
						...result[key] 
					})) : [];
					
					// 如果没有点位，显示提示
					if (this.availablePoints.length === 0) {
						uni.showToast({ title: '暂无点位，请先在点位设置中添加', icon: 'none' });
					}
				} catch (error) {
					console.error('获取点位列表失败:', error);
					// 如果获取失败，尝试从本地存储获取（备用方案）
					const storedPoints = uni.getStorageSync('points');
					if (storedPoints) {
						this.availablePoints = storedPoints;
					} else {
						uni.showToast({ title: `获取点位失败: ${error.message}`, icon: 'none' });
					}
				}
			},
			
			addPointToRoute(index) {
				const point = this.availablePoints.splice(index, 1)[0];
				this.selectedPoints.push(point);
			},
			removePointFromRoute(index) {
				const point = this.selectedPoints.splice(index, 1)[0];
				this.availablePoints.push(point);
			},
			async confirmAddRoute() {
				if (this.selectedPoints.length < 2) {
					uni.showToast({
						title: '请至少选择两个点位',
						icon: 'none'
					});
					return;
				}

				try {
					const newRoute = {
						name: `路线 ${Date.now()}`, // 使用时间戳确保唯一性
						description: '自定义路线',
						points: this.selectedPoints
					};

					// 调用云端保存路线
					await this.executeCommand('save_patrol_route', { route: newRoute }, '正在保存路线...');
					
					uni.showToast({
						title: '路线保存成功',
						icon: 'success'
					});

					setTimeout(() => {
						uni.navigateBack();
					}, 1500);
					
				} catch (error) {
					console.error('保存路线失败:', error);
					uni.showToast({
						title: `保存失败: ${error.message}`,
						icon: 'none'
					});
				}
			}
		}
	}
</script>

<style>
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
		background: linear-gradient(to bottom, #49C6A7, #F4F4F4 30%);
		height: 100vh;
	}
	.custom-nav-bar {
		position: relative;
		display: flex;
		justify-content: center;
		align-items: center;
		height: 90rpx;
		padding-top: var(--status-bar-height);
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
	.section-title {
		font-size: 36rpx;
		font-weight: bold;
		margin-bottom: 30rpx;
		color: #000000;
	}
	.new-route-section {
		padding: 20rpx 40rpx;
	}
	.empty-prompt {
		color: #666;
		text-align: center;
		padding: 40rpx 0;
	}
	.selected-points-container {
		display: flex;
		flex-wrap: wrap;
		gap: 20rpx;
	}
	.selected-point-card {
		background-color: #FFF;
		border-radius: 20rpx;
		padding: 20rpx;
		display: flex;
		align-items: center;
		gap: 20rpx;
	}
	.point-order {
		font-size: 60rpx;
		font-weight: bold;
		color: #E0E0E0;
	}
	.point-info {
		display: flex;
		flex-direction: column;
	}
	.point-name {
		font-size: 30rpx;
		font-weight: bold;
	}
	.point-location {
		font-size: 24rpx;
		color: #999;
	}
	.delete-button {
		background-color: #FF4D4F;
		color: #FFF;
		font-size: 24rpx;
		padding: 5rpx 15rpx;
		border-radius: 20rpx;
		border: none;
	}
	.point-selection-section {
		flex: 1;
		background-color: #F4F4F4;
		border-top-left-radius: 40rpx;
		border-top-right-radius: 40rpx;
		padding: 40rpx;
		margin-top: 20rpx;
		overflow-y: auto;
	}
	.empty-points-prompt {
		display: flex;
		justify-content: center;
		align-items: center;
		height: 200rpx;
		color: #999;
		text-align: center;
	}
	.available-points-grid {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		gap: 30rpx;
	}
	.available-point-card {
		background-color: #FFF;
		border-radius: 20rpx;
		padding: 20rpx;
		display: flex;
		align-items: center;
		gap: 20rpx;
	}
	.point-icon {
		width: 60rpx;
		height: 60rpx;
	}
	.add-button {
		background-color: #28a745;
		color: #FFF;
		font-size: 24rpx;
		padding: 5rpx 15rpx;
		border-radius: 20rpx;
		border: none;
	}
	.confirm-button-container {
		padding: 20rpx 40rpx;
		background-color: #F4F4F4;
	}
	.confirm-button {
		background-color: #28a745;
		color: #FFF;
		font-size: 36rpx;
		border-radius: 50rpx;
		height: 100rpx;
		line-height: 100rpx;
	}
	.confirm-button[disabled] {
		background-color: #A9D4B5;
		color: #E0E0E0;
	}
</style>