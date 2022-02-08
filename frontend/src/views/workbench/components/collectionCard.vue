<template>
  <div :class="pageType === '' ? 'collection-card' : ''" class="card-wrapper">
    <div class="cart-content" :style="{ borderColor: cardInfo.bgColor || '#3a84ff' }">
      <span class="bk-icon icon-star content-icon" v-if="pageType !== 'FUNCTION'"></span>
      <span class="content-title">{{ cardInfo.name }}</span>
      <span class="application" v-if="pageType !== 'FUNCTION'">所属应用: {{ cardInfo.type }}</span>
      <div class="content-description">{{ cardInfo.desc }}</div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CollectionCard',
  props: {
    pageType: {
      type: String,
      default: '',
    },
    cardInfo: {
      type: Object,
      default: () => {},
    },
  },
  computed: {
    randomBackGround() {
      const bgList = [
        'linear-gradient(224deg, #6CBAFF 0%, #3A84FF 100%)',
        'linear-gradient(225deg, #FF8F8F 0%, #FF5656 100%)',
        'linear-gradient(225deg, rgba(212,190,252,0.99) 0%, #AA89F7 100%)',
        'linear-gradient(225deg, #FFCB02 0%, #FF9C01 100%);',
      ];
      return {
        'border-image': `${bgList[Math.floor(Math.random() * bgList.length)]}`,
      };
    },
  },
};
</script>

<style lang="postcss" scoped>
.collection-card {
  margin: 16px 16px 0 0;
}
.cart-content {
  position: relative;
  width: 276px;
  height: 160px;
  background: #ffffff;
  box-shadow: 0 2px 4px 0 rgba(25, 25, 41, 0.05);
  border-radius: 8px;
  border-top: 4px solid transparent;
  background-image: url('../../../assets/images/card-bg.svg');
  background-repeat: no-repeat;
  background-size: 276px 80px;
  background-position: bottom right;
}

.content-icon {
  position: absolute;
  left: 241px;
  top: 16px;
}

.content-title {
  display: inline-block;
  margin: 24px 0 0 24px;
  height: 22px;
  font-family: MicrosoftYaHei-Bold;
  font-size: 14px;
  font-weight: Bold;
  color: #313238;
  letter-spacing: 0;
  line-height: 22px;
}

.content-description {
  margin: 8px 0 0 24px;
  width: 228px;
  height: 82px;
  font-family: MicrosoftYaHei;
  font-size: 12px;
  color: #63656e;
  letter-spacing: 0;
  line-height: 20px;
  word-wrap: break-word;
}
</style>
