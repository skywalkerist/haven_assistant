<template>
	<view class="page-container">
		<!-- 1. 顶部用户信息区 -->
		<view class="top-user-section">
			<view class="user-avatar">
				<image src="/static/icon_user.png" mode="aspectFit" class="avatar-image"></image>
			</view>
			<view class="user-info-container">
				<text class="user-name">{{ userInfo.name }}</text>
				<text class="user-role">{{ userInfo.role }}</text>
				<view class="user-stats">
					<view class="stat-item">
						<text class="stat-number">{{ userInfo.loginDays }}</text>
						<text class="stat-label">连续登录天数</text>
					</view>
					<view class="stat-item">
						<text class="stat-number">{{ userInfo.totalCommands }}</text>
						<text class="stat-label">总指令数</text>
					</view>
				</view>
			</view>
		</view>

		<!-- 2. 功能菜单区 -->
		<view class="menu-section">
			<text class="section-title">功能菜单</text>
			<view class="menu-list">
				<view class="menu-item" v-for="(menu, index) in menuItems" :key="index" @click="handleMenuClick(menu.title)">
					<view class="menu-icon">
						<image :src="menu.icon" class="menu-icon-image" mode="aspectFit"></image>
					</view>
					<view class="menu-content">
						<text class="menu-title">{{ menu.title }}</text>
						<text class="menu-subtitle">{{ menu.subtitle }}</text>
					</view>
					<view class="menu-arrow">
						<text>&gt;</text>
					</view>
				</view>
			</view>
		</view>

		<!-- 3. 使用统计区 -->
		<view class="statistics-section">
			<text class="section-title">使用统计</text>
			<view class="stats-grid">
				<view class="stats-card" v-for="(stat, index) in statistics" :key="index">
					<text class="stats-number">{{ stat.number }}</text>
					<text class="stats-label">{{ stat.label }}</text>
				</view>
			</view>
		</view>

		<!-- 4. 快速操作区 -->
		<view class="quick-actions-section">
			<text class="section-title">快速操作</text>
			<view class="actions-grid">
				<view class="action-button" v-for="(action, index) in quickActions" :key="index" @click="handleActionClick(action.title)">
					<image :src="action.icon" class="action-icon" mode="aspectFit"></image>
					<text class="action-text">{{ action.title }}</text>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				userInfo: {
					name: '管理员',
					role: '系统管理员',
					loginDays: 15,
					totalCommands: 128
				},
				menuItems: [{
					title: '个人设置',
					subtitle: '修改个人信息和偏好',
					icon: '/static/icon_personnalset.png'
				}, {
					title: '系统设置',
					subtitle: '应用配置和系统参数',
					icon: '/static/icon_robo.png'
				}, {
					title: '历史记录',
					subtitle: '查看操作和使用历史',
					icon: '/static/icon_chat.png'
				}, {
					title: '帮助中心',
					subtitle: '使用说明和常见问题',
					icon: '/static/icon_warning.png'
				}, {
					title: '关于应用',
					subtitle: '版本信息和开发团队',
					icon: '/static/icon_voice.png'
				}],
				statistics: [{
					number: '89%',
					label: '系统使用率'
				}, {
					number: '24h',
					label: '在线时长'
				}, {
					number: '5',
					label: '活跃设备'
				}, {
					number: '100%',
					label: '任务完成率'
				}],
				quickActions: [{
					title: '重启系统',
					icon: '/static/icon_robo.png'
				}, {
					title: '清理缓存',
					icon: '/static/icon_safety.png'
				}, {
					title: '导出日志',
					icon: '/static/icon_delivery.png'
				}, {
					title: '联系客服',
					icon: '/static/icon_contact.png'
				}]
			};
		},
		onShow() {
			this.loadUserInfo();
		},
		methods: {
			loadUserInfo() {
				// 模拟加载用户信息
				// 这里可以从本地存储或云端获取真实用户数据
				console.log('加载用户信息');
			},
			handleMenuClick(title) {
				switch(title) {
					case '个人设置':
						uni.navigateTo({
							url: '/pages/personalization/index'
						});
						break;
					case '系统设置':
						uni.showToast({
							title: '系统设置功能开发中',
							icon: 'none'
						});
						break;
					case '历史记录':
						this.showHistory();
						break;
					case '帮助中心':
						this.showHelp();
						break;
					case '关于应用':
						this.showAbout();
						break;
					default:
						uni.showToast({
							title: `${title}功能开发中`,
							icon: 'none'
						});
				}
			},
			handleActionClick(title) {
				switch(title) {
					case '重启系统':
						uni.showModal({
							title: '确认重启',
							content: '确定要重启系统吗？这将中断当前所有操作。',
							success: (res) => {
								if (res.confirm) {
									uni.showToast({
										title: '重启指令已发送',
										icon: 'success'
									});
								}
							}
						});
						break;
					case '清理缓存':
						uni.showLoading({
							title: '清理中...'
						});
						setTimeout(() => {
							uni.hideLoading();
							uni.showToast({
								title: '缓存清理完成',
								icon: 'success'
							});
						}, 2000);
						break;
					case '导出日志':
						uni.showToast({
							title: '日志导出功能开发中',
							icon: 'none'
						});
						break;
					case '联系客服':
						uni.showModal({
							title: '联系客服',
							content: '客服电话：400-123-4567\n工作时间：9:00-18:00',
							showCancel: false
						});
						break;
					default:
						uni.showToast({
							title: `${title}功能开发中`,
							icon: 'none'
						});
				}
			},
			showHistory() {
				const histories = [
					'2小时前 - 执行安防巡逻',
					'4小时前 - 语音交互',
					'昨天 - 添加新点位',
					'昨天 - 物品配送完成',
					'2天前 - 系统状态检查'
				];
				
				uni.showModal({
					title: '最近操作历史',
					content: histories.join('\n'),
					showCancel: false
				});
			},
			showHelp() {
				const helpContent = [
					'1. 点击底部机器人图标返回主界面',
					'2. 使用语音功能与机器人对话',
					'3. 在点位设置中管理机器人位置',
					'4. 通过安防巡逻设置巡检路线',
					'5. 如遇问题请联系客服'
				];
				
				uni.showModal({
					title: '使用帮助',
					content: helpContent.join('\n'),
					showCancel: false
				});
			},
			showAbout() {
				uni.showModal({
					title: '关于Haven App',
					content: '版本：v1.0.0\n开发团队：Haven Tech\n更新时间：2024年7月\n\n智能机器人控制系统',
					showCancel: false
				});
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

	/* 顶部用户信息区 */
	.top-user-section {
		display: flex;
		padding: 40rpx;
		align-items: center;
		background-color: rgba(255, 255, 255, 0.1);
		margin: 20rpx;
		border-radius: 20rpx;
	}
	.user-avatar {
		width: 120rpx;
		height: 120rpx;
		border-radius: 60rpx;
		background-color: rgba(255, 255, 255, 0.3);
		display: flex;
		justify-content: center;
		align-items: center;
		margin-right: 30rpx;
	}
	.avatar-image {
		width: 80rpx;
		height: 80rpx;
	}
	.user-info-container {
		flex: 1;
	}
	.user-name {
		font-size: 36rpx;
		font-weight: bold;
		color: #000000;
		display: block;
		margin-bottom: 10rpx;
	}
	.user-role {
		font-size: 26rpx;
		color: #666;
		display: block;
		margin-bottom: 20rpx;
	}
	.user-stats {
		display: flex;
		gap: 40rpx;
	}
	.stat-item {
		display: flex;
		flex-direction: column;
		align-items: center;
	}
	.stat-number {
		font-size: 32rpx;
		font-weight: bold;
		color: #28a745;
	}
	.stat-label {
		font-size: 20rpx;
		color: #999;
		margin-top: 5rpx;
	}

	/* 功能菜单区 */
	.menu-section {
		padding: 0 40rpx;
		margin-top: 20rpx;
	}
	.section-title {
		font-size: 36rpx;
		font-weight: bold;
		margin-bottom: 20rpx;
		color: #000000;
	}
	.menu-list {
		background-color: rgba(255, 255, 255, 0.9);
		border-radius: 20rpx;
		overflow: hidden;
	}
	.menu-item {
		display: flex;
		align-items: center;
		padding: 30rpx;
		border-bottom: 1rpx solid #f0f0f0;
	}
	.menu-item:last-child {
		border-bottom: none;
	}
	.menu-icon {
		width: 80rpx;
		height: 80rpx;
		margin-right: 30rpx;
	}
	.menu-icon-image {
		width: 100%;
		height: 100%;
	}
	.menu-content {
		flex: 1;
	}
	.menu-title {
		font-size: 32rpx;
		font-weight: bold;
		color: #333;
		display: block;
		margin-bottom: 8rpx;
	}
	.menu-subtitle {
		font-size: 24rpx;
		color: #999;
	}
	.menu-arrow {
		font-size: 32rpx;
		color: #ccc;
	}

	/* 使用统计区 */
	.statistics-section {
		padding: 0 40rpx;
		margin-top: 30rpx;
	}
	.stats-grid {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		gap: 20rpx;
	}
	.stats-card {
		background-color: rgba(255, 255, 255, 0.9);
		border-radius: 15rpx;
		padding: 30rpx;
		text-align: center;
	}
	.stats-number {
		font-size: 48rpx;
		font-weight: bold;
		color: #007bff;
		display: block;
		margin-bottom: 10rpx;
	}
	.stats-label {
		font-size: 24rpx;
		color: #666;
	}

	/* 快速操作区 */
	.quick-actions-section {
		padding: 0 40rpx;
		margin-top: 30rpx;
	}
	.actions-grid {
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		gap: 20rpx;
	}
	.action-button {
		background-color: rgba(255, 255, 255, 0.9);
		border-radius: 15rpx;
		padding: 25rpx;
		display: flex;
		flex-direction: column;
		align-items: center;
		text-align: center;
	}
	.action-icon {
		width: 60rpx;
		height: 60rpx;
		margin-bottom: 15rpx;
	}
	.action-text {
		font-size: 22rpx;
		color: #333;
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