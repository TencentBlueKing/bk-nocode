<template>
  <div class="card-container">
    <div class="card-info">
      <div class="card-header">
        <span class="card-title" :title="userGroup.name">{{ userGroup.name }}</span>
        <div class="operation-area">
          <bk-button
            :text="true"
            title="primary"
            class="operate-btn"
            @click="$emit('handleClick',{ card: userGroup,type: 'setting' })">
            权限设置
          </bk-button>
          <bk-button
            :text="true"
            title="primary"
            class="operate-btn"
            @click="$emit('handleClick',{ card: userGroup,type: 'add' })">
            添加人员
          </bk-button>
          <bk-button
            :text="true"
            title="primary"
            class="operate-btn"
            @click="$emit('handleClick',{ card: userGroup,type: 'delete' })">
            删除
          </bk-button>
        </div>
      </div>
      <span class="card-desc">{{ userGroup.desc }}</span>
    </div>
    <div class="show-members">
            <member-tag
              v-for="item in currentShowTag"
              :key="item.id"
              @delete="handleDelete"
              :member="item">
            </member-tag>
    </div>
  </div>
</template>

<script>
import memberTag from './memberTag.vue';

export default {
  name: 'PermissionCard',
  components: {
    memberTag,
  },
  props: {
    userGroup: {
      type: Object,
      delete: () => {
      },
    },
  },
  computed: {
    department() {
      return this.$store.state.setting.departmentsTree;
    },
    member() {
      return this.userGroup.users.members ? this.userGroup.users.members.map(item => ({
        username: item,
        display_name: item,
      })) : [];
    },
    currentShowTag() {
      return this.checkedDepartment(this.department, this.userGroup.users.departments || []).concat(this.member);
    },
  },
  methods: {
    checkedDepartment(val, departments, result = []) {
      val.forEach((item) => {
        if (departments.includes(item.id)) {
          result.push(item);
        }
        if (item.children) {
          this.checkedDepartment(item.children, departments, result);
        }
      });
      return result;
    },
    handleDelete(tag) {
      this.$emit('deleteCard', tag, this.userGroup);
    },

  },
};
</script>

<style scoped>
.card-container {
  position: relative;
  margin-top: 24px;
  padding: 24px;
  min-height: 134px;;
  background: #fff;
  box-shadow: 0 2px 4px 0 rgba(25, 25, 41, 0.05);
  border-radius: 2px;
}

.card-header {
  display: inline-flex;
}

.card-title {
  margin: 0;
  color: #313238;
  line-height: 22px;
  width: 160px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: Bold;
  font-size: 16px;
  color: #313238;
}

.card-info {
  display: flex;
  flex-direction: column;
}

.operation-area {
  margin-left: 48px;
}

.operate-btn {
  margin-left: 16px;
  cursor: pointer;
}

.card-desc {
  margin-top: 12px;
  line-height: 20px;
  color: #63656e;
  overflow: hidden;
  word-break: break-all;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
  text-overflow: ellipsis;
  font-size: 16px;
}

.icon-area {
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: absolute;
  top: 8px;
  right: 8px;
  width: 60px;
  height: 34px;
}

.show-members{
  margin-top: 16px;
}
.cursor-pointer {
  cursor: pointer;
}
</style>
