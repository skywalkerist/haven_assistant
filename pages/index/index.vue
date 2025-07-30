<template>
	<view class="page-container">
		<!-- 1. 顶部状态区 -->
		<view class="top-status-section">
			<view class="robot-illustration">
				<image src="/static/robot.png" mode="aspectFit" class="robot-image"></image>
			</view>
			<view class="robot-info-container">
				<text class="info-title">基本信息</text>
				<view class="robot-info-card">
					<view><text>状态: 空闲</text></view>
					<view><text>位置: A302房间</text></view>
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

		<!-- 3. 语音播报条 -->
		<view class="voice-broadcast-bar">
			<image src="/static/icon_trumpet.png" class="voice-icon"></image>
			<text class="voice-text">老吾老，以及人之老；幼吾幼，以及人之幼。</text>
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
					icon: '/static/icon_delivery.png'
				}, {
					title: '音色管理',
					subtitle: '聊天分享 记录回忆',
					icon: '/static/icon_personnalset.png'
				}, {
					title: '点位设置',
					subtitle: '新的位置 心的发现',
					icon: '/static/icon_positon.png'
				}, {
					title: '提醒设置',
					subtitle: '服药提醒 用药保障',
					icon: '/static/icon_chat.png'
				}, {
					title: '安防巡逻',
					subtitle: '防患未然 智能巡检',
					icon: '/static/icon_safety.png'
				}, {
					title: '语音模式',
					subtitle: '方言识别 从心所欲',
					icon: '/static/icon_voice.png'
				}]
			};
		},
		onShow() {
			// 强制刷新，确保每次返回页面时组件都正确渲染
			this.$forceUpdate();
		},
		methods: {
			handleTaskClick(title) {
				if (title === '物品配送') {
					uni.navigateTo({
						url: '/pages/delivery/index'
					});
				} else if (title === '音色管理') {
					uni.navigateTo({
						url: '/pages/voice_management/index'
					});
				} else if (title === '点位设置') {
					uni.navigateTo({
						url: '/pages/marker/index'
					});
				} else if (title === '语音模式') {
					uni.navigateTo({
						url: '/pages/chat/chat'
					});
				} else if (title === '安防巡逻') {
					uni.navigateTo({
						url: '/pages/patrol/index'
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
	.robot-illustration {
		flex: 1.2;
		display: flex;
		justify-content: center;
		align-items: center;
	}
	.robot-image {
		width: 320rpx;
		height: 320rpx;
	}
	.robot-info-container {
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
	.robot-info-card {
		background-color: rgba(255, 255, 255, 0.5);
		border-radius: 20rpx;
		padding: 20rpx;
		font-size: 26rpx;
		color: #333;
		width: 100%;
	}
	.call-button {
		margin-top: 20rpx;
		background-color: #28a745; /* Green color from design */
		color: #FFFFFF;
		font-size: 32rpx;
		font-weight: bold;
		border-radius: 40rpx;
		height: 80rpx;
		line-height: 80rpx;
		width: 100%;
		text-align: center;
	}

	/* 任务下发区 */
	.task-assignment-section {
		padding: 0 40rpx;
		margin-top: 20rpx;
	}
	.section-title {
		font-size: 36rpx;
		font-weight: bold;
		margin-bottom: 20rpx;
		color: #000000;
	}
	.task-grid {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		gap: 25rpx;
	}
	.task-card {
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
		font-size: 36rpx;
		font-weight: bold;
		color: #333;
	}
	.card-subtitle {
		font-size: 26rpx;
		color: #999;
		margin-top: 8rpx;
	}
	.card-icon {
		position: absolute;
		bottom: -15rpx;
		right: -15rpx;
		width: 120rpx;
		height: 120rpx;
		z-index: 1;
		opacity: 1;
	}
	.card-icon-image {
		width: 100%;
		height: 100%;
	}

	/* 语音播报条 */
	.voice-broadcast-bar {
		margin: 30rpx 40rpx;
		padding: 20rpx;
		background-color: rgba(230, 247, 237, 0.8); /* Light green with transparency */
		border-radius: 20rpx;
		display: flex;
		align-items: center;
	}
	.voice-icon {
		width: 40rpx;
		height: 40rpx;
		margin-right: 20rpx;
	}
	.voice-text {
		font-size: 24rpx;
		color: #555;
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
		transform: translateY(-10rpx); /* Move icon up slightly */
		width: 70rpx; /* Make active icon larger */
		height: 70rpx;
	}
</style>