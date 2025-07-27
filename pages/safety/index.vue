<template>
	<view class="page-container">
		<!-- 全屏加载动画 -->
		<view v-if="isLoading" class="loading-overlay">
			<view class="loading-spinner"></view>
			<text class="loading-text">{{ loadingText }}</text>
		</view>
		
		<!-- 1. 顶部状态区 -->
		<view class="top-status-section">
			<view class="safety-illustration">
				<image src="/static/icon_safety.png" mode="aspectFit" class="safety-image"></image>
			</view>
			<view class="safety-info-container">
				<text class="info-title">安全状态</text>
				<view class="safety-info-card">
					<view class="status-item" :class="systemStatus.class">
						<text>系统状态: {{ systemStatus.text }}</text>
					</view>
					<view><text>最后检查: {{ lastCheckTime }}</text></view>
					<view><text>在线设备: {{ onlineDevices }}/{{ totalDevices }}</text></view>
				</view>
				<button class="refresh-button" @click="refreshStatus">刷新状态</button>
			</view>
		</view>

		<!-- 2. 安全功能区 -->
		<view class="safety-functions-section">
			<text class="section-title">安全功能</text>
			<view class="function-grid">
				<view class="function-card" v-for="(func, index) in safetyFunctions" :key="index" @click="handleFunctionClick(func.title)">
					<view class="card-text">
						<text class="card-title">{{ func.title }}</text>
						<text class="card-subtitle">{{ func.subtitle }}</text>
					</view>
					<view class="card-icon">
						<image :src="func.icon" class="card-icon-image" mode="aspectFit"></image>
					</view>
				</view>
			</view>
		</view>

		<!-- 3. 报警记录区 -->
		<view class="alert-history-section">
			<view class="alert-header">
				<text class="section-title">报警记录</text>
				<button class="clear-button" @click="clearAlerts">清空</button>
			</view>
			<scroll-view scroll-y class="alert-list">
				<view v-if="alerts.length === 0" class="empty-alerts">
					<text>暂无报警记录</text>
				</view>
				<view v-for="(alert, index) in alerts" :key="index" class="alert-item" :class="alert.level">
					<view class="alert-content">
						<text class="alert-title">{{ alert.title }}</text>
						<text class="alert-time">{{ alert.time }}</text>
					</view>
					<view class="alert-level">
						<text>{{ alert.levelText }}</text>
					</view>
				</view>
			</scroll-view>
		</view>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				isLoading: false,
				loadingText: '加载中...',
				systemStatus: {
					text: '正常',
					class: 'status-normal'
				},
				lastCheckTime: '刚刚',
				onlineDevices: 1,
				totalDevices: 1,
				safetyFunctions: [{
					title: '紧急呼叫',
					subtitle: '一键求助 快速响应',
					icon: '/static/icon_warning.png'
				}, {
					title: '视频监控',
					subtitle: '实时画面 安全保障',
					icon: '/static/icon_safety.png'
				}, {
					title: '环境监测',
					subtitle: '温湿度检测 环境安全',
					icon: '/static/icon_positon.png'
				}, {
					title: '设备检查',
					subtitle: '设备状态 定期巡检',
					icon: '/static/icon_robo.png'
				}],
				alerts: [
					{
						title: '系统启动完成',
						time: '2小时前',
						level: 'info',
						levelText: '信息'
					},
					{
						title: '定时巡检完成',
						time: '1小时前',
						level: 'success',
						levelText: '正常'
					}
				]
			};
		},
		onShow() {
			this.updateTime();
			this.checkSystemStatus();
		},
		methods: {
			refreshStatus() {
				this.isLoading = true;
				this.loadingText = '刷新状态中...';
				
				// 模拟刷新延迟
				setTimeout(() => {
					this.updateTime();
					this.checkSystemStatus();
					this.isLoading = false;
					uni.showToast({
						title: '状态已刷新',
						icon: 'success'
					});
				}, 1500);
			},
			updateTime() {
				const now = new Date();
				const hours = now.getHours().toString().padStart(2, '0');
				const minutes = now.getMinutes().toString().padStart(2, '0');
				this.lastCheckTime = `${hours}:${minutes}`;
			},
			checkSystemStatus() {
				// 模拟系统状态检查
				const statuses = [
					{ text: '正常', class: 'status-normal' },
					{ text: '正常', class: 'status-normal' },
					{ text: '正常', class: 'status-normal' },
					{ text: '注意', class: 'status-warning' }
				];
				this.systemStatus = statuses[Math.floor(Math.random() * statuses.length)];
			},
			handleFunctionClick(title) {
				if (title === '紧急呼叫') {
					uni.showModal({
						title: '紧急呼叫',
						content: '确定要发起紧急呼叫吗？',
						success: (res) => {
							if (res.confirm) {
								this.addAlert('紧急呼叫已发起', 'warning', '紧急');
								uni.showToast({
									title: '紧急呼叫已发送',
									icon: 'success'
								});
							}
						}
					});
				} else if (title === '安防巡逻') {
					uni.navigateTo({
						url: '/pages/patrol/index'
					});
				} else {
					uni.showToast({
						title: `${title}功能开发中`,
						icon: 'none'
					});
				}
			},
			addAlert(title, level, levelText) {
				const now = new Date();
				const timeStr = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;
				
				this.alerts.unshift({
					title,
					time: timeStr,
					level,
					levelText
				});
			},
			clearAlerts() {
				uni.showModal({
					title: '确认清空',
					content: '确定要清空所有报警记录吗？',
					success: (res) => {
						if (res.confirm) {
							this.alerts = [];
							uni.showToast({
								title: '记录已清空',
								icon: 'success'
							});
						}
					}
				});
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
		background-image: url('/static/background.png');
		background-size: cover;
		background-repeat: no-repeat;
		background-position: center;
		min-height: 100vh;
		padding-bottom: 30rpx; /* 减少padding，原生TabBar会自动处理 */
	}

	/* 顶部状态区 */
	.top-status-section {
		display: flex;
		padding: 40rpx 160rpx 40rpx 40rpx;
		align-items: center;
	}
	.safety-illustration {
		flex: 1.2;
		display: flex;
		justify-content: center;
		align-items: center;
	}
	.safety-image {
		width: 320rpx;
		height: 320rpx;
	}
	.safety-info-container {
		flex: 1;
		display: flex;
		flex-direction: column;
		align-items: flex-start;
	}
	.info-title {
		font-size: 32rpx;
		font-weight: bold;
		color: #000000;
		margin-bottom: 10rpx;
	}
	.safety-info-card {
		background-color: rgba(255, 255, 255, 0.5);
		border-radius: 20rpx;
		padding: 20rpx;
		font-size: 26rpx;
		color: #333;
		width: 100%;
	}
	.status-item {
		font-weight: bold;
	}
	.status-normal {
		color: #28a745;
	}
	.status-warning {
		color: #ffc107;
	}
	.status-error {
		color: #dc3545;
	}
	.refresh-button {
		margin-top: 20rpx;
		background-color: #007bff;
		color: #FFFFFF;
		font-size: 32rpx;
		font-weight: bold;
		border-radius: 40rpx;
		height: 80rpx;
		line-height: 80rpx;
		width: 100%;
		text-align: center;
	}

	/* 安全功能区 */
	.safety-functions-section {
		padding: 0 40rpx;
		margin-top: 20rpx;
	}
	.section-title {
		font-size: 36rpx;
		font-weight: bold;
		margin-bottom: 20rpx;
		color: #000000;
	}
	.function-grid {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		gap: 25rpx;
	}
	.function-card {
		background-color: #F7F7F7;
		border-radius: 20rpx;
		padding: 30rpx;
		height: 160rpx;
		position: relative;
		overflow: hidden;
	}
	.card-text {
		display: flex;
		flex-direction: column;
		position: relative;
		z-index: 2;
	}
	.card-title {
		font-size: 32rpx;
		font-weight: bold;
		color: #333;
	}
	.card-subtitle {
		font-size: 22rpx;
		color: #999;
		margin-top: 8rpx;
	}
	.card-icon {
		position: absolute;
		bottom: -15rpx;
		right: -15rpx;
		width: 100rpx;
		height: 100rpx;
		z-index: 1;
		opacity: 0.2;
	}
	.card-icon-image {
		width: 100%;
		height: 100%;
	}

	/* 报警记录区 */
	.alert-history-section {
		flex: 1;
		margin: 30rpx 40rpx 0;
		background-color: rgba(255, 255, 255, 0.9);
		border-radius: 20rpx;
		padding: 30rpx;
		display: flex;
		flex-direction: column;
	}
	.alert-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 20rpx;
	}
	.clear-button {
		background-color: #6c757d;
		color: #FFFFFF;
		font-size: 24rpx;
		padding: 8rpx 20rpx;
		border-radius: 20rpx;
		line-height: 1.5;
		border: none;
	}
	.alert-list {
		flex: 1;
		max-height: 400rpx;
	}
	.empty-alerts {
		display: flex;
		justify-content: center;
		align-items: center;
		height: 200rpx;
		color: #999;
	}
	.alert-item {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 20rpx;
		margin-bottom: 15rpx;
		border-radius: 15rpx;
		background-color: #f8f9fa;
	}
	.alert-item.info {
		border-left: 5rpx solid #17a2b8;
	}
	.alert-item.success {
		border-left: 5rpx solid #28a745;
	}
	.alert-item.warning {
		border-left: 5rpx solid #ffc107;
	}
	.alert-item.error {
		border-left: 5rpx solid #dc3545;
	}
	.alert-content {
		display: flex;
		flex-direction: column;
	}
	.alert-title {
		font-size: 28rpx;
		font-weight: bold;
		color: #333;
	}
	.alert-time {
		font-size: 22rpx;
		color: #999;
		margin-top: 5rpx;
	}
	.alert-level {
		background-color: #e9ecef;
		padding: 5rpx 15rpx;
		border-radius: 15rpx;
		font-size: 20rpx;
		color: #6c757d;
	}

	/* 底部导航栏 */
	.bottom-nav-bar {
		position: fixed;
		z-index: 100;
		bottom: 0;
		left: 0;
		right: 0;
		display: flex;
		justify-content: space-around;
		align-items: center;
		height: 120rpx;
		background-color: #FFFFFF;
		border-top-left-radius: 40rpx;
		border-top-right-radius: 40rpx;
		box-shadow: 0 -2rpx 10rpx rgba(0,0,0,0.05);
	}
	.nav-item {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		flex: 1;
	}
	.nav-icon-image {
		width: 50rpx;
		height: 50rpx;
	}
	.nav-item.active .nav-icon-image {
		transform: translateY(-10rpx);
		width: 70rpx;
		height: 70rpx;
	}
</style>