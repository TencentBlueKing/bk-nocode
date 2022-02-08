<template>
  <section>
    <page-wrapper title="权限管理" v-bkloading="{ isLoading: userGroupLoading }">
      <div class="list-table">
        <div class="operate-area">
          <bk-button theme="primary" icon="plus" @click="handleAddTemplate">新增用户组</bk-button>
        </div>
        <template v-if="userGroupList.length > 0">
          <permission-card
            v-for="userGroup in userGroupList"
            :key="userGroup.id"
            :user-group="userGroup"
            @delete="handleDeleteRole"
            @deleteCard="handleDeleteCard"
            @handleClick="handleClick">
          </permission-card>
        </template>
        <template v-else>
          <div class="no-data">
            <bk-exception type="empty"> </bk-exception>
          </div>
        </template>
      </div>
    </page-wrapper>
    <bk-dialog
      title="新建用户组"
      header-position="left"
      :mask-close="false"
      :auto-close="false"
      :width="640"
      :loading="templateDialogloading"
      :value="templateDialogShow"
      @confirm="onCreateTemplateConfirm"
      @cancel="onCreateTemplateCancel">
      <div class="form-basic-info">
        <bk-form form-type="vertical" :rules="basicRules" ref="roleForm" :model="formBasic">
          <bk-form-item label="用户组名称" property="name" :required="true">
            <bk-input v-model.trim="formBasic.name"></bk-input>
          </bk-form-item>
          <bk-form-item label="用户组描述" property="desc" :required="true">
            <bk-input type="textarea" :rows="7" v-model.trim="formBasic.desc"></bk-input>
          </bk-form-item>
        </bk-form>
      </div>
    </bk-dialog>
    <bk-sideslider
      :is-show.sync="sidesliderIsShow"
      :width="640"
      :title="sidesliderTitle"
      ext-cls="custom-sidelider"
      :before-close="handleClose">
      <div slot="content" v-bkloading="{ isLoading: sidesliderLoading }">
        <template v-if="sidesliderType === 'settingPermission'">
          <bk-tab :active.sync="active" style="margin-top: 20px" ext-cls="setting-tab" type="unborder-card">
            <bk-tab-panel name="menuPermission" label="菜单权限"> </bk-tab-panel>
            <bk-tab-panel name="functionPermission" label="功能权限"> </bk-tab-panel>
            <menu-permission
              v-if="active === 'menuPermission'"
              @checkNode="handleCheckNode"
              :tree-info="menuTree"
              :value="currentUserGroup.action_configs.page_view"></menu-permission>
            <function-permission
              :function-permission="functionPermission"
              v-if="functionPermission && functionPermission.length !== 0 && active === 'functionPermission'"
              :value="currentUserGroup.action_configs.action_execute"
              ref="functionPermission">
            </function-permission>
          </bk-tab>
        </template>
        <template v-if="sidesliderType === 'addMember'">
          <member-permission
            ref="memberPermission"
            :organization-list="organizationList"
            :loading="sidesliderLoading"
            :value="currentUserGroup.users"></member-permission>
        </template>
      </div>
      <div slot="footer" class="king-slider-footer">
        <bk-button theme="primary" @click="submit" :loading="submitPending"> 确定</bk-button>
        <bk-button theme="default" @click="handleClose" style="margin-left: 8px">取消</bk-button>
      </div>
    </bk-sideslider>
  </section>
</template>

<script>
import PageWrapper from '@/components/pageWrapper.vue';
import menuPermission from '../components/menuPermission.vue';
import functionPermission from '../components/functionPermission.vue';
import permissionCard from '../components/permissionCard.vue';
import memberPermission from '../components/memberPermission.vue';
import cloneDeep from 'lodash.clonedeep';

export default {
  name: 'PermissionTemplate',
  components: {
    functionPermission,
    menuPermission,
    permissionCard,
    PageWrapper,
    memberPermission,
  },
  props: {
    appId: String,
  },
  data() {
    return {
      active: 'menuPermission',
      sidesliderType: 'addMember',
      sidesliderTitle: '',
      templateDialogloading: false,
      templateDialogShow: false,
      sidesliderIsShow: false,
      userGroupLoading: false,
      sidesliderLoading: false,
      listData: [{}],
      submitPending: false,
      formBasic: {
        name: '',
        desc: '',
      },
      basicRules: {
        name: [
          {
            required: true,
            message: '必填项',
            trigger: 'blur',
          },
        ],
        desc: [
          {
            required: true,
            message: '必填项',
            trigger: 'blur',
          },
        ],
      },
      currentUserGroup: {},
      organizationList: [],
      userGroupList: [],
      menuPermission: {
        page_view: [],
        action_execute: [],
      },
      functionPermission: [],
      checkOrganizationList: [],
      checkedList: [],
      menuTree: [],
    };
  },
  created() {
    this.getUserGroup();
    this.getOrganization();
  },
  methods: {
    async handleAddTemplate() {
      this.templateDialogShow = true;
    },
    async addUserGroup() {
      const { desc, name } = this.formBasic;
      const params = {
        name,
        desc,
        project_key: this.appId,
      };
      try {
        this.templateDialogloading = true;
        const res = await this.$store.dispatch('setting/addUserGroup', params);
        if (res.result) {
          this.$bkMessage({
            message: '新增成功',
            theme: 'success',
          });
          this.getUserGroup();
          this.templateDialogShow = false;
        }
      } catch (e) {
        console.log(e);
      } finally {
        this.templateDialogloading = false;
      }
    },
    async getUserGroup() {
      try {
        this.userGroupLoading = true;
        const params = {
          project_key: this.appId,
        };
        const res = await this.$store.dispatch('setting/getUserGroup', params);
        this.userGroupList = res.data.items;
      } catch (e) {
        console.log(e);
      } finally {
        this.userGroupLoading = false;
      }
    },
    onCreateTemplateConfirm() {
      this.$refs.roleForm.validate().then(
        async validator => {
          await this.addUserGroup();
          await this.getUserGroup();
          this.formBasic = { name: '', desc: '' };
        },
        validator => {}
      );
    },
    onCreateTemplateCancel() {
      this.templateDialogShow = false;
      this.$refs.roleForm.clearError();
      this.formBasic = { name: '', desc: '' };
    },
    async submit() {
      const params = {
        ...this.currentUserGroup,
      };
      delete params.name;
      const message = '添加成功';
      if (this.sidesliderType === 'addMember') {
        params.users = this.$refs.memberPermission.getData();
      }
      if (this.sidesliderType === 'settingPermission') {
        // this.menuPermission.action_execute = this.$refs.functionPermission
        //   ? this.$refs.functionPermission.getData() : this.currentUserGroup.action_configs.action_execute;
        // params.action_configs = this.menuPermission;
        params.action_configs.action_execute = this.$refs.functionPermission
          ? this.$refs.functionPermission.getData()
          : this.currentUserGroup.action_configs.action_execute;
      }
      try {
        this.submitPending = true;
        const res = await this.$store.dispatch('setting/pathUpdateUserGroup', params);
        if (res.result) {
          this.$bkMessage({
            message: `${message}`,
            theme: 'success',
          });
          this.getUserGroup();
          this.sidesliderIsShow = false;
        }
      } catch (e) {
        console.log(e);
      } finally {
        this.submitPending = false;
      }
    },
    handleDeleteRole(card) {
      this.$bkInfo({
        type: 'warning',
        subTitle: '确认删除？',
        confirmLoading: true,
        confirmFn: async () => {
          try {
            const res = await this.$store.dispatch('setting/deleteUserGroup', { id: card.id });
            if (res.result) {
              this.$bkMessage({
                message: '删除成功',
                theme: 'success',
              });
            }
            this.getUserGroup();
          } catch (e) {
            console.error(e);
          } finally {
            this.appDeletePending = false;
          }
        },
      });
    },
    handleClose() {
      this.$bkInfo({
        title: '此操作会导致您的编辑没有保存，确认吗？',
        type: 'warning',
        width: 500,
        confirmFn: () => {
          this.sidesliderIsShow = false;
        },
      });
    },
    handleCheckNode(node) {
      const { type } = node;
      // eslint-disable-next-line camelcase
      const { page_view = [] } = this.currentUserGroup.action_configs;
      const pageViewId = cloneDeep(page_view).map(el => el.id);
      const pageView = cloneDeep(page_view);
      if (type === 'GROUP') {
        node.children.forEach(item => {
          if (!pageViewId.includes(item.id)) {
            pageViewId.push(item.id);
            pageView.push({ id: item.id, name: item.name });
          } else {
            pageViewId.splice(
              pageViewId.findIndex(el => el === item.id),
              1
            );
            pageView.splice(
              pageView.findIndex(el => el.id === item.id),
              1
            );
          }
        });
      } else {
        const { id, name } = node;
        if (!pageViewId.includes(id)) {
          pageViewId.push(id);
          pageView.push({ id, name });
        } else {
          pageViewId.splice(
            pageViewId.findIndex(el => el === id),
            1
          );
          pageView.splice(
            pageView.findIndex(el => el.id === id),
            1
          );
        }
      }
      this.currentUserGroup.action_configs.page_view = pageView;
    },
    handleClick($event) {
      const { card, type } = $event;
      this.active = 'menuPermission';
      switch (type) {
        case 'setting':
          this.settingPermission(card);
          this.currentUserGroup = card;
          this.menuPermission.page_view = card.action_configs.page_view;
          break;
        case 'add':
          this.currentUserGroup = card;
          this.addMembers();
          break;
        case 'delete':
          this.handleDeleteRole(card);
      }
    },
    async settingPermission(card) {
      this.sidesliderType = 'settingPermission';
      this.sidesliderIsShow = true;
      //  获取菜单
      this.getMenu();
      this.getDataFunction();
    },
    async getMenu() {
      try {
        this.sidesliderLoading = true;
        const res = await this.$store.dispatch('setting/getTreePage', { project_key: this.appId });
        this.menuTree = res.data[0].children;
      } catch (e) {
        console.error(e);
      } finally {
        this.sidesliderLoading = false;
      }
    },
    async getDataFunction() {
      const params = {
        project_key: this.appId,
      };
      try {
        this.sidesliderLoading = true;
        const res = await this.$store.dispatch('setting/getFunctionPermission', params);
        this.functionPermission = res.data;
      } catch (e) {
        console.error(e);
      } finally {
        this.sidesliderLoading = false;
      }
    },
    addMembers(card) {
      this.sidesliderIsShow = true;
      this.sidesliderTitle = '添加人员';
      this.sidesliderType = 'addMember';
      // const { departments = [] } = this.currentUserGroup.users;
      // this.organizationList = this.transNewTree(cloneDeep(this.organizationList), departments);
    },
    async getOrganization() {
      try {
        this.sidesliderLoading = true;
        const res = await this.$store.dispatch('setting/getOrganizations');
        this.organizationList = res.data;
        this.$store.commit('setting/setDepartmentsTree', cloneDeep(res.data));
      } catch (e) {
        console.log(e);
      } finally {
        this.sidesliderLoading = false;
      }
    },
    handleCheckOrganizationNode(node, tree) {
      const { checked } = node;
      const { departments = [], members = [] } = this.currentUserGroup.users;
      if (checked) {
        // 选择是一个部门且不存在
        if (node.async && !departments.includes(node.id)) {
          // if (node.id === 1) {
          //   this.currentUserGroup.users.departments = [1];
          //   this.currentUserGroup.users.members = [];
          // }
          // console.log(node);
          // // if (node.every(children => children.checked)) {
          // //
          // // }
          // const { departmentsTree } = this.$store.state.setting;
          // // 获取该节点所有的子节点
          // // 这里有点问题
          // const departmentIds = this.getOrganizationId(departmentsTree[0], node.id);
          // //  获取改节点已选择的id
          // const selectedIds  = this.getSelectedIds(tree[0]);
          // console.log('selectedIds', selectedIds);
          // console.log('departmentIds', departmentIds);
          // if (this.getIntersection(departments, departmentIds)) {
          //   this.currentUserGroup.users.departments.push(node.id);
          //   this.currentUserGroup.users.departments = departments
          //     .filter(department => !departmentIds.includes(department));
          // }
          // if (this.getIntersection(members, selectedIds)) {
          //   this.currentUserGroup.users.members = members
          //     .filter(member => !selectedIds.includes(member));
          // }
          // //  获取改节点已选择的id
          // const selectedIds  = this.getSelectedIds(tree[0]);
          // console.log('selectedIds', selectedIds);
          // if (node) {
          //
          //   //   取并集 如果已选的节点全部位于某个部门下 取消所有勾选节点 并且选中部门
          //
          // }
          departments.length > 0
            ? this.currentUserGroup.users.departments.push(node.id)
            : this.$set(this.currentUserGroup.users, 'departments', [node.id]);
        } else if (!node.async && !members.includes(node.id)) {
          // 选择是一个人员且 不存在
          members.length > 0
            ? this.currentUserGroup.users.members.push(node.id)
            : this.$set(this.currentUserGroup.users, 'members', [node.id]);
        }
      } else {
        const type = node.async ? 'departments' : 'members';
        // 删除对应的id
        this.currentUserGroup.users[type].splice(this.currentUserGroup.users[type].findIndex(item => node.id === item));
        if (type === 'departments') {
          this.setChildCanSelect(node);
        }
      }
    },
    getIntersection(arr1, arr2) {
      const map = arr2.reduce((r, i) => ((r[i] = true), r), {});
      return arr1.some(i => map[i]);
    },
    // 获取该节点所有的子节点
    getOrganizationId(department, id, list = []) {
      if (department.children) {
        department.children.forEach(item => {
          // item.parent
          if (item.parent && item.parent === id) {
            list.push(item.id);
          }
          if (item.children) {
            return this.getOrganizationId(item, item.id, list);
          }
        });
      }
      return list;
    },
    getSelectedIds(tree, list = []) {
      if (tree.children) {
        tree.children.forEach(item => {
          if (!item.async && item.checked) {
            if ((this.currentUserGroup.users.members || []).includes(item.id)) {
              list.push(...item.departments.map(el => el.id));
            }
          } else if (item.children) {
            return this.getSelectedIds(item, list);
          }
        });
      }
      return list;
    },
    // 设置子节点可选
    setChildCanSelect(node) {
      if (node.children) {
        node.children.forEach(item => {
          item.checked = false;
          item.disabled = false;
          if (item.children) {
            return this.setChildCanSelect(item);
          }
        });
      }
    },
    // 给组织架构树加上async异步请求  checked ,disabled
    getNewTree(arr) {
      return arr.map(v => {
        const item = {
          async: true,
          checked: false,
          disabled: false,
          ...v, // 这是创建的新对象 根据需要的键随意更改
        };
        if (v.children) item.children = this.getNewTree(v.children);
        return item;
      });
    },

    handleDelete(id, type) {
      this.currentUserGroup.users[type].splice(
        this.currentUserGroup.users[type].findIndex(item => item === id),
        1
      );
    },
    handleRest() {
      this.currentUserGroup.users = { members: [], departments: [] };
    },
    handleDeleteCard(tag, userGroup) {
      this.currentUserGroup = userGroup;
      const { async } = tag;
      this.$bkInfo({
        type: 'warning',
        subTitle: `确认删除${tag.name || tag.display_name}？`,
        confirmLoading: true,
        confirmFn: async () => {
          try {
            if (async) {
              this.currentUserGroup.users.departments.splice(
                this.currentUserGroup.users.departments.findIndex(item => item.id === tag.id),
                1
              );
            } else {
              this.currentUserGroup.users.members.splice(
                this.currentUserGroup.users.members.findIndex(item => item === tag.username),
                1
              );
            }
            const params = { ...this.currentUserGroup };
            delete params.name;
            const res = await this.$store.dispatch('setting/pathUpdateUserGroup', params);
            if (res.result) {
              this.$bkMessage({
                message: '删除成功',
                theme: 'success',
              });
            }
            this.getUserGroup();
          } catch (e) {
            console.error(e);
          } finally {
            this.appDeletePending = false;
          }
        },
      });
    },
  },
};
</script>

<style lang="postcss" scoped>
@import '../../../css/scroller.css';

.setting-tab {
  background: #ffffff;
  margin: 24px;

  /deep/ .bk-tab-section {
    padding: 16px 0 0 0;
  }
}

.list-table {
  margin: 24px;
}

.operate-area {
  position: relative;
  margin-bottom: 24px;

  .search-input {
    position: absolute;
    right: 0;
    top: 0;
    width: 240px;
  }
}

.member-container {
  margin: 24px;
  width: 592px;
  min-height: 437px;
  background: #ffffff;
  border: 1px solid #dcdee5;
  display: flex;

  .organization {
    flex: 1;
    border-right: 1px solid #dcdee5;
  }

  .check-member {
    flex: 1;
  }
}

/deep/ .custom-sidelider {
  .bk-sideslider-wrapper {
    @mixin scroller;

    .bk-sideslider-content {
      @mixin scroller;
      height: calc(100% - 60px) !important;

      .content {
        overflow-x: hidden;
      }
    }
  }
}

.king-slider-footer {
  z-index: 2;
  display: flex;
  align-items: center;
  width: 640px;
  height: 60px;
  padding-left: 20px;
  background-color: #fff;
  border-top: 1px solid #dcdee5;
}

.no-data {
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>
