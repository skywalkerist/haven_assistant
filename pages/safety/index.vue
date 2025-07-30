<template>
	<view class="page-container">
		<!-- 当前活跃警报 -->
		<view class="active-alerts-section">
			<text class="section-title">当前活跃警报</text>
			<view v-if="activeAlerts.length === 0" class="empty-alerts">
				<image src="/static/icon_safety.png" class="empty-icon" mode="aspectFit"></image>
				<text class="empty-text">暂无活跃警报</text>
			</view>
			<view v-for="(alert, index) in activeAlerts" :key="alert.id" class="alert-card">
				<view class="alert-header">
					<view class="alert-type" :class="alert.type">
						<text class="alert-type-text">{{ alert.typeText }}</text>
					</view>
					<text class="alert-time">{{ alert.time }}</text>
				</view>
				
				<text class="alert-description">{{ alert.description }}</text>
				
				<!-- 机器人信息 -->
				<view class="robot-info">
					<view class="robot-detail">
						<text class="robot-label">机器人型号:</text>
						<text class="robot-value">{{ alert.robot.model }}</text>
					</view>
					<view class="robot-detail">
						<text class="robot-label">设备编号:</text>
						<text class="robot-value">{{ alert.robot.id }}</text>
					</view>
					<view class="robot-detail">
						<text class="robot-label">电量:</text>
						<text class="robot-value">{{ alert.robot.battery }}%</text>
					</view>
				</view>
				
				<!-- 位置信息 -->
				<view class="location-info">
					<text class="location-text">{{ alert.location.building }} {{ alert.location.floor }} {{ alert.location.room }}</text>
				</view>
				
				<!-- 操作按钮 -->
				<view class="alert-actions">
					<button class="action-btn secondary" @click="viewMonitoring(alert)">查看监控</button>
					<button class="action-btn primary" @click="markCompleted(alert)">标记完成</button>
				</view>
			</view>
		</view>

		<!-- 历史警报 -->
		<view class="history-section">
			<view class="history-header">
				<text class="section-title">历史警报</text>
				<button class="clear-btn" @click="clearHistory">清空历史</button>
			</view>
			<scroll-view scroll-y class="history-list">
				<view v-if="historyAlerts.length === 0" class="empty-history">
					<text>暂无历史记录</text>
				</view>
				<view v-for="(alert, index) in historyAlerts" :key="alert.id" class="history-item">
					<view class="history-main">
						<text class="history-title">{{ alert.typeText }} - {{ alert.description }}</text>
						<text class="history-time">{{ alert.completedTime }}</text>
					</view>
					<view class="history-status completed">
						<text>已处理</text>
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
				activeAlerts: [
					{
						id: 1,
						type: 'fire',
						typeText: '火情警报',
						description: '检测到异常高温，疑似火情',
						time: '13:25',
						robot: {
							model: 'Haven Guard Pro',
							id: 'HGP-001',
							battery: 87
						},
						location: {
							building: '1号楼',
							floor: '3楼',
							room: '301室'
						}
					},
					{
						id: 2,
						type: 'fall',
						typeText: '摔倒警报',
						description: '检测到人员摔倒，需要紧急救援',
						time: '12:58',
						robot: {
							model: 'Haven Care Plus',
							id: 'HCP-002',
							battery: 64
						},
						location: {
							building: '2号楼',
							floor: '1楼',
							room: '大厅'
						}
					}
				],
				historyAlerts: [
					{
						id: 3,
						typeText: '设备异常',
						description: '摄像头连接中断',
						completedTime: '今天 11:30'
					},
					{
						id: 4,
						typeText: '环境警报',
						description: '湿度过高警报',
						completedTime: '今天 10:15'
					}
				]
			};
		},
		methods: {
			viewMonitoring(alert) {
				uni.showToast({
					title: `正在打开${alert.location.room}监控`,
					icon: 'none'
				});
			},
			
			markCompleted(alert) {
				uni.showModal({
					title: '确认处理',
					content: `确认已处理"${alert.typeText}"警报？`,
					success: (res) => {
						if (res.confirm) {
							// 移动到历史记录
							const historyItem = {
								id: alert.id,
								typeText: alert.typeText,
								description: alert.description,
								completedTime: this.getCurrentTime()
							};
							this.historyAlerts.unshift(historyItem);
							
							// 从活跃警报中移除
							this.activeAlerts = this.activeAlerts.filter(a => a.id !== alert.id);
							
							uni.showToast({
								title: '警报已处理',
								icon: 'success'
							});
						}
					}
				});
			},
			
			getCurrentTime() {
				const now = new Date();
				const hours = now.getHours().toString().padStart(2, '0');
				const minutes = now.getMinutes().toString().padStart(2, '0');
				return `今天 ${hours}:${minutes}`;
			},
			
			clearHistory() {
				uni.showModal({
					title: '确认清空',
					content: '确定要清空所有历史警报记录吗？',
					success: (res) => {
						if (res.confirm) {
							this.historyAlerts = [];
							uni.showToast({
								title: '历史记录已清空',
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
	.page-container {
		background: linear-gradient(180deg, #FF6B6B 0%, #FFE66D 100%);
		min-height: 100vh;
		display: flex;
		flex-direction: column;
		padding-bottom: 30rpx; /* 适配原生TabBar */
	}

	/* 当前活跃警报 */
	.active-alerts-section {
		padding: 40rpx;
		flex: 1;
	}
	
	.section-title {
		font-size: 32rpx;
		font-weight: bold;
		color: #FFFFFF;
		margin-bottom: 30rpx;
	}
	
	.empty-alerts {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		height: 300rpx;
		background-color: rgba(255, 255, 255, 0.9);
		border-radius: 20rpx;
	}
	
	.empty-icon {
		width: 120rpx;
		height: 120rpx;
		opacity: 0.5;
		margin-bottom: 20rpx;
	}
	
	.empty-text {
		color: #999;
		font-size: 28rpx;
	}
	
	.alert-card {
		background-color: #FFFFFF;
		border-radius: 20rpx;
		padding: 30rpx;
		margin-bottom: 20rpx;
		box-shadow: 0 8rpx 25rpx rgba(0,0,0,0.1);
	}
	
	.alert-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 20rpx;
	}
	
	.alert-type {
		padding: 8rpx 20rpx;
		border-radius: 20rpx;
		font-size: 24rpx;
		color: #FFFFFF;
	}
	
	.alert-type.fire {
		background-color: #FF4757;
	}
	
	.alert-type.fall {
		background-color: #FF6B35;
	}
	
	.alert-type.security {
		background-color: #5352ED;
	}
	
	.alert-time {
		font-size: 26rpx;
		color: #666;
	}
	
	.alert-description {
		font-size: 30rpx;
		color: #333;
		margin-bottom: 25rpx;
		font-weight: 500;
	}
	
	/* 机器人信息 */
	.robot-info {
		background-color: #F8F9FA;
		border-radius: 15rpx;
		padding: 20rpx;
		margin-bottom: 20rpx;
	}
	
	.robot-detail {
		display: flex;
		justify-content: space-between;
		margin-bottom: 10rpx;
	}
	
	.robot-detail:last-child {
		margin-bottom: 0;
	}
	
	.robot-label {
		font-size: 26rpx;
		color: #666;
	}
	
	.robot-value {
		font-size: 26rpx;
		color: #333;
		font-weight: 500;
	}
	
	/* 位置信息 */
	.location-info {
		background-color: #E3F2FD;
		border-radius: 15rpx;
		padding: 15rpx 20rpx;
		margin-bottom: 25rpx;
	}
	
	.location-text {
		font-size: 28rpx;
		color: #1976D2;
		font-weight: 500;
	}
	
	/* 操作按钮 */
	.alert-actions {
		display: flex;
		gap: 20rpx;
	}
	
	.action-btn {
		flex: 1;
		height: 80rpx;
		border-radius: 40rpx;
		font-size: 28rpx;
		border: none;
	}
	
	.action-btn.primary {
		background-color: #4CAF50;
		color: #FFFFFF;
	}
	
	.action-btn.secondary {
		background-color: #2196F3;
		color: #FFFFFF;
	}

	/* 历史警报 */
	.history-section {
		background-color: rgba(255, 255, 255, 0.95);
		margin: 20rpx 40rpx 0;
		border-radius: 20rpx 20rpx 0 0;
		padding: 30rpx;
		flex: 1;
		display: flex;
		flex-direction: column;
	}
	
	.history-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 20rpx;
	}
	
	.history-header .section-title {
		color: #333;
		margin-bottom: 0;
	}
	
	.clear-btn {
		background-color: #6C757D;
		color: #FFFFFF;
		font-size: 24rpx;
		padding: 8rpx 20rpx;
		border-radius: 20rpx;
		border: none;
	}
	
	.history-list {
		flex: 1;
		max-height: 400rpx;
	}
	
	.empty-history {
		display: flex;
		justify-content: center;
		align-items: center;
		height: 200rpx;
		color: #999;
		font-size: 28rpx;
	}
	
	.history-item {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 20rpx;
		margin-bottom: 15rpx;
		background-color: #F8F9FA;
		border-radius: 15rpx;
	}
	
	.history-main {
		flex: 1;
		display: flex;
		flex-direction: column;
	}
	
	.history-title {
		font-size: 28rpx;
		color: #333;
		margin-bottom: 8rpx;
	}
	
	.history-time {
		font-size: 24rpx;
		color: #999;
	}
	
	.history-status {
		padding: 8rpx 15rpx;
		border-radius: 15rpx;
		font-size: 22rpx;
	}
	
	.history-status.completed {
		background-color: #D4EDDA;
		color: #155724;
	}
</style>