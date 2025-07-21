<template>
  <view class="container">
    <view class="status-card">
      <text class="title">机器人状态</text>
      <view v-if="robotStatus && robotStatus.current_pose">
        <text>坐标: ({{ robotStatus.current_pose.x.toFixed(2) }}, {{ robotStatus.current_pose.y.toFixed(2) }})</text>
        <text>角度: {{ robotStatus.current_pose.theta.toFixed(2) }}</text>
        <text>电量: {{ robotStatus.power_percent }}%</text>
        <text>移动状态: {{ robotStatus.move_status }}</text>
      </view>
      <view v-else>
        <text>正在获取状态...</text>
      </view>
    </view>

    <view class="control-card">
      <text class="title">发送指令</text>
      <button class="control-button" @click="sendMoveCommand" :disabled="isCommandRunning">移动到 (1.0, 2.0)</button>
      <view v-if="lastCommand" class="command-feedback">
        <text>上一条指令状态: {{ formattedCommandStatus }}</text>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  computed: {
    isCommandRunning() {
      if (!this.lastCommand) return false;
      const runningStatus = ['pending', 'sent'];
      return runningStatus.includes(this.lastCommand.status);
    },
    formattedCommandStatus() {
      if (!this.lastCommand) return '无';
      switch (this.lastCommand.status) {
        case 'pending':
        case 'sent':
          return '机器人处理中...';
        case 'completed':
          return '执行完成';
        case 'failed':
          return '执行失败';
        default:
          return '未知';
      }
    }
  },
  data() {
    return {
      robotStatus: null,
      lastCommand: null,
    };
  },
  onLoad() {
    this.initialize();
    this.listenToPush();
  },
  methods: {
    // 1. 初始化
    async initialize() {
      console.log("Initializing page...");
      // 页面加载时，获取一次最新的状态
      this.fetchStatus();
      // 注册客户端ID
      this.registerClientId();
    },
    
    // 2. 注册推送
    registerClientId() {
      uni.getPushClientId({
        success: (res) => {
          console.log('Successfully get client id:', res.cid);
          uniCloud.callFunction({
            name: 'updateClientInfo',
            data: { cid: res.cid }
          }).then(() => {
            console.log('Client ID registered to cloud.');
          }).catch(err => {
            console.error('Failed to register Client ID:', err);
          });
        },
        fail(err) {
          console.error('Failed to get client id:', err);
        }
      });
    },

    // 3. 监听推送消息
    listenToPush() {
      uni.onPushMessage((res) => {
        console.log("Received push message:", res);
        if (res.type === 'click') {
          // 这是点击通知栏的消息
          const payload = res.data.payload;
          this.handlePushPayload(payload);
        } else if (res.type === 'receive') {
          // 这是应用在前台时收到的透传消息
          this.handlePushPayload(res.data);
        }
      });
    },
    
    // 4. 处理推送内容
    handlePushPayload(payload) {
        if (typeof payload === 'string') {
            try {
                payload = JSON.parse(payload);
            } catch(e) {
                console.error("Failed to parse push payload:", e);
                return;
            }
        }
        
        console.log("Handling push payload:", payload);
        if (payload.type === 'status_updated') {
            console.log("Handling status_updated push.");
            this.robotStatus = payload.status;
        } else if (payload.type === 'command_updated') {
            console.log("Handling command_updated push.");
            this.lastCommand = payload.command;
        }
    },

    // 5. 主动获取状态（仅初始化时调用）
    fetchStatus() {
      uniCloud.callFunction({
        name: 'getRobotStatus'
      }).then(res => {
        if (res.result && res.result.success) {
          this.robotStatus = res.result.status;
        }
      }).catch(err => {
        console.error("Failed to fetch robot status:", err);
      });
    },
    
    // 6. 发送指令
    sendMoveCommand() {
      const command = '/api/move?marker=test_point';
      const params = {
        type: 'move',
        name: 'test_point',
        x: 1.0,
        y: 2.0,
        theta: 90.0
      };

      uni.showLoading({ title: '发送指令中...' });

      uniCloud.callFunction({
        name: 'sendRobotCommand',
        data: { command: command, params: params }
      }).then(res => {
        uni.hideLoading();
        if (res.result && res.result.success && res.result.command) {
          this.lastCommand = res.result.command;
          uni.showToast({ title: '指令已发送', icon: 'success' });
        } else {
          throw new Error(res.result.message || '发送失败');
        }
      }).catch(err => {
        uni.hideLoading();
        uni.showToast({ title: err.message || '发送失败', icon: 'none' });
      });
    }
  }
};
</script>

<style>
.container {
  padding: 20px;
  background-color: #f4f4f4;
  min-height: 100vh;
}
.status-card, .control-card {
  background-color: #fff;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 10px;
  display: block;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}
.status-card text {
  display: block;
  margin-top: 5px;
  color: #333;
}
.control-button {
  width: 100%;
  height: 45px;
  background-color: #007aff;
  color: white;
  border: none;
  border-radius: 5px;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 10px;
}
.control-button[disabled] {
  background-color: #c8c7cc;
}
.command-feedback {
  margin-top: 15px;
  padding: 10px;
  background-color: #f0f0f0;
  border-radius: 5px;
  text-align: center;
}
</style>
