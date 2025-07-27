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
			<text class="nav-title">点位设置</text>
		</view>

		<!-- 2. 当前区域 -->
		<view class="current-area-section">
			<text class="area-label">当前区域</text>
			<text class="area-name">老年活动室</text>
			<button class="set-point-button" @click="openAddModal">设为新点位</button>
		</view>

		<!-- 3. 点位管理 -->
		<view class="point-management-section">
			<view class="section-header">
				<text class="section-title">点位管理</text>
				<button class="refresh-button" @click="fetchMarkerList">刷新</button>
			</view>
			<view v-if="markers.length === 0 && !isLoading" class="empty-list">
				<text>暂无点位信息</text>
			</view>
			<view v-else class="point-grid">
				<view class="point-card" v-for="(marker, index) in markers" :key="index" @click="renameMarker(marker)">
					<image src="/static/icon_positon.png" class="point-icon" mode="aspectFit"></image>
					<view class="point-info">
						<text class="point-name">{{ marker.name }}</text>
						<text class="point-location">{{ marker.name }}</text>
						<button class="delete-button" @click.stop="openDeleteModal(marker)">删除</button>
					</view>
				</view>
			</view>
		</view>

		<!-- 添加/删除点位弹窗 -->
		<view v-if="isModalVisible" class="modal-overlay" @click.self="closeModal">
			<view class="modal-content">
				<text class="modal-title">{{ modal.title }}</text>
				<input v-if="modal.type === 'add'" v-model="modal.inputText" class="modal-input" placeholder="请输入点位名称" />
				<text v-if="modal.type === 'delete'" class="modal-text">确定要删除点位 "{{ modal.markerName }}" 吗？</text>
				<view class="modal-actions">
					<button class="modal-button cancel-button" @click="closeModal">取消</button>
					<button class="modal-button confirm-button" @click="handleConfirm">确定</button>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				isLoading: false,
				loadingText: '加载中...',
				markers: [],
				isModalVisible: false,
				modal: {
					type: 'add', // 'add' or 'delete'
					title: '',
					inputText: '',
					markerName: ''
				},
				pollingInterval: null
			};
		},
		onLoad() {
			this.fetchMarkerList();
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

			// 获取点位列表
			async fetchMarkerList() {
				try {
					const result = await this.executeCommand('get_marker_list', {}, '正在获取点位列表...');
					// **关键修复**：直接使用返回的 result 对象
					this.markers = result ? Object.keys(result).map(key => ({ name: key, ...result[key] })) : [];
					uni.showToast({ title: '列表已刷新', icon: 'success' });
				} catch (error) {
					uni.showToast({ title: `获取失败: ${error.message}`, icon: 'none' });
				}
			},

			// 弹窗控制
			openAddModal() {
				this.modal = { type: 'add', title: '添加新点位', inputText: '', markerName: '' };
				this.isModalVisible = true;
			},
			openDeleteModal(marker) {
				this.modal = { type: 'delete', title: '删除点位', inputText: '', markerName: marker.name };
				this.isModalVisible = true;
			},
			closeModal() {
				this.isModalVisible = false;
			},

			// 重命名点位（保留原有功能但用移动端交互）
			renameMarker(marker) {
				uni.showModal({
					title: '点位详情',
					content: `点位名称: ${marker.name}`,
					showCancel: false
				});
			},

			// 弹窗确认操作
			async handleConfirm() {
				const modalType = this.modal.type;
				const markerName = modalType === 'add' ? this.modal.inputText : this.modal.markerName;
				this.closeModal();

				if (modalType === 'add') {
					if (!markerName) {
						uni.showToast({ title: '点位名称不能为空', icon: 'none' });
						return;
					}
					try {
						await this.executeCommand('add_marker', { name: markerName }, '正在添加点位...');
						uni.showToast({ title: '添加成功', icon: 'success' });
						await this.fetchMarkerList(); // 成功后刷新列表
					} catch (error) {
						uni.showToast({ title: `添加失败: ${error.message}`, icon: 'none' });
					}
				} else if (modalType === 'delete') {
					try {
						await this.executeCommand('delete_marker', { name: markerName }, '正在删除点位...');
						uni.showToast({ title: '删除成功', icon: 'success' });
						await this.fetchMarkerList(); // 成功后刷新列表
					} catch (error) {
						uni.showToast({ title: `删除失败: ${error.message}`, icon: 'none' });
					}
				}
			}
		}
	};
</script>

<style>
	page {
		height: 100%;
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
	.set-point-button {
		margin-top: 30rpx;
		background-color: #28a745;
		color: #FFFFFF;
		border-radius: 50rpx;
		padding: 15rpx 60rpx;
		font-size: 32rpx;
	}

	/* 点位管理 */
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
	.section-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 30rpx;
	}
	.section-title {
		font-size: 36rpx;
		font-weight: bold;
	}
	.refresh-button {
		background-color: #4caf50;
		color: #FFFFFF;
		font-size: 24rpx;
		padding: 8rpx 20rpx;
		border-radius: 30rpx;
		border: none;
	}
	.empty-list {
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
	.delete-button {
		margin-top: 10rpx;
		background-color: #FF4D4F;
		color: #FFFFFF;
		font-size: 24rpx;
		padding: 5rpx 20rpx;
		border-radius: 30rpx;
		line-height: 1.5;
		/* 重置按钮默认样式 */
		border: none;
		text-align: center;
		display: inline-block;
		width: auto;
		height: auto;
	}

	.modal-overlay {
		position: fixed;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
		background-color: rgba(0, 0, 0, 0.4);
		display: flex;
		justify-content: center;
		align-items: center;
		z-index: 999;
	}

	.modal-content {
		background-color: white;
		padding: 20px;
		border-radius: 10px;
		width: 80%;
		max-width: 400px;
	}

	.modal-title {
		font-size: 18px;
		font-weight: bold;
		display: block;
		text-align: center;
		margin-bottom: 20px;
	}

	.modal-input {
		border: 1px solid #ddd;
		border-radius: 5px;
		padding: 15px;
		width: 100%;
		height: 50px;
		line-height: 20px;
		font-size: 16px;
		box-sizing: border-box;
		margin-bottom: 20px;
	}
	
	.modal-text {
		display: block;
		text-align: center;
		margin-bottom: 20px;
		font-size: 16px;
	}

	.modal-actions {
		display: flex;
		justify-content: space-between;
	}

	.modal-button {
		flex: 1;
		margin: 0 5px;
	}
	
	.confirm-button {
		background-color: #2979ff;
		color: white;
	}
</style>
