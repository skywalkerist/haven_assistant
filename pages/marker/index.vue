<template>
	<view class="page-container">
		<!-- 全屏加载动画 -->
		<view v-if="isLoading" class="loading-overlay">
			<view class="loading-spinner"></view>
			<text class="loading-text">{{ loadingText }}</text>
		</view>

		<!-- 主内容区 -->
		<view class="main-content">
			<view class="left-panel">
				<image class="robot-image" src="/static/robot.png" mode="aspectFit"></image>
				<button class="action-button add-button" @click="openAddModal">添加点位</button>
			</view>
			<view class="right-panel">
				<view class="marker-list-header">
					<text class="list-title">点位列表 ({{ markers.length }})</text>
					<button class="action-button refresh-button" @click="fetchMarkerList">刷新</button>
				</view>
				<scroll-view scroll-y class="marker-list">
					<view v-if="markers.length === 0 && !isLoading" class="empty-list">
						<text>暂无点位信息</text>
					</view>
					<view v-for="(marker, index) in markers" :key="index" class="marker-item">
						<text class="marker-name">{{ marker.name }}</text>
						<button class="action-button delete-button" @click="openDeleteModal(marker)">删除</button>
					</view>
				</scroll-view>
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
	.page-container {
		display: flex;
		flex-direction: column;
		height: 100vh;
		background-color: #f4f7fa;
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

	.main-content {
		display: flex;
		flex: 1;
		padding: 20px;
	}

	.left-panel {
		flex: 1;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding-right: 20px;
	}

	.robot-image {
		width: 150px;
		height: 150px;
		margin-bottom: 30px;
	}

	.right-panel {
		flex: 1;
		display: flex;
		flex-direction: column;
		background-color: white;
		border-radius: 10px;
		box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
		overflow: hidden;
	}

	.marker-list-header {
		padding: 15px;
		border-bottom: 1px solid #eee;
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.list-title {
		font-size: 18px;
		font-weight: bold;
		color: #333;
	}

	.marker-list {
		flex: 1;
	}

	.empty-list {
		display: flex;
		justify-content: center;
		align-items: center;
		height: 100%;
		color: #999;
	}

	.marker-item {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 15px;
		border-bottom: 1px solid #f0f0f0;
	}

	.marker-name {
		font-size: 16px;
	}

	.action-button {
		font-size: 14px;
		padding: 5px 15px;
		border-radius: 20px;
		color: white;
		margin: 0;
	}

	.add-button {
		background-color: #2979ff;
	}
	
	.refresh-button {
		background-color: #4caf50;
		font-size: 12px;
		padding: 4px 12px;
	}

	.delete-button {
		background-color: #ff5252;
		font-size: 12px;
		padding: 4px 12px;
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
		padding: 10px;
		width: 100%;
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
