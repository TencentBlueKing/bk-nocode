<template>
  <div class="quick-entrance">
    <div class="img-container">
      <img :src="base64String+page.config.path" v-if="page.config.path">
      <img :src="defaultImg" v-else>
    </div>
    <div class="text-container">
      <span class="title" v-bk-overflow-tips="{ width: 140 }">{{page.config.name}}</span>
      <span class="desc" v-bk-overflow-tips="{ width: 140 }" v-if="page.config.desc">{{page.config.desc}}</span>
    </div>
  </div>
</template>

<script>
export default {
  name: 'QuickEntrance',
  props: {
    src: [String],
    title: [String],
    desc: [String],
    page: {
      type: Object,
      default: () => ({}),
    },
  },
  data() {
    return {
      base64String: 'data:image/jpeg;base64,',
      defaultImg: require('@/assets/images/s-marker-logo.svg'),
    };
  },
};
</script>

<style scoped lang="postcss">
.quick-entrance {
  height: 92px;
  background: #FFFFFF;
  border-radius: 4px;
  margin: 24px 12px 0 0;
  display: flex;
  align-items: center;
}

.img-container {
  width: 40px;
  height: 40px;
  border-radius: 4px;
  margin-left: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;

  img {
    width: 100%;
    height: 100%;
  }
}

.text-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  height: 40px;
  margin-left: 12px;
  width:calc(100% - 80px) ;
  .title {
    font-weight: 500;
    font-size: 16px;
    color: #313238;
    display: inline-block;
    min-width: 140px;
    //max-width: ;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
  }

  .desc {
    font-weight: 400;
    font-size: 14px;
    color: #979BA5;
    display: inline-block;
    width: 140px;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
  }
}
</style>
