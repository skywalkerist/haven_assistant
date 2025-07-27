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
			<text class="nav-title">安防巡逻</text>
		</view>

		<!-- 2. 路线选择 -->
		<view class="route-selection-section">
			<text class="section-title">路线选择</text>
			<view class="route-grid">
				<view class="route-card" v-for="(route, index) in routes" :key="index" @click="renameRoute(index)">
					<view class="route-info">
						<text class="route-name">{{ route.name }}</text>
						<text class="route-description">{{ route.description }}</text>
					</view>
					<view class="route-actions">
						<button class="start-button" @click.stop="startPatrol(index)">开始</button>
						<button class="delete-button" @click.stop="deleteRoute(index)">删除</button>
					</view>
				</view>
			</view>
		</view>

		<!-- 3. 添加路线按钮 -->
		<view class="add-route-button-container">
			<button class="stop-patrol-button" @click="stopPatrol">停止巡逻</button>
			<button class="add-route-button" @click="addRoute">添加路线</button>
		</view>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				routes: [],
				isLoading: false,
				loadingText: '加载中...',
				pollingInterval: null
			};
		},
		onLoad() {
			this.loadRoutes();
			this.updateRoutesHandler = () => {
				this.loadRoutes();
			};
		},
		onShow() {
			// 在页面每次显示时重新加载数据并监听事件
			this.loadRoutes();
			uni.$on('routes-updated', this.updateRoutesHandler);
		},
		onHide() {
			// 在页面隐藏时移除监听，避免重复注册
			uni.$off('routes-updated', this.updateRoutesHandler);
		},
		onUnload() {
			// 在页面卸载时彻底移除监听器
			uni.$off('routes-updated', this.updateRoutesHandler);
			// 页面卸载时清除定时器
			if (this.pollingInterval) {
				clearInterval(this.pollingInterval);
			}
		},
		methods: {
			goBack() {
				uni.navigateBack();
			},
			
			// 核心逻辑：提交任务并等待结果
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
			async loadRoutes() {
				try {
					// 从云端获取巡逻路线
					const result = await this.executeCommand('get_patrol_routes', {}, '正在获取巡逻路线...');
					if (result && result.fileContent) {
						const config = JSON.parse(result.fileContent);
						this.routes = config.routes || [];
					} else {
						this.routes = [];
					}
				} catch (error) {
					console.error('获取巡逻路线失败:', error);
					// 如果获取失败，尝试从本地存储获取（备用方案）
					const storedRoutes = uni.getStorageSync('patrol_routes');
					if (storedRoutes && storedRoutes.length > 0) {
						this.routes = storedRoutes;
					} else {
						this.routes = [];
						uni.showToast({ title: `获取路线失败: ${error.message}`, icon: 'none' });
					}
				}
			},
			async startPatrol(index) {
				const route = this.routes[index];
				if (!route.points || route.points.length < 2) {
					uni.showToast({
						title: '该路线点位不足，无法启动巡逻',
						icon: 'none'
					});
					return;
				}
				
				try {
					// 调用云端开始巡逻
					await this.executeCommand('start_patrol', { route_id: route.id }, `正在启动巡逻路线: ${route.name}...`);
					uni.showToast({
						title: `${route.name} 巡逻已启动`,
						icon: 'success'
					});
				} catch (error) {
					console.error('启动巡逻失败:', error);
					uni.showToast({
						title: `启动失败: ${error.message}`,
						icon: 'none'
					});
				}
			},
			addRoute() {
				uni.navigateTo({
					url: '/pages/patrol/add'
				});
			},
			renameRoute(index) {
				// 暂时保留原有功能，后续可以实现云端重命名
				uni.showModal({
					title: '查看路线详情',
					content: `路线名称: ${this.routes[index].name}\n点位数量: ${this.routes[index].points ? this.routes[index].points.length : 0}`,
					showCancel: false
				});
			},
			deleteRoute(index) {
				// 暂时保留原有删除功能
				uni.showModal({
					title: '确认删除',
					content: `您确定要删除路线 "${this.routes[index].name}" 吗？`,
					success: (res) => {
						if (res.confirm) {
							this.routes.splice(index, 1);
							// TODO: 实现云端删除功能
							uni.showToast({
								title: '删除成功',
								icon: 'success'
							});
						}
					}
				});
			},
			async stopPatrol() {
				try {
					// 调用云端停止巡逻
					await this.executeCommand('stop_patrol', {}, '正在停止巡逻...');
					uni.showToast({
						title: '巡逻已停止',
						icon: 'success'
					});
				} catch (error) {
					console.error('停止巡逻失败:', error);
					uni.showToast({
						title: `停止失败: ${error.message}`,
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
		background: linear-gradient(to bottom, #49C6A7, #F4F4F4 50%);
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
		padding-top: var(--status-bar-height);
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

	/* 路线选择 */
	.route-selection-section {
		padding: 40rpx;
		flex: 1;
		overflow-y: auto;
	}
	.section-title {
		font-size: 36rpx;
		font-weight: bold;
		margin-bottom: 30rpx;
		color: #000000;
	}
	.route-grid {
		display: flex;
		flex-direction: column;
		gap: 30rpx;
	}
	.route-card {
		background-color: #FFFFFF;
		border-radius: 20rpx;
		padding: 30rpx;
		display: flex;
		justify-content: space-between;
		align-items: center;
	}
	.route-info {
		display: flex;
		flex-direction: column;
		flex: 1;
	}
	.route-actions {
		display: flex;
		flex-direction: row;
		align-items: center;
		gap: 20rpx;
	}
	.delete-button {
		background-color: #FF4D4F;
		color: #FFFFFF;
		font-size: 24rpx;
		padding: 5rpx 20rpx;
		border-radius: 30rpx;
		line-height: 1.5;
		border: none;
	}
	.route-name {
		font-size: 32rpx;
		font-weight: bold;
	}
	.route-description {
		font-size: 24rpx;
		color: #999;
		margin-top: 5rpx;
	}
	.start-button {
		background-color: #28a745;
		color: #FFFFFF;
		font-size: 28rpx;
		padding: 10rpx 30rpx;
		border-radius: 30rpx;
		line-height: 1.5;
		border: none;
	}

	/* 添加路线按钮 */
	.add-route-button-container {
		padding: 40rpx;
		background-color: #F4F4F4;
		display: flex;
		gap: 20rpx;
	}
	.stop-patrol-button {
		background-color: #FF4D4F;
		color: #FFFFFF;
		font-size: 36rpx;
		font-weight: bold;
		border-radius: 50rpx;
		height: 100rpx;
		line-height: 100rpx;
		text-align: center;
		flex: 1;
	}
	.add-route-button {
		background-color: #28a745;
		color: #FFFFFF;
		font-size: 36rpx;
		font-weight: bold;
		border-radius: 50rpx;
		height: 100rpx;
		line-height: 100rpx;
		text-align: center;
		flex: 1;
	}
</style>