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
			<text class="nav-title">音色管理</text>
		</view>

		<!-- 错误状态 -->
		<view v-if="status === 'error'" class="status-handler">
			<text class="error-message">{{ errorMessage }}</text>
			<button class="retry-button" @click="fetchVoices">点击重试</button>
		</view>

		<!-- 2. 音色列表 -->
		<view v-else class="voice-list-section">
			<view class="tip">
				<text>轻点卡片选择默认音色，长按可进行编辑操作</text>
			</view>
			
			<view class="voice-grid">
				<view 
					v-for="(voice, index) in voiceList" 
					:key="voice.name || index" 
					class="voice-card"
					:class="{ 'is-default': voice.isDefault }"
					@click="selectVoice(voice)"
					@longpress="showVoiceActions(voice, index)">
					
					<view v-if="voice.isDefault" class="default-badge">默认</view>
					
					<image src="/static/icon_speak.png" class="voice-icon" mode="aspectFit"></image>
					<view class="voice-info">
						<text class="voice-name">{{ voice.name }}</text>
						<text v-if="voice.relation" class="voice-details">{{ voice.relation }} {{ voice.age }}岁</text>
						<text v-else-if="!voice.isDefault" class="voice-details">自定义音色</text>
					</view>
				</view>
			</view>
		</view>

		<!-- 3. 添加音色按钮 -->
		<view class="add-voice-button-container">
			<button class="add-voice-button" @click="addVoice">添加音色</button>
		</view>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				status: 'loading', // loading, success, error
				errorMessage: '',
				voiceList: [],
				isLoading: false,
				loadingText: '加载中...',
				pollingInterval: null
			};
		},
		onLoad() {
			this.fetchVoices();
		},
		onShow() {
			// 页面显示时，检查是否有新录入的音色
			const newVoice = uni.getStorageSync('newly_added_voice');
			if (newVoice) {
				// 检查是否已存在相同ID的音色
				const exists = this.voiceList.some(v => v.name === newVoice.name);
				if (!exists) {
					this.voiceList.push(newVoice);
				}
				// 清除缓存，防止下次进入时重复添加
				uni.removeStorageSync('newly_added_voice');
			}
		},
		onUnload() {
			if (this.pollingInterval) {
				clearInterval(this.pollingInterval);
			}
		},
		methods: {
			goBack() {
				uni.navigateBack();
			},
			
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

			async fetchVoices() {
				this.status = 'loading';
				try {
					const result = await this.executeCommand('get_voices_config', {}, '正在获取音色列表...');
					if (result && result.fileContent) {
						const config = JSON.parse(result.fileContent);
						const defaultVoiceId = config.default;
						let defaultVoiceName = '';

						// 找出默认音色的名字
						for (const name in config) {
							if (config[name] === defaultVoiceId && name !== 'default') {
								defaultVoiceName = name;
								break;
							}
						}

						// 转换数据结构用于渲染，添加更多信息
						this.voiceList = Object.keys(config)
							.filter(key => key !== 'default')
							.map(name => ({
								name: name,
								res_id: config[name],
								isDefault: name === defaultVoiceName,
								// 可以根据名称推断关系和年龄，或从其他地方获取
								relation: this.getVoiceRelation(name),
								age: this.getVoiceAge(name)
							}));
							
						this.status = 'success';
					} else {
						throw new Error('未能获取到配置文件内容');
					}
				} catch (err) {
					this.status = 'error';
					this.errorMessage = err.message;
					console.error('fetchVoices error:', err);
				}
			},

			// 辅助方法：根据音色名称推断关系
			getVoiceRelation(name) {
				// 这里可以根据业务逻辑推断或从其他数据源获取
				if (name.includes('女儿')) return '女儿';
				if (name.includes('儿子')) return '儿子';
				if (name.includes('老伴')) return '老伴';
				return null;
			},

			// 辅助方法：根据音色名称推断年龄
			getVoiceAge(name) {
				// 这里可以根据业务逻辑推断或从其他数据源获取
				return null; // 暂时返回null，可根据需要实现
			},

			async selectVoice(voice) {
				if (voice.isDefault || this.isLoading) {
					return; // 如果已经是默认或者正在加载，则不执行任何操作
				}

				try {
					await this.executeCommand(
						'set_voices_config', 
						{ default_voice: voice.name }, 
						`正在将默认音色设为 ${voice.name}...`
					);
					
					uni.showToast({ title: '设置成功', icon: 'success' });

					// 更新本地列表的默认状态
					this.voiceList.forEach(v => {
						v.isDefault = (v.name === voice.name);
					});

				} catch (err) {
					uni.showToast({ title: `设置失败: ${err.message}`, icon: 'none' });
					console.error('selectVoice error:', err);
				}
			},

			addVoice() {
				uni.navigateTo({
					url: '/pages/voice_cloning/index'
				});
			},

			showVoiceActions(voice, index) {
				if (voice.isDefault) {
					uni.showToast({
						title: '默认音色无法编辑',
						icon: 'none'
					});
					return;
				}

				uni.showActionSheet({
					itemList: ['重命名', '删除'],
					success: (res) => {
						if (res.tapIndex === 0) {
							this.renameVoice(voice, index);
						} else if (res.tapIndex === 1) {
							this.deleteVoice(voice, index);
						}
					}
				});
			},

			renameVoice(voice, index) {
				uni.showModal({
					title: '重命名音色',
					content: `为 "${voice.name}" 输入新名称`,
					editable: true,
					placeholderText: voice.name,
					success: (res) => {
						if (res.confirm) {
							const newName = res.content.trim();
							if (newName && newName !== voice.name) {
								// 更新本地显示
								this.voiceList[index].name = newName;
								// 这里可以添加云端更新逻辑
								uni.showToast({
									title: '重命名成功',
									icon: 'success'
								});
							} else if (!newName) {
								uni.showToast({
									title: '名称不能为空',
									icon: 'none'
								});
							}
						}
					}
				});
			},

			deleteVoice(voice, index) {
				uni.showModal({
					title: '确认删除',
					content: `您确定要删除音色 "${voice.name}" 吗？`,
					success: (res) => {
						if (res.confirm) {
							// 删除本地显示
							this.voiceList.splice(index, 1);
							// 这里可以添加云端删除逻辑
							uni.showToast({
								title: '删除成功',
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
		display: flex;
		flex-direction: column;
		min-height: 100vh;
		color: #333;
		position: relative;
		padding-bottom: 180rpx; /* 为底部固定按钮留出空间 */
	}

	/* 自定义导航栏 */
	.custom-nav-bar {
		position: relative;
		display: flex;
		justify-content: center;
		align-items: center;
		height: 90rpx;
		padding-top: var(--status-bar-height);
		z-index: 1;
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

	/* 音色列表 */
	.voice-list-section {
		flex: 1;
		padding: 40rpx;
		z-index: 1;
	}

	.tip {
		font-size: 28rpx;
		color: #666;
		margin-bottom: 40rpx;
		text-align: center;
		background-color: rgba(255, 255, 255, 0.8);
		padding: 20rpx;
		border-radius: 15rpx;
	}
	
	.voice-grid {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		gap: 30rpx;
	}

	.voice-card {
		position: relative;
		background-color: #FFFFFF;
		border-radius: 20rpx;
		padding: 30rpx;
		display: flex;
		flex-direction: column;
		align-items: flex-start;
		gap: 15rpx;
		box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.08);
		border: 4rpx solid transparent;
		transition: all 0.2s ease-in-out;
		min-height: 160rpx;
	}
	
	.voice-card.is-default {
		border-color: #007AFF;
		box-shadow: 0 8rpx 20rpx rgba(0, 122, 255, 0.2);
	}

	.voice-icon {
		width: 50rpx;
		height: 50rpx;
		margin-bottom: 10rpx;
	}

	.voice-info {
		display: flex;
		flex-direction: column;
		gap: 5rpx;
		flex: 1;
	}

	.voice-name {
		font-size: 32rpx;
		font-weight: bold;
		color: #333;
	}

	.voice-details {
		font-size: 24rpx;
		color: #999;
	}

	.default-badge {
		position: absolute;
		top: 0;
		right: 0;
		background-color: #007AFF;
		color: white;
		padding: 4rpx 12rpx;
		border-top-right-radius: 20rpx;
		border-bottom-left-radius: 20rpx;
		font-size: 22rpx;
	}

	/* 添加音色按钮 */
	.add-voice-button-container {
		position: fixed;
		bottom: 0;
		left: 0;
		right: 0;
		padding: 40rpx;
		background-color: transparent;
		z-index: 100;
		padding-bottom: calc(40rpx + var(--safe-area-inset-bottom));
	}

	.add-voice-button {
		background-color: #28a745;
		color: #FFFFFF;
		font-size: 36rpx;
		font-weight: bold;
		border-radius: 50rpx;
		height: 100rpx;
		line-height: 100rpx;
		text-align: center;
		width: 100%;
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
</style>
