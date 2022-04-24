<template>
  <div class="member-org-container">
    <div class="member-org-content">
      <div class="organization">
        <div class="organization-container">
          <div class="title">组织架构</div>
          <div class="search-input">
            <bk-input
              v-model="organizationValue"
              right-icon="bk-icon icon-search"
              placeholder="搜索"
              :clearable="true"
              @enter="handleSearch"
              @clear="handleSearchReset"
              @change="handleInputEmpty">
            </bk-input>
          </div>
          <div class="tree-select-wrapper">
            <bk-big-tree
              ref="orgTree"
              size="small"
              :data="searchMode ? searchResult : orgTree"
              :check-strictly="false"
              :show-checkbox="true"
              :default-checked-nodes="localValue.departments.concat(localValue.members).map(item => item.id)"
              :lazy-method="getChildNodes"
              :lazy-disabled="isLeafNode"
              @check-change="handleCheckNode">
            </bk-big-tree>
            <bk-exception
              v-if="!searchLoading && (searchMode ? searchResult.length === 0 : orgTree.length === 0)"
              class="exception-part"
              type="empty"
              scene="part">
              {{ searchMode ? '搜索结果为空' : '没有数据' }}
            </bk-exception>
          </div>
        </div>
      </div>
      <!--已选展示-->
      <div class="selected-data-wrapper">
        <div class="current-select-numbers">
          已经选择
          <span>{{ localValue.departments.length }}</span>
          组织,
          <span>{{ localValue.members.length }}</span>
          个用户
          <span :text="true" title="primary" class="rest-btn" @click="handleClearSelected"> 清除 </span>
        </div>
        <div class="organization-list">
          <div class="fullOrgList-container">
            <div class="check-organization">
              <span style="display: block">已选组织</span>
              <template v-if="localValue.departments.length > 0">
                <member-tag
                  v-for="dept in localValue.departments"
                  :member="dept"
                  :key="dept.id"
                  @delete="handleDelSelected(dept.id, 'department')">
                </member-tag>
              </template>
              <bk-exception v-else class="exception-wrap-item exception-part" type="empty" scene="part"></bk-exception>
            </div>
            <div class="check-member">
              <span style="display: block">已选人员</span>
              <template v-if="localValue.members.length > 0">
                <member-tag
                  v-for="user in localValue.members"
                  :key="user.id"
                  :member="user"
                  @delete="handleDelSelected(user.id, 'member')">
                </member-tag>
              </template>
              <bk-exception v-else class="exception-wrap-item exception-part" type="empty" scene="part"></bk-exception>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import memberTag from './memberTag.vue';
import cloneDeep from 'lodash.clonedeep';

export default {
  name: 'MemberPermission',
  components: {
    memberTag,
  },
  props: {
    value: {
      type: Object,
      default: () => ({ departments: [], members: [] }),
    },
    fullOrgList: {
      type: Array,
      default: () => [],
    },
    loading: {
      type: Boolean,
    },
  },
  data() {
    return {
      organizationValue: '',
      localValue: cloneDeep(this.value),
      orgTree: this.getFirstLevelData(this.fullOrgList),
      searchResult: [],
      searchMode: false,
      searchLoading: false,
    };
  },
  watch: {
    loading(val) {
      if (!val) {
        this.orgTree = this.getFirstLevelData(this.fullOrgList);
      }
    },
  },
  methods: {
    // 只获取第一层级的数据，层级内的组织架构数据在展开时获取，避免数据量过大导致初次渲染卡顿
    getFirstLevelData(data) {
      return data.map(item => {
        const nodeItem = { ...item };
        if (nodeItem.children) {
          nodeItem.children = [];
        }
        return nodeItem;
      });
    },
    // 是否为叶子结点，决定是否可以展开icon
    isLeafNode(node) {
      return !!node.data.isLeaf;
    },
    // 加载下一级组织架构数据或者具体人员
    async getChildNodes(node) {
      let childNodes = [];
      // 组织架构节点查找下一级组织架构数据
      if ('children' in node.data) {
        const { id, name } = node.data;
        const route = node.data.route.slice(0);
        route.push({ id, name });
        const routeLen = route.length;
        route.reduce((crtList, node, index) => {
          const nodeData = crtList.find(item => item.id === node.id);
          if (index === routeLen - 1) {
            childNodes = nodeData.children.map(item => {
              const nodeItem = { ...item };
              if (nodeItem.children) {
                nodeItem.children = [];
              }
              return nodeItem;
            });
          }
          return nodeData.children;
        }, this.fullOrgList);
      } else {
        // 拉取组织架构下具体人员
        const res = await this.$store.dispatch('setting/getUserByDepartment', { id: node.data.id });
        childNodes = res.data.map(item => {
          const { username, display_name: dispalyName } = item;
          return {
            id: username,
            isLeaf: true,
            name: `${username}${dispalyName ? `(${dispalyName})` : ''}`,
          };
        });
      }
      this.setCheckedNodes(childNodes);
      return { data: childNodes };
    },
    // 勾选节点
    handleCheckNode(checked, node) {
      const { isLeaf, id, name } = node.data;
      const data = isLeaf ? this.localValue.members : this.localValue.departments;
      const index = data.findIndex(item => item.id === id);
      if (index > -1) {
        data.splice(index, 1);
      } else {
        data.push({ id, name });
      }
    },
    // 异步设置的节点设置选中态
    setCheckedNodes(nodes) {
      const selected = this.localValue.departments.concat(this.localValue.members).map(item => item.id);
      const checkedIds = [];
      nodes.forEach(item => {
        if (selected.includes(item.id)) {
          return checkedIds.push(item.id);
        }
      });
      // 给节点设置checked属性不生效，需要调用方法动态设置
      setTimeout(() => {
        checkedIds.forEach(id => {
          this.$refs.orgTree.setChecked(id, true);
        });
      }, 0);
    },
    // 给单个节点设置选中状态的时候需要判断节点是否存在
    changeNodeCheckState(id, state = true) {
      const node = this.$refs.orgTree.getNodeById(id);
      if (node) {
        this.$refs.orgTree.setChecked(id, { checked: state });
      }
    },
    // 删除选中
    handleDelSelected(id, type) {
      const selected = type === 'department' ? this.localValue.departments : this.localValue.members;
      const index = selected.findIndex(item => item.id === id);
      selected.splice(index, 1);
      this.changeNodeCheckState(id, false);
    },
    // 清空选中
    handleClearSelected() {
      const selectedIds = this.localValue.departments.concat(this.localValue.members).map(item => item.id);
      selectedIds.forEach(id => {
        this.changeNodeCheckState(id, false);
      });
      this.localValue.departments = [];
      this.localValue.members = [];
    },
    async handleSearch(val) {
      try {
        this.searchLoading = true;
        this.searchMode = true;
        const params = { users: val, properties: 'username,display_name,id' };
        const res = await this.$store.dispatch('setting/getUser', params);
        const users = res.data.map(item => {
          const { username, display_name: dispalyName } = item;
          const name = `${username}${dispalyName ? `(${dispalyName})` : ''}`;
          return { id: username, name, isLeaf: true };
        });
        this.searchResult = users;
        console.log(res);
      } catch (e) {
        console.error(e);
      } finally {
        this.searchLoading = false;
      }
    },
    handleSearchReset() {
      this.searchMode = false;
      this.searchResult = [];
    },
    handleInputEmpty(val) {
      if (val === '') {
        this.handleSearchReset();
      }
    },
    getData() {
      return this.localValue;
    },
  },
};
</script>

<style scoped lang="postcss">
.member-org-container {
  padding: 24px;
  height: 100%;
  background: #ffffff;
  overflow: hidden;
}
.member-org-content {
  display: flex;
  justify-content: space-between;
  border: 1px solid #dcdee5;
  overflow: hidden;
}
.organization {
  width: 50%;
  min-height: 100%;
  border-right: 1px solid #dcdee5;
  .organization-container {
    padding: 16px 0;
    .title {
      padding: 0 16px;
      font-size: 14px;
      color: #313238;
    }
    .search-input {
      margin: 12px 16px;
    }
  }
  .tree-select-wrapper {
    padding: 0 16px;
    min-height: 300px;
    max-height: calc(100vh - 260px);
    overflow-y: auto;
  }
}
.selected-data-wrapper {
  padding: 16px 0;
  width: 50%;
  .current-select-numbers {
    padding: 0 16px;
    font-size: 14px;
    position: relative;
    color: #313238;
    span {
      color: #2dcb56;
      font-size: 14px;
      min-width: 20px;
      display: inline-block;
      text-align: center;
    }
    .rest-btn {
      display: inline-block;
      color: #3a84ff;
      position: absolute;
      top: 2px;
      right: 16px;
      cursor: pointer;
      font-size: 12px;
    }
  }
  .organization-list {
    padding: 0 16px;
    max-height: calc(100vh - 220px);
    overflow-y: auto;
  }
  .check-organization {
    font-size: 12px;
    color: #63656e;
    margin-top: 12px;
    min-height: 52px;
  }
  .check-member {
    font-size: 12px;
    color: #63656e;
    margin-top: 12px;
    min-height: 52px;
  }
}
</style>
