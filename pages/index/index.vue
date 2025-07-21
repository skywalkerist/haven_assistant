<template>
	<view class="page-container">
		<!-- 1. 顶部状态区 -->
		<view class="top-status-section">
			<view class="robot-illustration">
				<image src="/static/robot.png" mode="aspectFit" class="robot-image"></image>
			</view>
			<view class="robot-info">
				<text class="info-title">基本信息</text>
				<view class="info-list">
					<view><text>状态: 空闲</text></view>
					<view><text>区域: A302房间</text></view>
					<view><text>电量: 70%</text></view>
				</view>
				<button class="call-button">呼唤</button>
			</view>
		</view>

		<!-- 2. 任务下发区 -->
		<view class="task-assignment-section">
			<text class="section-title">任务下发</text>
			<view class="task-grid">
				<view class="task-card" v-for="(task, index) in tasks" :key="index" @click="handleTaskClick(task.title)">
					<view class="card-text">
						<text class="card-title">{{ task.title }}</text>
						<text class="card-subtitle">{{ task.subtitle }}</text>
					</view>
					<view class="card-icon">
						<image :src="task.icon" class="card-icon-image" mode="aspectFit"></image>
					</view>
				</view>
			</view>
		</view>

		<!-- 3. 底部导航栏 -->
		<view class="bottom-nav-bar">
			<view class="nav-item">
				<image src="/static/icon_warning.png" class="nav-icon-image"></image>
			</view>
			<view class="nav-item active">
				<view class="active-icon-background">
					<image src="/static/icon_robot.png" class="nav-icon-image"></image>
				</view>
			</view>
			<view class="nav-item">
				<image src="/static/icon_user.png" class="nav-icon-image"></image>
			</view>
		</view>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				tasks: [{
					title: '物品配送',
					subtitle: '快速配送 解放双手',
					icon: '/static/Vector1.png'
				}, {
					title: '个性设置',
					subtitle: '人员注册 声音配置',
					icon: '/static/Vector4.png'
				}, {
					title: '点位设置',
					subtitle: '新的位置 心的发现',
					icon: '/static/Vector3.png'
				}, {
					title: '拍照录入',
					subtitle: '轻松一拍 信息入库',
					icon: '/static/Vector2.png'
				}, {
					title: '安防巡逻',
					subtitle: '防患未然 智能巡检',
					icon: '/static/V5.png'
				}, {
					title: '语音模式',
					subtitle: '方言识别 从心所欲',
					icon: '/static/V6.png'
				}]
			};
		},
		methods: {
			handleTaskClick(title) {
				if (title === '个性设置') {
					uni.navigateTo({
						url: '/pages/personalization/index'
					});
				} else if (title === '点位设置') {
					uni.navigateTo({
						url: '/pages/marker/index'
					});
				} else {
					uni.showToast({
						title: '功能待开发',
						icon: 'none'
					});
				}
			}
		}
	}
</script>

<style>
	.page-container {
		display: flex;
		flex-direction: column;
		background-color: #FFFFFF;
		min-height: 100vh;
		padding-bottom: 120rpx; /* 为底部导航栏留出空间 */
	}

	/* 顶部状态区 */
	.top-status-section {
		display: flex;
		padding: 40rpx;
		align-items: center;
	}
	.robot-illustration {
		flex: 1;
	}
	.robot-image {
		width: 300rpx;
		height: 300rpx;
	}
	.robot-info {
		flex: 2;
		display: flex;
		flex-direction: column;
		padding-left: 20rpx;
	}
	.info-title {
		font-size: 32rpx;
		font-weight: bold;
		margin-bottom: 10rpx;
	}
	.info-list {
		font-size: 24rpx;
		color: #666;
	}
	.call-button {
		margin-top: 20rpx;
		background-color: #f0f0f0;
		color: #333;
		font-size: 28rpx;
		border-radius: 40rpx;
		height: 60rpx;
		line-height: 60rpx;
	}

	/* 任务下发区 */
	.task-assignment-section {
		padding: 0 40rpx;
	}
	.section-title {
		font-size: 36rpx;
		font-weight: bold;
		margin-bottom: 20rpx;
	}
	.task-grid {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		gap: 20rpx;
	}
	.task-card {
		background-color: #FFFFFF;
		border-radius: 20rpx;
		box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
		padding: 30rpx;
		height: 180rpx;
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
		font-size: 34rpx;
		font-weight: bold;
	}
	.card-subtitle {
		font-size: 24rpx;
		color: #999;
		margin-top: 10rpx;
	}
	.card-icon {
		position: absolute;
		bottom: -20rpx;
		right: -20rpx;
		width: 120rpx;
		height: 120rpx;
		z-index: 1;
		opacity: 0.5;
	}
	.card-icon-image {
		width: 100%;
		height: 100%;
	}

	/* 底部导航栏 */
	.bottom-nav-bar {
		position: fixed;
		bottom: 0;
		left: 0;
		right: 0;
		display: flex;
		justify-content: space-around;
		align-items: center;
		height: 120rpx;
		background-color: #f8f8f8;
		border-top: 1rpx solid #e7e7e7;
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
	.nav-item.active .active-icon-background {
		background-color: #e0e0e0; /* 浅灰色背景 */
		border-radius: 25rpx; /* 圆角 */
		padding: 15rpx;
		display: flex;
		justify-content: center;
		align-items: center;
	}
	.nav-item.active .nav-icon-image {
		/* 也许可以给激活的图标加个效果，如果需要的话 */
	}
</style>
