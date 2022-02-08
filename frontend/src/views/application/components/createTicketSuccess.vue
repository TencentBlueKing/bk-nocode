<template>
  <div class="create-ticket-success">
    <div class="success-tip-content">
      <div class="icon-wrapper">
        <i class="bk-icon icon-check-circle"></i>
        <p>提单成功</p>
        <div class="desc">当前流程已跳转到至下一流程节点，{{ count }}s将自动跳转至流程详情查看</div>
      </div>
      <div class="btn-action">
        <bk-button @click="$emit('back')">继续提单</bk-button>
        <bk-button theme="primary" @click="goToDetail">查看流程详情</bk-button>
      </div>
    </div>
  </div>
</template>
<script>
export default {
  name: 'createTicketSuccess',
  props: {
    id: Number,
  },
  data() {
    return {
      count: 30,
      timer: null,
    };
  },
  mounted() {
    this.setCountDown();
  },
  beforeDestroy() {
    if (this.timer) {
      clearTimeout(this.timer);
    }
  },
  methods: {
    setCountDown() {
      if (this.count > 0) {
        this.timer = setTimeout(() => {
          this.count -= 1;
          this.setCountDown();
        }, 1000);
      } else {
        this.goToDetail();
      }
    },
    goToDetail() {
      this.$router.push({ name: 'processDetail', params: { id: this.id } });
    },
  },
};
</script>
<style lang="postcss" scoped>
.create-ticket-success {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  .success-tip-content {
    text-align: center;
  }
  .icon-wrapper {
    & > i {
      font-size: 56px;
      color: #2dcb56;
    }
    & > p {
      margin: 20px 0 8px;
      color: #000000;
      font-size: 16px;
      line-height: 1;
    }
    .desc {
      color: #63656e;
      font-size: 12px;
    }
  }
  .btn-action {
    margin-top: 40px;
  }
}
</style>
