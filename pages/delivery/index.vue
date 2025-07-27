<template>
	<view class="page-container">
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
			<view class="point-grid">
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
				points: []
			};
		},
		onShow() {
			this.loadPoints();
		},
		methods: {
			goBack() {
				uni.navigateBack();
			},
			loadPoints() {
				const storedPoints = uni.getStorageSync('points');
				if (storedPoints) {
					this.points = storedPoints;
				}
			},
			sendDelivery(index) {
				const point = this.points[index];
				uni.showToast({
					title: `配送指令已发送至 ${point.name}`,
					icon: 'none'
				});
			}
		}
	}
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