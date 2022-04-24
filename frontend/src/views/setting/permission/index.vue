<template>
  <section>
    <page-wrapper title="权限管理" v-bkloading="{ isLoading: userGroupLoading }">
      <template slot="header">
        <bk-button :theme="'primary'" :title="'应用发布'" @click="onReleaseClick"> 应用发布 </bk-button>
      </template>
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
            <bk-exception type="empty"></bk-exception>
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
          <bk-form-item label="用户组名称" property="name" :required="true" :error-display-type="'normal'">
            <bk-input v-model.trim="formBasic.name"></bk-input>
          </bk-form-item>
          <bk-form-item label="用户组描述" property="desc" :required="true" :error-display-type="'normal'">
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
      <div slot="content" style="height: 100%" v-bkloading="{ isLoading: sidesliderLoading }">
        <template v-if="sidesliderType === 'settingPermission'">
          <bk-tab :active.sync="active" style="margin-top: 20px" ext-cls="setting-tab" type="unborder-card">
            <bk-tab-panel name="menuPermission" label="菜单权限"></bk-tab-panel>
            <bk-tab-panel name="functionPermission" label="功能权限"></bk-tab-panel>
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
            :full-org-list="organizationList"
            :loading="sidesliderLoading"
            :value="currentUserGroup.users">
          </member-permission>
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
import release from '../mixin/release';
import cloneDeep from 'lodash.clonedeep';

export default {
  name: 'PermissionManage',
  components: {
    functionPermission,
    menuPermission,
    permissionCard,
    PageWrapper,
    memberPermission,
  },
  mixins: [release],
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
            message: '用户组名称为必填项',
            trigger: 'blur',
          },
        ],
        desc: [
          {
            required: true,
            message: '用户组描述为必填项',
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
        res.data.items.forEach(group => {
          // 新建用户组时接口返回users缺少members、departments字段
          if (Object.keys(group.users).length === 0) {
            Object.assign(group, { users: { members: [], departments: [] } });
          }
          const { departments, members } = group.users;
          departments.forEach((item, index, arr) => {
            if (['string', 'number'].includes(typeof item)) {
              arr[index] = { id: item, name: item };
            }
          });
          members.forEach((item, index, arr) => {
            if (['string', 'number'].includes(typeof item)) {
              arr[index] = { id: item, name: item };
            }
          });
        });
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
    handleDeleteCard(tag, userGroup) {
      this.currentUserGroup = userGroup;
      this.$bkInfo({
        type: 'warning',
        subTitle: `确认删除${tag.name}？`,
        confirmLoading: true,
        confirmFn: async () => {
          try {
            const { departments, members } = userGroup.users;
            let index = departments.findIndex(item => item.id === tag.id);
            if (index > -1) {
              departments.splice(index, 1);
            } else {
              index = members.findIndex(item => item === tag.id);
              members.splice(index, 1);
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
@import '../../../css/header-wrapper.css';
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
  height: 52px;
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
