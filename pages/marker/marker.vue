<template>
	<view class="container">
		<!-- 左侧控制区域 -->
		<view class="control-panel">
			<button type="primary" @click="promptAddMarker">设定目标点</button>
		</view>

		<!-- 右侧列表区域 -->
		<view class="list-panel">
			<view class="list-header">目标点列表</view>
			<scroll-view scroll-y="true" class="marker-list">
				<view v-for="(marker, index) in markers" :key="index" class="marker-item">
					<text>{{ marker.name }}</text>
					<button class="move-button" size="mini" @click="move_to_marker(marker.name)">移动</button>
				</view>
				<view v-if="markers.length === 0" class="empty-list">
					暂无目标点
				</view>
			</scroll-view>
			<button class="refresh-button" @click="fetchMarkers">刷新列表</button>
		</view>

		<!-- 添加点位弹窗 -->
		<view class="popup" v-if="popupVisible">
			<view class="popup-content">
				<view class="popup-title">命名目标点</view>
				<input class="popup-input" v-model="newMarkerName" placeholder="请输入名称" />
				<view class="popup-buttons">
					<button class="popup-btn cancel" @click="popupVisible = false">取消</button>
					<button class="popup-btn confirm" @click="addMarker">确定</button>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				markers: [],
				popupVisible: false,
				newMarkerName: ''
			};
		},
		onShow() {
			this.fetchMarkers();
		},
		methods: {
			// 弹出输入框
			promptAddMarker() {
				this.newMarkerName = '';
				this.popupVisible = true;
			},
			
			// 添加目标点指令
			async addMarker() {
				if (!this.newMarkerName.trim()) {
					uni.showToast({ title: '名称不能为空', icon: 'none' });
					return;
				}
				this.popupVisible = false;
				uni.showLoading({ title: '设定中...' });
				try {
					const commandId = await this.sendCommand('add_marker', { name: this.newMarkerName });
					const result = await this.pollCommandStatus(commandId);
					if (result.status === 'completed') {
						uni.showToast({ title: '添加成功', icon: 'success' });
						this.fetchMarkers(); // 添加成功后刷新列表
					} else {
						throw new Error('添加失败');
					}
				} catch (err) {
					uni.showToast({ title: err.message || '添加失败', icon: 'none' });
				} finally {
					uni.hideLoading();
				}
			},

			// 移动到目标点指令
			async move_to_marker(name) {
				uni.showLoading({ title: '正在移动...' });
				try {
					const commandId = await this.sendCommand('move_to_marker', { name: name });
					// 对于移动指令，我们只发送，不等待结果，可以根据需要修改
					uni.showToast({ title: '移动指令已发送', icon: 'success' });
				} catch (err) {
					uni.showToast({ title: err.message || '指令发送失败', icon: 'none' });
				} finally {
					uni.hideLoading();
				}
			},

			// 获取目标点列表
			async fetchMarkers() {
				uni.showLoading({ title: '正在获取列表...' });
				try {
					const commandId = await this.sendCommand('get_marker_list', {});
					const result = await this.pollCommandStatus(commandId);
					if (result.status === 'completed' && result.result) {
						this.markers = result.result || [];
						uni.showToast({ title: '列表已刷新', icon: 'success' });
					} else {
						throw new Error('获取列表失败');
					}
				} catch (err) {
					uni.showToast({ title: err.message || '获取列表失败', icon: 'none' });
				} finally {
					uni.hideLoading();
				}
			},

			// 通用发送指令函数, 返回 commandId
			sendCommand(command, params) {
				return new Promise((resolve, reject) => {
					uniCloud.callFunction({
						name: 'sendRobotCommand',
						data: { command, params }
					}).then(res => {
						if (res.result && res.result.success) {
							resolve(res.result.commandId);
						} else {
							reject(new Error(res.result.message || '指令发送失败'));
						}
					}).catch(err => {
						reject(new Error(err.message || '指令发送失败'));
					});
				});
			},

			// 轮询指令状态
			pollCommandStatus(commandId, timeout = 30000, interval = 3000) {
				return new Promise((resolve, reject) => {
					const startTime = Date.now();

					const checkStatus = async () => {
						if (Date.now() - startTime > timeout) {
							reject(new Error('获取指令结果超时'));
							return;
						}

						try {
							const res = await uniCloud.callFunction({
								name: 'getCommandStatus',
								data: { commandId }
							});

							if (res.result && res.result.success) {
								const command = res.result.command;
								if (command.status === 'completed' || command.status === 'failed') {
									resolve(command);
								} else {
									// 如果状态是 pending 或 processing，继续轮询
									setTimeout(checkStatus, interval);
								}
							} else {
								// 如果获取状态本身失败，则停止
								reject(new Error(res.result.message || '查询状态失败'));
							}
						} catch (err) {
							reject(new Error(err.message || '查询状态时发生网络错误'));
						}
					};

					setTimeout(checkStatus, interval); // 第一次查询
				});
			}
		}
	};
</script>

<style>
.container {
	display: flex;
	flex-direction: row;
	height: 100vh;
}
.control-panel {
	width: 40%;
	padding: 20px;
	display: flex;
	justify-content: center;
	align-items: center;
	border-right: 1px solid #e0e0e0;
}
.list-panel {
	width: 60%;
	display: flex;
	flex-direction: column;
}
.list-header {
	font-size: 18px;
	font-weight: bold;
	text-align: center;
	padding: 15px;
	border-bottom: 1px solid #e0e0e0;
}
.marker-list {
	flex: 1;
}
.marker-item {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 15px;
	border-bottom: 1px solid #f0f0f0;
}
.move-button {
	margin-left: 10px;
}
.empty-list {
	text-align: center;
	color: #999;
	margin-top: 50px;
}
.refresh-button {
	margin: 10px;
}
.popup {
	position: fixed;
	top: 0;
	left: 0;
	width: 100%;
	height: 100%;
	background-color: rgba(0, 0, 0, 0.5);
	display: flex;
	justify-content: center;
	align-items: center;
}
.popup-content {
	background-color: white;
	padding: 20px;
	border-radius: 10px;
	width: 80%;
}
.popup-title {
	font-size: 18px;
	text-align: center;
	margin-bottom: 20px;
}
.popup-input {
	border: 1px solid #ccc;
	border-radius: 5px;
	padding: 10px;
	margin-bottom: 20px;
}
.popup-buttons {
	display: flex;
	justify-content: space-between;
}
.popup-btn {
	width: 48%;
}
.cancel {
	background-color: #f0f0f0;
}
.confirm {
	background-color: #007aff;
	color: white;
}
</style>
