<template>
  <div class="member-container">
    <div class="organization">
      <div class="organization-container">
        <div class="title">组织架构</div>
        <div class="search-input">
          <bk-input
            clearable
            :placeholder="'搜索'"
            :right-icon="'bk-icon icon-search'"
            v-model="organizationValue"
            @enter="handlerIconClick"
            @clear="handleRestTree"
            @change="handleChange"
            @right-icon-click="handlerIconClick">
          </bk-input>
        </div>
        <bk-tree
          v-if="tree.length!==0"
          ref="tree"
          ext-cls="organization-tree"
          :node-key="'id'"
          :multiple="true"
          :show-icon="false"
          :show-checkbox="true"
          @on-expanded="handleExpandNode"
          @on-check="handleCheckNode"
          @async-load-nodes="asyncLoadNodes"
          :data="tree">
        </bk-tree>
      </div>
    </div>
    <!--已选展示-->
    <div class="check-members">
      <div class="organization-list">
        <div class="organizationList-container">
          <div class="title">
            已经选择<span>{{ currentDepartment.length }}</span>组织,<span>{{ currentUsers.length }}</span>个用户
            <span :text="true" title="primary" class="rest-btn" @click="handleDelete">
              删除
            </span>
          </div>
          <div class="check-organization">
            <span style="display: block">已选组织</span>
            <template v-if="currentDepartment.length!==0">
              <member-tag v-for="dept in currentDepartment" :member="dept" :key="dept.id"
                          @delete="handleDeleteDepartment">
              </member-tag>
            </template>
            <bk-exception v-else class="exception-wrap-item exception-part" type="empty" scene="part"></bk-exception>
          </div>
          <div class="check-member">
            <span style="display: block">已选人员</span>
            <template v-if="currentUsers.length!==0">
              <member-tag v-for="user in currentUsers" :key="user.username" :member="user"
                          @delete="handleDeleteMembers">
              </member-tag>
            </template>
            <bk-exception v-else class="exception-wrap-item exception-part" type="empty" scene="part"></bk-exception>
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
      default: () => ({}),
    },
    organizationList: {
      type: Array,
      default: () => ([]),
    },
    loading: {
      type: Boolean,
    },
  },
  data() {
    return {
      organizationValue: '',
      localValue: JSON.stringify(cloneDeep(this.value)) === '{}' ? { departments: [], members: [] } : this.init(cloneDeep(this.value)),
      tree: this.transNewTree(cloneDeep(this.organizationList), this.value.departments),
    };
  },
  computed: {
    currentUsers() {
      return this.localValue.members ? this.localValue.members.map(item => ({
        username: item, display_name: item,
      })) : [];
    },
    currentDepartment() {
      return this.localValue.departments
        ? this.getCurrentDepart(cloneDeep(this.organizationList), this.localValue.departments) : [];
    },
  },
  watch: {
    loading(val) {
      if (!val) {
        this.transNewTree(cloneDeep(this.organizationList), this.value.departments);
      }
    },
  },
  methods: {
    init(val) {
      const tempValue = val;
      if (!val.members) {
        tempValue.members = [];
      }
      if (!val.departments) {
        tempValue.departments = [];
      }
      return tempValue;
    },
    // 初始化树的结构 添加 checked async disabled 属性
    transNewTree(tree, departments = []) {
      tree.forEach((v) => {
        v.async = true;
        v.checked = false;
        v.disabled = false;
        if (departments.includes(v.id)) {
          v.checked = true;
        } else {
          const parentIdList = v.route.map(el => el.id).reverse();
          const parentIsSelect = parentIdList.some(id => departments.includes(id));
          if (parentIsSelect) {
            v.checked = true;
            v.disabled = true;
          }
        }
        if (v.children) {
          this.transNewTree(v.children, departments);
        }
      });
      return tree;
    },

    // 获取选中的部门信息
    getCurrentDepart(tree, departments = [], list = []) {
      tree.forEach((item) => {
        if (departments.includes(item.id)) {
          list.push({ id: item.id, name: item.name });
        } else if (item.children) {
          this.getCurrentDepart(item.children, departments, list);
        }
      });
      return list;
    },

    async asyncLoadNodes(node) {
      this.$set(node, 'loading', true);
      const { members = [] } = this.localValue;
      try {
        const res = await this.$store.dispatch('setting/getUserByDepartment', { id: node.id });
        res.data.forEach((el) => {
          // eslint-disable-next-line no-prototype-builtins
          if (!node.hasOwnProperty('children')) {
            this.$set(node, 'children', []);
          }
          el.name = el.display_name;
          el.id = el.username;
          // 有该成员 则选中

          if (node.checked) {
            el.checked = true;
            el.disabled = true;
          } else if (members.length > 0 && members.includes(el.id)) {
            el.checked = true;
            // 父节点选中 该节点disabled
          }
          node.children.push(el);
        });
      } catch (e) {
        console.warn(e);
      } finally {
        this.$set(node, 'loading', false);
      }
    },
    // 展开节点
    handleExpandNode(node, expanded) {
      // 判断是否该节点需要再次去加载数据
      const isExistchildren = !!((node.async && !node.children) || node.children.every(item => item.async));
      if (expanded && isExistchildren) {
        this.asyncLoadNodes(node);
      }
    },
    // 点击节点
    async handleCheckNode(node) {
      if (node.async) {
        if (!node.checked) {
          if (!node.parent) {
            this.localValue.departments = [];
            node.children && this.removeSelect(node);
          } else {
            this.localValue.departments.splice(this.localValue.departments.findIndex(val => val === node.id), 1);
            node.children && this.removeSelect(node);
          }
        } else {
          this.localValue.departments.push(node.id);
          node.children && this.handleSelect(node);
        }
      } else {
        !node.checked
          ? this.localValue.members.splice(this.localValue.members.findIndex(val => val === node.id), 1)
          : this.localValue.members.push(node.id);
      }
      const childIdList = node.parent ? node.parent.children.map(child => child.id) : [];
      const isSubset = this.isSubset(childIdList);
      if (node.async && node.parent && isSubset) {
        this.localValue.departments.push(node.parent.id);
        this.handleSelect(node.parent);
        for (let i = 0; i < childIdList.length; i++) {
          const departmentIndex = this.localValue.departments.findIndex(val => childIdList[i] === val);
          const memberIndex = this.localValue.members.findIndex(val => val === childIdList[i]);
          if (departmentIndex >= 0) {
            this.localValue.departments.splice(departmentIndex, 1);
          } else if (memberIndex >= 0) {
            this.localValue.members.splice(memberIndex, 1);
          }
        }
      } else if (node.async && !node.parent) {
        this.localValue.members = [];
      } else if (node.parent && isSubset) {
        this.localValue.departments.push(node.parent.id);
        this.handleSelect(node.parent);
        for (let i = 0; i < childIdList.length; i++) {
          const departmentIndex = this.localValue.departments.findIndex(val => childIdList[i] === val);
          const memberIndex = this.localValue.members.findIndex(val => val === childIdList[i]);
          if (departmentIndex >= 0) {
            this.localValue.departments.splice(departmentIndex, 1);
          } else if (memberIndex >= 0) {
            this.localValue.members.splice(memberIndex, 1);
          }
        }
      }
      // 人员节点
    },
    // 取消选中
    removeSelect(node) {
      node.children.forEach((child) => {
        child.checked = false;
        child.disabled = false;
        if (child.children) {
          return this.removeSelect(child);
        }
      });
    },
    // 选中
    handleSelect(node) {
      node.children.forEach((child) => {
        child.checked = true;
        child.disabled = true;
        if (child.children) {
          return this.handleSelect(child);
        }
      });
    },
    // 获取节点的路径
    getNodePath(tree, id) {
      let path;
      for (let i = 0; i < tree.length; i++) {
        if (tree[i].id === id) {
          path = tree[i].route.map(el => el.id);
          break;
        }
        if (tree[i].children) {
          path = this.getNodePath(tree[i].children, id);
          if (path) {
            break;
          }
        }
      }
      return path;
    },
    // 根据路径删除取消选中的节点
    // getNodeByPath(tree, id, path) {
    //   let node;
    //   const pathLen = path.length;
    //   for (let i = 0;i < pathLen;i++) {
    //     node  = tree.find(node => node.id === path[i]);
    //     if ()
    //   }
    //   return node;
    // },

    // 获取子节点的id
    getChildrenId(node, tempIds = []) {
      if (node.children) {
        node.children.forEach((item) => {
          tempIds.push(item.id);
          if (item.children) {
            this.getChildrenId(item);
          }
        });
      }
      return tempIds;
    },
    //  是否为已选集合的子集
    isSubset(arr) {
      return arr.every(item => [...this.localValue.members, ...this.localValue.departments].includes(item));
    },
    removeNodeById(tree, id) {
      let flag = false;
      for (let i = 0; i < tree.length; i++) {
        if (tree[i].id == id) {
          flag = true;
          tree[i].checked = false;
          if (tree[i].children) {
            this.removeSelect(tree[i]);
          }
          break;
        } else if (tree[i].children && tree[i].children.length > 0) {
          this.removeNodeById(tree[i].children, id);
          if (flag) {
            break;
          }
        }
      }
    },
    handleDeleteDepartment(val) {
      // 待优化
      this.removeNodeById(this.tree, val.id);
      this.localValue.departments.splice(this.localValue.departments.findIndex(val => val === val.id), 1);
    },
    handleDeleteMembers(val) {
      // 待优化
      this.removeNodeById(this.tree, val.username);
      this.localValue.members.splice(this.localValue.members.findIndex(item => item === val.username), 1);
    },
    handleDelete() {
      this.tree = this.organizationList;
      this.localValue = [];
    },
    async  handlerIconClick() {
      if (!!this.organizationValue) {
        await this.getUser();
      }
    },
    handleChange(val) {
      if (!val) {
        this.tree = this.transNewTree(cloneDeep(this.organizationList), this.value.departments);
      }
    },
    handleRestTree() {
      this.tree = this.transNewTree(cloneDeep(this.organizationList), this.value.departments);
    },
    // 搜索人员
    async getUser() {
      try {
        const params = { users: this.organizationValue, properties: 'username,display_name' };
        const res = await this.$store.dispatch('setting/getUser', params);
        this.tree = res.data.map(item => ({
          name: item.display_name,
          id: item.username,
          checked: this.localValue.members.includes(item.username),
        }));
      } catch (e) {
        console.warn(e);
      } finally {

      }
    },
    getData() {
      return this.localValue;
    },
  },
};
</script>

<style scoped lang="postcss">
.member-container {
  margin: 24px;
  width: 592px;
  min-height: 437px;
  background: #FFFFFF;
  border: 1px solid #DCDEE5;
  display: flex;

  .organization {
    flex: 1;
    border-right: 1px solid #DCDEE5;

    .organization-container {
      margin: 16px;

      .title {
        font-size: 14px;
        color: #313238;
      }

      .search-input {
        margin-top: 12px;
      }

      .organization-tree {
        margin-top: 12px;
      }
    }
  }

  .check-members {
    flex: 1;

    .organizationList-container {
      margin: 16px;

      .title {
        font-size: 14px;
        position: relative;
        color: #313238;

        span {
          color: #2DCB56;
          font-size: 14px;
          min-width: 20px;
          display: inline-block;
          text-align: center;
        }

        .rest-btn {
          display: inline-block;
          color: #3a84ff;
          position: absolute;
          top: 0;
          right: 0;
          cursor: pointer;
        }
      }

      .check-organization {
        font-size: 12px;
        color: #63656E;
        margin-top: 12px;
        min-height: 52px;;
      }

      .check-member {
        font-size: 12px;
        color: #63656E;
        margin-top: 12px;
        min-height: 52px;;
      }

    }
  }
}
</style>
