<template>
	<view class="page-container">
		<!-- 全屏加载动画 -->
		<view v-if="isLoading" class="loading-overlay">
			<view class="loading-spinner"></view>
			<text class="loading-text">{{ loadingText }}</text>
		</view>

		<view class="scroll-content">
			<!-- 1. 自定义导航栏 -->
			<view class="custom-nav-bar">
				<text class="nav-title">人员</text>
			</view>

			<!-- 2. 关怀通知 -->
			<view class="care-section">
				<text class="care-title">关怀通知</text>
				<view class="notification-cards">
					<view class="notification-card" v-for="item in careNotifications" :key="item.id">
						<view class="card-header">
							<image :src="item.avatar" class="avatar"></image>
							<view class="info">
								<text class="name">{{ item.name }}</text>
								<text class="details">{{ item.gender }} {{ item.age }}岁</text>
							</view>
						</view>
						<text class="message">{{ item.message }}</text>
						<button class="ack-button" @click="acknowledgeNotification(item.id)">我已知晓</button>
					</view>
				</view>
			</view>

			<!-- 3. 人员档案 -->
			<view class="personnel-section">
				<view class="personnel-header">
					<text class="personnel-title">人员档案</text>
					<view class="header-right">
						<button class="face-register-button" @click="goToFaceRegister">人脸注册</button>
						<view class="search-bar">
							<input type="text" placeholder="搜索..." class="search-input" v-model="searchText" @input="handleSearch" />
						</view>
					</view>
				</view>
				<!-- 调试信息 -->
				<view v-if="status === 'success'" style="background: #f0f0f0; padding: 20rpx; margin: 20rpx;">
					<text style="font-size: 24rpx; color: #666;">调试信息:</text>  
					<text style="font-size: 24rpx; color: #333;">状态: {{ status }}</text>
					<text style="font-size: 24rpx; color: #333;">原始数据长度: {{ personnelList.length }}</text>
					<text style="font-size: 24rpx; color: #333;">过滤后长度: {{ filteredPersonnelList.length }}</text>
				</view>

				<!-- 错误状态 -->
				<view v-if="status === 'error'" class="status-handler">
					<text class="error-message">{{ errorMessage }}</text>
					<button class="retry-button" @click="fetchProfiles">点击重试</button>
				</view>

				<view v-else class="personnel-grid">
					<view class="personnel-card" v-for="person in filteredPersonnelList" :key="person.profile_id" @click="handlePersonClick(person)">
						<image :src="person.avatar || '/static/icon_user.png'" class="person-avatar"></image>
						<view class="person-info">
							<text class="person-name">{{ person.name }}</text>
							<text class="person-details">{{ getPersonDetails(person) }}</text>
						</view>
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
				searchText: '',
				status: 'loading', // loading, success, error
				errorMessage: '',
				isLoading: false,
				loadingText: '加载中...',
				pollingInterval: null,
				careNotifications: [{
					id: 1,
					avatar: '/static/icon_user.png',
					name: '刘秀丽',
					gender: '女',
					age: 73,
					message: '今天是刘秀丽奶奶的73周岁生日，祝她生日快乐吧'
				}, {
					id: 2,
					avatar: '/static/icon_user.png',
					name: '李善良',
					gender: '男',
					age: 81,
					message: '李爷爷最近经常提起小女儿，提醒家人常来看看吧'
				}],
				personnelList: []
			};
		},
		computed: {
			filteredPersonnelList() {
				console.log('[Debug] 计算属性被调用, searchText:', this.searchText);
				console.log('[Debug] personnelList长度:', this.personnelList.length);
				
				if (!this.searchText) {
					console.log('[Debug] 无搜索条件，返回全部数据');
					return this.personnelList;
				}
				const filtered = this.personnelList.filter(person => 
					person.name.includes(this.searchText)
				);
				console.log('[Debug] 搜索结果长度:', filtered.length);
				return filtered;
			}
		},
		onLoad() {
			this.fetchProfiles();
		},
		onUnload() {
			if (this.pollingInterval) {
				clearInterval(this.pollingInterval);
			}
		},
		onShow() {
			// 每次显示页面时可以加载最新数据
			console.log('[Debug] onShow 被调用, 当前personnelList长度:', this.personnelList.length);
			if (this.personnelList.length === 0) {
				console.log('[Debug] 数据为空，重新获取');
				this.fetchProfiles();
			} else {
				console.log('[Debug] 数据已存在，不重新获取');
			}
		},
		methods: {
			async executeCommand(task, params = {}, loadingText = '处理中...') {
				this.isLoading = true;
				this.loadingText = loadingText;

				if (this.pollingInterval) {
					clearInterval(this.pollingInterval);
				}

				try {
					const postRes = await uniCloud.callFunction({
						name: 'postCommand',
						data: { task, params }
					});

					if (!postRes.result.success) {
						throw new Error(postRes.result.errMsg || '提交指令失败');
					}
					const commandId = postRes.result.commandId;

					return new Promise((resolve, reject) => {
						const timeout = setTimeout(() => {
							clearInterval(this.pollingInterval);
							this.isLoading = false;
							reject(new Error('请求超时，请稍后重试'));
						}, 20000);

						this.pollingInterval = setInterval(async () => {
							try {
								const resultRes = await uniCloud.callFunction({
									name: 'getCommandResult',
									data: { commandId }
								});

								if (resultRes.result.success && resultRes.result.command) {
									const command = resultRes.result.command;
									if (command.status === 'completed') {
										clearInterval(this.pollingInterval);
										clearTimeout(timeout);
										this.isLoading = false;
										resolve(command.result);
									} else if (command.status === 'failed') {
										clearInterval(this.pollingInterval);
										clearTimeout(timeout);
										this.isLoading = false;
										reject(new Error(command.error_message || '任务执行失败'));
									}
								} else if (!resultRes.result.success) {
									throw new Error(resultRes.result.errMsg || '查询结果失败');
								}
							} catch (pollError) {
								clearInterval(this.pollingInterval);
								clearTimeout(timeout);
								this.isLoading = false;
								reject(pollError);
							}
						}, 2000);
					});
				} catch (error) {
					this.isLoading = false;
					uni.showToast({ title: error.message, icon: 'none' });
					return Promise.reject(error);
				}
			},

			async fetchProfiles() {
				this.status = 'loading';
				try {
					console.log('[Debug] 开始获取人员档案...');
					const result = await this.executeCommand('get_profiles_config', {}, '正在获取人员档案...');
					console.log('[Debug] 后端返回的原始数据:', result);
					
					if (result && result.profiles) {
						console.log('[Debug] 档案数据数组:', result.profiles);
						console.log('[Debug] 档案数量:', result.profiles.length);
						
						this.personnelList = result.profiles;
						this.status = 'success';
						
						console.log('[Debug] 设置后的personnelList:', this.personnelList);
						console.log('[Debug] 设置后的状态:', this.status);
						console.log('成功加载', this.personnelList.length, '个人员档案');
						
						// 强制触发视图更新
						this.$forceUpdate();
					} else {
						console.error('[Debug] 后端返回数据格式错误:', result);
						throw new Error('未能获取到人员档案数据');
					}
				} catch (err) {
					this.status = 'error';
					this.errorMessage = err.message;
					console.error('fetchProfiles error:', err);
					console.error('[Debug] 错误详情:', err);
				}
			},

			getPersonDetails(person) {
				// 根据档案数据生成显示的详情
				let details = [];
				if (person.age) details.push(person.age + '岁');
				if (person.occupation) details.push(person.occupation);
				if (person.hometown) details.push(person.hometown);
				return details.length > 0 ? details.join(' ') : '点击查看详情';
			},
			loadPersonnelData() {
				// 在新的实现中，这个方法由fetchProfiles替代
				console.log('加载人员数据 - 使用fetchProfiles代替');
			},
			goToFaceRegister() {
				uni.navigateTo({
					url: '/pages/face_entry/index'
				});
			},
			handlePersonClick(person) {
				// 显示人员详情并支持编辑
				this.showPersonDetail(person);
			},

			showPersonDetail(person) {
				// 构建详情内容
				let content = `姓名: ${person.name}\n`;
				if (person.age) content += `年龄: ${person.age}\n`;
				if (person.occupation) content += `职业: ${person.occupation}\n`;
				if (person.hometown) content += `家乡: ${person.hometown}\n`;
				if (person.personality) content += `性格: ${person.personality}\n`;
				if (person.hobbies && person.hobbies.length > 0) content += `爱好: ${person.hobbies.join(', ')}\n`;
				if (person.favorite_foods && person.favorite_foods.length > 0) content += `喜爱食物: ${person.favorite_foods.join(', ')}\n`;
				if (person.habits && person.habits.length > 0) content += `习惯: ${person.habits.join(', ')}\n`;
				if (person.mood) content += `心情: ${person.mood}\n`;

				uni.showActionSheet({
					itemList: ['查看详情', '编辑档案'],
					success: (res) => {
						if (res.tapIndex === 0) {
							// 查看详情
							uni.showModal({
								title: '人员详情',
								content: content,
								showCancel: false,
								confirmText: '确定'
							});
						} else if (res.tapIndex === 1) {
							// 编辑档案
							this.editPersonProfile(person);
						}
					}
				});
			},

			editPersonProfile(person) {
				// 简单的编辑实现 - 可以根据需要扩展为完整的编辑页面
				const fields = [
					{ key: 'name', label: '姓名', value: person.name },
					{ key: 'age', label: '年龄', value: person.age },
					{ key: 'occupation', label: '职业', value: person.occupation },
					{ key: 'hometown', label: '家乡', value: person.hometown },
					{ key: 'personality', label: '性格', value: person.personality },
					{ key: 'mood', label: '心情', value: person.mood }
				];

				this.showEditDialog(person, fields, 0);
			},

			showEditDialog(person, fields, index) {
				if (index >= fields.length) {
					// 所有字段编辑完成，保存到云端
					this.savePersonProfile(person);
					return;
				}

				const field = fields[index];
				uni.showModal({
					title: `编辑${field.label}`,
					content: `当前${field.label}: ${field.value || '(空)'}`,
					editable: true,
					placeholderText: field.value || `请输入${field.label}`,
					success: (res) => {
						if (res.confirm && res.content.trim()) {
							person[field.key] = res.content.trim();
						}
						// 继续编辑下一个字段
						this.showEditDialog(person, fields, index + 1);
					},
					fail: () => {
						// 用户取消，继续下一个字段
						this.showEditDialog(person, fields, index + 1);
					}
				});
			},

			async savePersonProfile(person) {
				try {
					await this.executeCommand(
						'update_profile', 
						{ 
							profile_id: person.profile_id,
							profile_data: person
						}, 
						`正在保存 ${person.name} 的档案...`
					);
					
					uni.showToast({ title: '保存成功', icon: 'success' });
					
					// 更新本地列表
					const index = this.personnelList.findIndex(p => p.profile_id === person.profile_id);
					if (index !== -1) {
						this.personnelList[index] = { ...person };
					}

				} catch (err) {
					uni.showToast({ title: `保存失败: ${err.message}`, icon: 'none' });
					console.error('savePersonProfile error:', err);
				}
			},
			acknowledgeNotification(notificationId) {
				// 处理"我已知晓"按钮点击
				this.careNotifications = this.careNotifications.filter(item => item.id !== notificationId);
				uni.showToast({
					title: '已确认',
					icon: 'success'
				});
			},
			handleSearch() {
				// 搜索功能，通过计算属性filteredPersonnelList实现
				console.log('搜索:', this.searchText);
			}
		}
	}
</script>

<style>
	.page-container {
		display: flex;
		flex-direction: column;
		height: 100vh;
		background-color: #F7F7F7;
	}

	.scroll-content {
		flex: 1;
		overflow-y: auto;
		padding-bottom: 30rpx; /* 适配原生TabBar */
	}

	/* 自定义导航栏 */
	.custom-nav-bar {
		display: flex;
		align-items: flex-end;
		padding: 20rpx 40rpx;
		height: 120rpx;
		padding-top: var(--status-bar-height);
		background-color: transparent;
	}

	.nav-title {
		font-size: 36rpx;
		font-weight: bold;
		color: #000000;
	}

	/* 关怀通知 */
	.care-section {
		background: linear-gradient(180deg, #63D8A2 0%, #90E5B4 100%);
		padding: 30rpx 40rpx;
		border-bottom-left-radius: 40rpx;
		border-bottom-right-radius: 40rpx;
	}

	.care-title {
		font-size: 40rpx;
		font-weight: bold;
		color: #FFFFFF;
		margin-bottom: 30rpx;
		display: block;
	}

	.notification-cards {
		display: flex;
		justify-content: space-between;
		gap: 20rpx;
	}

	.notification-card {
		background-color: rgba(255, 255, 255, 0.8);
		border-radius: 20rpx;
		padding: 20rpx;
		width: 48%;
		box-sizing: border-box;
	}

	.card-header {
		display: flex;
		align-items: center;
		margin-bottom: 15rpx;
	}

	.avatar {
		width: 80rpx;
		height: 80rpx;
		border-radius: 50%;
		margin-right: 20rpx;
	}

	.info {
		display: flex;
		flex-direction: column;
	}

	.name {
		font-size: 30rpx;
		font-weight: bold;
	}

	.details {
		font-size: 24rpx;
		color: #666;
	}

	.message {
		font-size: 26rpx;
		color: #333;
		line-height: 1.4;
		display: block;
		margin-bottom: 20rpx;
	}

	.ack-button {
		background-color: #28a745;
		color: #FFFFFF;
		font-size: 24rpx;
		border-radius: 30rpx;
		padding: 10rpx 0;
		text-align: center;
		width: 80%;
		margin: 0 auto;
	}

	/* 人员档案 */
	.personnel-section {
		padding: 40rpx;
	}

	.personnel-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 30rpx;
	}

	.personnel-title {
		font-size: 36rpx;
		font-weight: bold;
	}

	.header-right {
		display: flex;
		align-items: center;
		gap: 20rpx;
	}

	.face-register-button {
		background-color: #007AFF;
		color: #FFFFFF;
		font-size: 24rpx;
		border-radius: 30rpx;
		padding: 8rpx 20rpx;
		height: auto;
		line-height: normal;
	}

	.search-bar {
		position: relative;
		width: 200rpx;
	}

	.search-input {
		background-color: #FFFFFF;
		border-radius: 30rpx;
		padding: 10rpx 20rpx;
		font-size: 26rpx;
		text-align: center;
	}

	.personnel-grid {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		gap: 25rpx;
	}

	.personnel-card {
		background-color: #FFFFFF;
		border-radius: 20rpx;
		padding: 20rpx;
		display: flex;
		align-items: center;
	}

	.person-avatar {
		width: 90rpx;
		height: 90rpx;
		border-radius: 50%;
		margin-right: 20rpx;
	}

	.person-info {
		display: flex;
		flex-direction: column;
	}

	.person-name {
		font-size: 30rpx;
		font-weight: bold;
	}

	.person-details {
		font-size: 24rpx;
		color: #666;
	}

	/* 加载动画样式 */
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

	/* 错误状态 */
	.status-handler {
		display: flex;
		flex-direction: column;
		justify-content: center;
		align-items: center;
		padding-top: 200rpx;
		z-index: 1;
	}
	.error-message {
		color: #dd524d;
		margin-bottom: 40rpx;
		text-align: center;
	}
	.retry-button {
		width: 300rpx;
		background-color: #007AFF;
		color: white;
		border-radius: 30rpx;
		padding: 15rpx 30rpx;
	}
</style>