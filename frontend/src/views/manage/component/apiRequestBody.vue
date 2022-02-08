<template>
  <div class="bk-request-body">
    <ul class="child-node" v-if="!treeIndex">
      <li class="vue-tree-item">
        <div :class="['tree-node',{ 'down': true,'set-frist-pLeft': true,'active': true }]">
          <!-- 业务需求 -->
          <div class="bk-tree-body-form">
            <div class="bk-body-content">
              <div class="bk-content-left-body" style="padding-right: 5px;">
                <i class="bk-icon" style="
                                float: left;
                                width: 24px;
                                height: 32px;
                                line-height: 32px;"></i>
                <div style="float: left;
                                width: calc(100% - 100px);
                                margin-right: 3px;">
                  {{ '属性' }}
                </div>
                <div style="float: left;
                                margin-left: 5px;
                                width: 65px;">
                  {{ '是否必须' }}
                </div>
              </div>
              <div class="bk-content-right-body">
                <div class="bk-value-type">
                  {{ '类型' }}
                </div>
                <div class="bk-desc" :class="{ 'bk-big-desc': !isBody }">
                  {{ '备注' }}
                </div>
                <div class="bk-value-default" v-if="isBody">
                  {{ '默认值' }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </li>
    </ul>
    <ul class="child-node">
      <li class="vue-tree-item" v-for="(item, index) in treeDataList" :key="index">
        <div
          :class="['tree-node',
          { 'down': item.showChildren,
          'set-frist-pLeft': treeIndex + 1 === 1,'active': item.checkInfo }]"
          @click="toggle(item)">
          <!-- 业务需求 -->
          <div class="bk-tree-body-form">
            <div class="bk-body-content">
              <div class="bk-content-left-body" :style="pLeft">
                <i v-if="!item.showChildren && item.type === 'object'"
                   class="bk-icon icon-right-shape"
                   :class="{ 'bk-padding': !item.has_children }"
                   @click.stop="item.showChildren = true"></i>
                <i v-else-if="item.type === 'object'"
                   class="bk-icon icon-down-shape"
                   :class="{ 'bk-padding': !item.has_children }"
                   @click.stop="item.showChildren = false"></i>
                <i class="bk-icon" v-else style="
                                    float: left;
                                    width: 24px;
                                    height: 36px;
                                    line-height: 36px;"></i>
                <div class="bk-body-input">
                  <bk-input
                    :clearable="false"
                    :disabled="(!item.parentInfo && item.key === 'root')
                    || item.parentInfo.type === 'array' || isBuiltin"
                    :placeholder="'请输入'"
                    v-model="item.key">
                  </bk-input>
                </div>
                <div class="bk-body-check">
                  <bk-checkbox
                    :disabled="(!item.parentInfo && item.key === 'root')
                    || item.parentInfo.type === 'array' || isBuiltin"
                    :true-value="trueStatus"
                    :false-value="falseStatus"
                    v-model="item.is_necessary">
                  </bk-checkbox>
                </div>
              </div>
              <div class="bk-content-right-body">
                <div class="bk-value-type">
                  <bk-select
                    v-model="item.type"
                    :clearable="false"
                    :font-size="'medium'"
                    :disabled="!item.parentInfo && item.key === 'root' || isBuiltin"
                    @selected="changeType(item)">
                    <bk-option
                      v-for="option in treeTypeList"
                      :key="option.id"
                      :id="option.id"
                      :name="option.name">
                    </bk-option>
                  </bk-select>
                </div>
                <div class="bk-desc" :class="{ 'bk-big-desc': !isBody }">
                  <bk-input
                    :clearable="false"
                    :disabled="!item.parentInfo && item.key === 'root' || isBuiltin"
                    :placeholder="'备注'"
                    v-model="item.desc">
                  </bk-input>
                </div>
                <div class="bk-value-default" v-if="isBody">
                  <template v-if="item.type === 'boolean'">
                    <bk-radio-group v-model="item.default">
                      <bk-radio :value="trueStatus" class="mr10">true</bk-radio>
                      <bk-radio :value="falseStatus">false</bk-radio>
                    </bk-radio-group>
                  </template>
                  <template v-else>
                    <bk-input
                      :type="item.type === 'INT' ? 'number' : 'text'"
                      v-model="item.default"
                      :placeholder="'请输入默认值'"
                      :disabled="item.type !== 'string' && item.type !== 'number' && item.type !== 'boolean'">
                    </bk-input>
                  </template>
                </div>
              </div>
            </div>
            <div class="bk-design-add" v-if="!isBuiltin">
              <span class="bk-add-node">
                <i class="custom-icon-font icon-add-circle bk-itsm-icon"></i>
                <div class="bk-add-other"
                     v-if="item.parentInfo.type === 'object' || item.type === 'object'">
                  <ul>
                    <li v-if="item.parentInfo && item.parentInfo.type === 'object'"
                        :title="'兄弟节点'" @click.stop="addBrotherLine(item)">
                      <span>{{ "兄弟节点" }}</span>
                    </li>
                    <li
                      v-if="item.type === 'object' || (item.type === 'array'
                      && (!item.children || !item.children.length))"
                      :title="'子节点'" @click.stop="addChildLine(item)">
                      <span>{{ "子节点" }}</span>
                    </li>
                  </ul>
                </div>
              </span>
              <span v-if="item.parentInfo.type === 'object'"
                    class="bk-reduce-node"
                    @click.stop="deleteLine(item)">
                  <i class="bk-icon icon-minus-circle-shape bk-itsm-icon"></i>
              </span>
            </div>
          </div>
        </div>
        <collapse-transition>
          <template v-if="item.children && item.showChildren">
            <exportTree
              :is-body="isBody"
              :is-builtin="isBuiltin"
              :tree-data-list="item.children"
              :tree-index="treeIndex + 1"
              @selectItem="selectItem"
              @toggle="toggle"
              @toggleChildren="toggleChildren"
              @addBrotherLine="addBrotherLine"
              @addChildLine="addChildLine"
              @deleteLine="deleteLine">
            </exportTree>
          </template>
        </collapse-transition>
      </li>
    </ul>
  </div>
</template>

<script>
import collapseTransition from '../mixins/collapse-transition';

export default {
  name: 'ExportTree',
  components: {
    collapseTransition,
  },
  props: {
    isBuiltin: {
      type: Boolean,
      default() {
        return false;
      },
    },
    isBody: {
      type: Boolean,
      default() {
        return false;
      },
    },
    treeDataList: {
      type: Array,
      default: () => [],
    },
    treeIndex: {
      type: Number,
      default: () => 0,
    },
  },
  data() {
    return {
      pLeft: `padding-left:${15 * (this.treeIndex)}px; padding-right: 5px;`,
      treeTypeList: [
        { id: 'string', name: 'string' },
        { id: 'object', name: 'object' },
        { id: 'number', name: 'number' },
        { id: 'boolean', name: 'boolean' },
        { id: 'array', name: 'array' },
      ],
      trueStatus: true,
      falseStatus: false,
    };
  },
  methods: {
    // 展开子级
    toggleChildren(item) {
      this.$emit('toggleChildren', item);
    },
    toggle(item) {
      this.$emit('toggle', item);
    },
    // 组件内调用组件，需要抛出数据两次
    selectItem(item) {
      this.$emit('selectItem', item);
    },
    // 新增数据
    addBrotherLine(item) {
      this.$emit('addBrotherLine', item);
    },
    addChildLine(item) {
      this.$emit('addChildLine', item);
    },
    deleteLine(item) {
      this.$emit('deleteLine', item);
    },
    changeType(item) {
      this.$set(item, 'children', []);
      if (item.type === 'array') {
        this.addChildLine(item);
      }
    },
  },
};
</script>

<style lang="postcss" scoped>
@import '../../../css/clearfix.css';
@import '../../../css/scroller.css';

.tree-node {
  position: relative;
  padding-left: 20px;
  line-height: 32px;
  height: 32px;
  font-size: 14px;
  font-weight: 400;
  color: #63656E;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 10px;

  .icon-down-shape,
  .icon-right-shape {
    color: #C4C6CC;
  }

  &.set-frist-pLeft {
    padding-left: 20px !important;
  }

  &.down {
    transition: all 0.3s ease;
  }
}

.icon-down-shape,
.icon-right-shape {
  float: left;
  width: 24px;
  height: 32px;
  line-height: 32px;
}

.bk-tree-body-form {
  width: 100%;
  @minix clearfix;

  .bk-body-content {
    margin-left: 0px;
    width: calc(100% - 70px);
    float: left;
    @minix clearfix;
  }

  .bk-design-add {
    width: 70px;
    float: right;
  }

  .bk-content-left-body {
    width: 45%;
    float: left;

    .bk-body-check {
      float: left;
      width: 30px;
      margin-left: 5px;
      text-align: center;
    }

    .bk-body-input {
      float: left;
      width: calc(100% - 100px);
      margin-right: 3px;
    }
  }

  .bk-content-right-body {
    float: left;
    width: 55%;
    @minix clearfix;

    .bk-value-type {
      float: left;
      width: 30%;
      padding-right: 10px;
    }

    .bk-desc {
      float: left;
      width: 40%;
      padding-right: 10px;
    }

    .bk-big-desc {
      float: left;
      width: 70%;
      padding-right: 10px;
    }

    .bk-value-default {
      float: left;
      width: 30%;
      padding-right: 10px;
    }
  }

  .bk-reduce-node,
  .bk-add-node {
    width: 27px;
    height: 36px;
    display: inline-block;
    text-align: center;
    line-height: 36px;
    cursor: pointer;
    font-size: 18px;

    .bk-itsm-icon {
      color: #C4C6CC;

      &:hover {
        color: #979BA5;
      }

      cursor: pointer;
    }
  }

  .bk-add-node {
    position: relative;

    &:hover {
      .bk-add-other {
        display: block;
      }
    }
  ;

    .bk-add-other {
      position: absolute;
      top: 8px;
      right: -70px;
      width: 79px;
      background: #fff;
      box-shadow: 0px 2px 2px 2px rgba(227, 225, 225, 0.5);
      border-radius: 2px;
      z-index: 10;
      display: none;

      ul {
        width: 100%;
        height: 100%;

        li {
          width: 100%;
          height: 36px;
          line-height: 36px;
          color: #63656E;
          text-align: center;
          cursor: pointer;
          font-size: 14px;

          &:hover {
            background: rgba(163, 197, 253, 0.2);
            color: #3A84FF;
          }
        }
      }

    }
  }

  .bk-reduce-disable {
    background-color: #fafafa;
    border: 1px solid #c3cdd7;
    cursor: not-allowed;
    color: #aaa;
  }
}

input[disabled] {
  border: 1px solid #c3cdd7;
  background: #fafafa;
  cursor: not-allowed;
}

</style>
