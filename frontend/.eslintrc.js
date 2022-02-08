module.exports = {
  parser: 'vue-eslint-parser',
  parserOptions: {
    parser: '@babel/eslint-parser',
    ecmaVersion: 2019,
    // ECMAScript modules 模式
    sourceType: 'module',
    ecmaFeatures: {
      // 不允许 return 语句出现在 global 环境下
      globalReturn: false,
      // 开启全局 script 模式
      impliedStrict: true,
      jsx: true,
    },
    // 即使没有 babelrc 配置文件，也使用 babel-eslint 来解析
    requireConfigFile: false,
    // 仅允许 import export 语句出现在模块的顶层
    allowImportExportEverywhere: false,
  },
  env: {
    browser: true,
    node: true,
    commonjs: true,
    es6: true,
  },
  // 以当前目录为根目录，不再向上查找 .eslintrc.js
  root: true,
  extends: ['plugin:vue/recommended', 'prettier'],
  // required to lint *.vue files
  plugins: ['vue', 'prettier'],
  rules: {
    /**
     * 不要在中括号中添加空格
     */
    'array-bracket-spacing': ['error', 'never'],
    /**
     * 数组的方法除了 forEach 之外，回调函数必须有返回值
     */
    'array-callback-return': 'warn',
    /**
     * 要求箭头函数体使用大括号
     */
    'arrow-body-style': ['warn', 'as-needed'],
    /**
     * 要求箭头函数的参数使用圆括号
     */
    'arrow-parens': [
      'warn',
      'as-needed',
      {
        requireForBlockBody: true,
      },
    ],
    /**
     * 强制箭头函数的箭头前后使用一致的空格
     */
    'arrow-spacing': 'warn',
    /**
     * 要求打开的块标志和同一行上的标志拥有一致的间距。此规则还会在同一行关闭的块标记和前边的标记强制实施一致的间距。
     */
    'block-spacing': 'error',
    /**
     * 强制在代码块中使用一致的大括号风格
     */
    'brace-style': 'error',
    /**
     * 使用驼峰命名法（camelCase）命名对象、函数和实例。
     */
    camelcase: [
      'error',
      {
        ignoreDestructuring: true,
        properties: 'never',
      },
    ],
    /**
     * 添加尾随逗号
     */
    'comma-dangle': [
      'warn',
      {
        arrays: 'always-multiline',
        objects: 'always-multiline',
        imports: 'always-multiline',
        exports: 'always-multiline',
        functions: 'ignore',
      },
    ],
    /**
     * 强制在逗号前后使用一致的空格
     */
    'comma-spacing': [
      'error',
      {
        before: false,
        after: true,
      },
    ],
    /**
     * 强制使用一致的逗号风格
     */
    'comma-style': ['error', 'last'],
    /**
     * 强制在计算的属性的方括号中使用一致的空格
     */
    'computed-property-spacing': ['warn', 'never'],
    /**
     * 禁止使用 foo['bar']，必须写成 foo.bar
     */
    'dot-notation': 'warn',
    /**
     * 要求或禁止文件末尾存在空行
     */
    'eol-last': ['error', 'always'],
    /**
     * 必须使用 === 或 !==，禁止使用 == 或 !=
     */
    eqeqeq: ['warn', 'always'],
    /**
     * 要求或禁止在函数标识符和其调用之间有空格
     */
    'func-call-spacing': ['error', 'never'],
    /**
     * 必须只使用函数声明或只使用函数表达式
     */
    'func-style': ['off', 'expression'],
    /**
     * 强制在函数括号内使用一致的换行
     */
    'function-paren-newline': ['warn', 'multiline'],
    /**
     * 强制 generator 函数中 * 号周围使用一致的空格
     */
    'generator-star-spacing': [
      'warn',
      {
        before: false,
        after: true,
      },
    ],
    /**
     * 限制变量名长度
     */
    'id-length': 'off',
    /**
     * 强制隐式返回的箭头函数体的位置
     */
    'implicit-arrow-linebreak': ['warn', 'beside'],
    /**
     * 使用 2 个空格缩进
     */
    indent: [
      'warn',
      2,
      {
        SwitchCase: 1,
        VariableDeclarator: 1,
        outerIIFEBody: 1,
        FunctionDeclaration: {
          parameters: 1,
          body: 1,
        },
        FunctionExpression: {
          parameters: 1,
          body: 1,
        },
        CallExpression: {
          arguments: 1,
        },
        ArrayExpression: 1,
        ObjectExpression: 1,
        ImportDeclaration: 1,
        flatTernaryExpressions: false,
        ignoredNodes: [
          'JSXElement',
          'JSXElement > *',
          'JSXAttribute',
          'JSXIdentifier',
          'JSXNamespacedName',
          'JSXMemberExpression',
          'JSXSpreadAttribute',
          'JSXExpressionContainer',
          'JSXOpeningElement',
          'JSXClosingElement',
          'JSXFragment',
          'JSXOpeningFragment',
          'JSXClosingFragment',
          'JSXText',
          'JSXEmptyExpression',
          'JSXSpreadChild',
        ],
        ignoreComments: false,
      },
    ],
    /**
     * 强制在对象字面量的属性中键和值之间使用一致的间距
     */
    'key-spacing': 'error',
    /**
     * 强制在关键字前后使用一致的空格
     */
    'keyword-spacing': [
      'error',
      {
        overrides: {
          if: {
            after: true,
          },
          for: {
            after: true,
          },
          while: {
            after: true,
          },
          else: {
            after: true,
          },
        },
      },
    ],
    /**
     * 只允许使用 unix 的 LF 作为换行符，Windows 的 CRLF 不可以使用
     */
    'linebreak-style': ['warn', 'unix'],
    /**
     * 强制一行的最大长度，限制单行不能超过100个字符，字符串和正则表达式除外。
     */
    'max-len': [
      'error',
      {
        code: 120,
        ignoreStrings: true,
        ignoreUrls: true,
        ignoreRegExpLiterals: true,
        ignoreTemplateLiterals: true,
      },
    ],
    /**
     * 只有在命名构造器或者类的时候，才用帕斯卡拼命名法（PascalCase），即首字母大写。
     */
    'new-cap': [
      'error',
      {
        newIsCap: true,
        newIsCapExceptions: [],
        capIsNew: false,
        capIsNewExceptions: ['Immutable.Map', 'Immutable.Set', 'Immutable.List'],
        properties: false,
      },
    ],
    /**
     * 在编写多个方法链式调用(超过两个方法链式调用)时。 使用前导点，强调这行是一个方法调用，而不是一个语句。
     */
    'newline-per-chained-call': [
      'warn',
      {
        ignoreChainWithDepth: 2,
      },
    ],
    /**
     * 使用字面量语法创建数组。
     */
    'no-array-constructor': ['error'],
    /**
     * 在 case 和 default 的子句中，如果存在声明 (例如. let, const, function, 和 class)，使用大括号来创建块级作用域。
     */
    'no-case-declarations': 'error',
    /**
     * 避免搞混箭头函数符号 (=>) 和比较运算符 (<=, >=)。
     */
    'no-confusing-arrow': 'warn',
    /**
     * 禁止对使用 const 定义的常量重新赋值
     */
    'no-const-assign': 'error',
    /**
     * 禁止重复定义类的成员
     */
    'no-dupe-class-members': 'error',
    /**
     * 禁止在 else 内使用 return，必须改为提前结束
     */
    'no-else-return': [
      'warn',
      {
        allowElseIf: false,
      },
    ],
    /**
     * 禁止使用 eval
     */
    'no-eval': 'error',
    /**
     * 不要使用迭代器。
     * @reason 推荐使用 JavaScript 的高阶函数代替 for-in。
     */
    'no-iterator': 'warn',
    /**
     * 禁止在循环内的函数内部出现循环体条件语句中定义的变量
     */
    'no-loop-func': 'error',
    /**
     * 禁止混合使用不同的操作符:
     * - 禁止 `%`, `**` 之间混用
     * - 禁止 `%` 与其它运算符之间混用
     * - 禁止乘除运算符之间混用
     * - 禁止位运算符之间的任何混用
     * - 禁止比较运算符之间混用
     * - 禁止 `&&`, `||` 之间混用
     */
    'no-mixed-operators': [
      'error',
      {
        groups: [
          ['%', '**'],
          ['%', '+'],
          ['%', '-'],
          ['%', '*'],
          ['%', '/'],
          ['&', '|', '<<', '>>', '>>>'],
          ['==', '!=', '===', '!=='],
          ['&&', '||'],
        ],
        allowSamePrecedence: false,
      },
    ],
    /**
     * 禁止连续赋值，比如 foo = bar = 1
     */
    'no-multi-assign': 'error',
    /**
     * 不要使用多个空行填充代码。
     */
    'no-multiple-empty-lines': 'error',
    /**
     * 禁止使用嵌套的三元表达式，比如 a ? b : c ? d : e
     */
    'no-nested-ternary': 'warn',
    /**
     * 禁止使用 new Function
     * @reason 这和 eval 是等价的
     */
    'no-new-func': 'error',
    /**
     * 禁止直接 new Object
     */
    'no-new-object': 'error',
    /**
     * 禁止使用 new 来生成 String, Number 或 Boolean
     */
    'no-new-wrappers': 'warn',
    /**
     * 禁止对函数的参数重新赋值
     */
    'no-param-reassign': [
      'warn',
      {
        props: true,
        ignorePropertyModificationsFor: [
          'acc',
          'accumulator',
          'e',
          'ctx',
          'req',
          'request',
          'res',
          'response',
          '$scope',
          'staticContext',
          'state',
        ],
      },
    ],
    /**
     * 禁止使用 ++ 或 --
     */
    'no-plusplus': [
      'error',
      {
        allowForLoopAfterthoughts: true,
      },
    ],
    /**
     * 禁止使用 hasOwnProperty, isPrototypeOf 或 propertyIsEnumerable
     */
    'no-prototype-builtins': 'error',
    /**
     * 计算指数时，可以使用 ** 运算符。
     */
    'no-restricted-properties': [
      'warn',
      {
        object: 'Math',
        property: 'pow',
        message: 'Please use ** instand',
      },
    ],
    /**
     * 推荐使用 JavaScript 的高阶函数代替 for-in
     */
    'no-restricted-syntax': [
      'warn',
      {
        selector: 'ForInStatement',
        message:
          'for..in loops iterate over the entire prototype chain, which is virtually never what you want. Use Object.{keys,values,entries}, and iterate over the resulting array.',
      },
      {
        selector: 'LabeledStatement',
        message: 'Labels are a form of GOTO; using them makes code confusing and hard to maintain and understand.',
      },
      {
        selector: 'WithStatement',
        message: '`with` is disallowed in strict mode because it makes code impossible to predict and optimize.',
      },
    ],
    /**
     * 避免在行尾添加空格。
     */
    'no-trailing-spaces': 'error',
    /**
     * 变量应先声明再使用，禁止引用任何未声明的变量，除非你明确知道引用的变量存在于当前作用域链上。
     */
    'no-undef': ['error'],
    /**
     * 禁止变量名出现下划线
     */
    'no-underscore-dangle': 'warn',
    /**
     * 必须使用 !a 替代 a ? false : true
     */
    'no-unneeded-ternary': 'warn',
    /**
     * 已定义的变量必须使用
     * 但不检查最后一个使用的参数之前的参数
     * 也不检查 rest 属性的兄弟属性
     */
    'no-unused-vars': [
      'error',
      {
        args: 'after-used',
        ignoreRestSiblings: true,
      },
    ],
    /**
     * 禁止出现没必要的 constructor
     */
    'no-useless-constructor': 'warn',
    /**
     * 禁止出现没必要的转义
     */
    'no-useless-escape': 'error',
    /**
     * 禁止使用 var
     */
    'no-var': 'error',
    /**
     * 禁止属性前有空白
     */
    'no-whitespace-before-property': 'warn',
    /**
     * 强制单个语句的位置
     */
    'nonblock-statement-body-position': ['error', 'beside'],
    /**
     * 强制在大括号中使用一致的空格
     */
    'object-curly-spacing': ['warn', 'always'],
    /**
     * 将对象方法、属性简写，且间歇属性放在前面。
     */
    'object-shorthand': 'warn',
    /**
     * 禁止变量申明时用逗号一次申明多个
     */
    'one-var': ['warn', 'never'],
    /**
     * 避免在赋值语句 = 前后换行。如果你的代码单行长度超过了 max-len 定义的长度而不得不换行，那么使用括号包裹。
     */
    'operator-linebreak': [
      'error',
      'before',
      {
        overrides: {
          '=': 'none',
        },
      },
    ],
    /**
     * 要求或禁止块内填充
     */
    'padded-blocks': ['error', 'never'],
    /**
     * 要求回调函数使用箭头函数
     */
    'prefer-arrow-callback': 'warn',
    /**
     * 申明后不再被修改的变量必须使用 const 来申明
     */
    'prefer-const': [
      'error',
      {
        destructuring: 'any',
        ignoreReadBeforeAssign: false,
      },
    ],
    /**
     * 优先使用解构赋值
     */
    'prefer-destructuring': [
      'warn',
      {
        VariableDeclarator: {
          array: false,
          object: true,
        },
        AssignmentExpression: {
          array: true,
          object: false,
        },
      },
      {
        enforceForRenamedProperties: false,
      },
    ],
    /**
     * 必须使用 ...args 而不是 arguments
     */
    'prefer-rest-params': 'warn',
    /**
     * 必须使用 ... 而不是 apply，比如 foo(...args)
     */
    'prefer-spread': 'warn',
    /**
     * 必须使用模版字符串而不是字符串连接
     */
    'prefer-template': 'error',
    /**
     * 要求对象字面量属性名称用引号括起来
     */
    'quote-props': [
      'error',
      'as-needed',
      {
        keywords: false,
      },
    ],
    /**
     * 使用单引号 '' 定义字符串
     */
    quotes: [
      'warn',
      'single',
      {
        allowTemplateLiterals: false,
      },
    ],
    /**
     * parseInt 必须传入第二个参数
     */
    radix: 'warn',
    /**
     * 要加分号
     */
    semi: ['error', 'always'],
    /**
     * 强制在块之前使用一致的空格
     */
    'space-before-blocks': 'error',
    /**
     * 强制在 function 的左括号之前使用一致的空格
     */
    'space-before-function-paren': [
      'error',
      {
        anonymous: 'always',
        named: 'never',
        asyncArrow: 'always',
      },
    ],
    /**
     * 强制在圆括号内使用一致的空格
     */
    'space-in-parens': ['error', 'never'],
    /**
     * 要求操作符周围有空格
     */
    'space-infix-ops': 'error',
    /**
     * 注释的斜线或 * 后必须有空格
     */
    'spaced-comment': ['error', 'always'],
    /**
     * 要求或禁止模板字符串中的嵌入表达式周围空格的使用
     */
    'template-curly-spacing': ['error', 'never'],
    /**
     * 要求立即执行的函数使用括号括起来
     */
    'wrap-iife': ['error', 'outside'],
    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/array-bracket-spacing.md
    'vue/array-bracket-spacing': ['error', 'never'],

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/arrow-spacing.md
    'vue/arrow-spacing': ['error', { before: true, after: true }],

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/attribute-hyphenation.md
    'vue/attribute-hyphenation': ['error', 'always'],

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/attributes-order.md
    // 属性顺序，不限制
    'vue/attributes-order': 'off',

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/block-spacing.md
    'vue/block-spacing': ['error', 'always'],

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/brace-style.md
    'vue/brace-style': ['error', '1tbs', { allowSingleLine: false }],

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/camelcase.md
    // 后端数据字段经常不是驼峰，所以不限制 properties，也不限制解构
    'vue/camelcase': ['error', { properties: 'never', ignoreDestructuring: true }],

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/comma-dangle.md
    // 禁止使用拖尾逗号，如 {demo: 'test',}
    'vue/comma-dangle': 0,

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/comment-directive.md
    // vue 文件 template 中允许 eslint-disable eslint-enable eslint-disable-line eslint-disable-next-line
    // 行内注释启用/禁用某些规则，配置为 1 即允许
    'vue/comment-directive': 1,

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/component-name-in-template-casing.md
    // 组件 html 标签的形式，连字符形式，所有 html 标签均会检测，如引入第三方不可避免，可通过 ignores 配置，支持正则，不限制
    'vue/component-name-in-template-casing': 'off',

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/dot-location.md
    // 等待 https://github.com/vuejs/eslint-plugin-vue/pull/794 合入
    // 'vue/dot-location': ['error', 'property'],

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/eqeqeq.md
    'vue/eqeqeq': ['error', 'always', { null: 'ignore' }],

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/html-closing-bracket-newline.md
    // 单行写法不需要换行，多行需要，不限制
    'vue/html-closing-bracket-newline': 'off',

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/html-closing-bracket-spacing.md
    'vue/html-closing-bracket-spacing': [
      'error',
      {
        startTag: 'never',
        endTag: 'never',
        selfClosingTag: 'always',
      },
    ],

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/html-end-tags.md
    'vue/html-end-tags': 'error',

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/html-quotes.md
    'vue/html-quotes': ['error', 'double'],

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/html-self-closing.md
    // html tag 是否自闭和，不限制
    'vue/html-self-closing': 'off',

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/jsx-uses-vars.md
    // 当变量在 `JSX` 中被使用了，那么 eslint 就不会报出 `no-unused-vars` 的错误。需要开启 eslint no-unused-vars 规则才适用
    'vue/jsx-uses-vars': 1,

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/key-spacing.md
    'vue/key-spacing': ['error', { beforeColon: false, afterColon: true }],

    // 关键字周围空格一致性，在关键字前后保留空格，如 if () else {}
    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/keyword-spacing.md
    // 等待 https://github.com/vuejs/eslint-plugin-vue/pull/795 合入
    // 'vue/keyword-spacing': ['error', {'before': true, 'after': true}],

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/match-component-file-name.md
    // 组件名称属性与其文件名匹配，不限制
    'vue/match-component-file-name': 'off',

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/max-attributes-per-line.md
    // 每行属性的最大个数，不限制
    'vue/max-attributes-per-line': 'off',

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/multiline-html-element-content-newline.md
    // 在多行元素的内容前后需要换行符，不限制
    'vue/multiline-html-element-content-newline': 'off',

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/mustache-interpolation-spacing.md
    // template 中 {{var}}，不限制
    'vue/mustache-interpolation-spacing': 'off',

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/name-property-casing.md
    'vue/name-property-casing': 'off',

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/no-async-in-computed-properties.md
    'vue/no-async-in-computed-properties': 'error',

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/no-boolean-default.md
    'vue/no-boolean-default': 'off',

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/no-confusing-v-for-v-if.md
    'vue/no-confusing-v-for-v-if': 'error',

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/no-dupe-keys.md
    // 二级属性名禁止重复
    'vue/no-dupe-keys': 'error',

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/no-duplicate-attributes.md
    // 禁止 html 元素中出现重复的属性
    'vue/no-duplicate-attributes': 'error',

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/no-empty-pattern.md
    // 等待 https://github.com/vuejs/eslint-plugin-vue/pull/798 合入
    // 禁止解构中出现空 {} 或 []
    // 'vue/no-empty-pattern': 'error',

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/no-multi-spaces.md
    // 删除 html 标签中连续多个不用于缩进的空格
    'vue/no-multi-spaces': 'error',

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/no-parsing-error.md
    // 禁止语法错误
    'vue/no-parsing-error': 'error',

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/no-reserved-keys.md
    // 禁止使用保留字
    'vue/no-reserved-keys': 'error',

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/no-restricted-syntax.md
    // 禁止使用特定的语法
    'vue/no-restricted-syntax': 'off',

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/no-shared-component-data.md
    // data 属性必须是函数
    'vue/no-shared-component-data': 'error',

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/no-side-effects-in-computed-properties.md
    // 禁止在计算属性对属性进行修改，不限制
    'vue/no-side-effects-in-computed-properties': 'off',

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/no-spaces-around-equal-signs-in-attribute.md
    'vue/no-spaces-around-equal-signs-in-attribute': 'error',

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/no-template-key.md
    // 禁止在 <template> 中使用 key 属性，不限制
    'vue/no-template-key': 'off',

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/no-template-shadow.md
    'vue/no-template-shadow': 'error',

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/no-textarea-mustache.md
    'vue/no-textarea-mustache': 'error',

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/no-unused-components.md
    // 禁止 components 中声明的组件在 template 中没有使用
    'vue/no-unused-components': 'error',

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/no-unused-vars.md
    'vue/no-unused-vars': 'error',

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/no-use-v-if-with-v-for.md
    // 禁止 v-for 和 v-if 在同一元素上使用，不限制
    'vue/no-use-v-if-with-v-for': 'off',

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/no-v-html.md
    // 禁止使用 v-html，防止 xss
    'vue/no-v-html': 'off',

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/object-curly-spacing.md
    // 对象写在一行时，大括号里需要空格
    'vue/object-curly-spacing': ['error', 'always'],

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/order-in-components.md
    // 官方推荐顺序
    'vue/order-in-components': [
      'error',
      {
        order: [
          'el',
          'name',
          'parent',
          'functional',
          ['delimiters', 'comments'],
          ['components', 'directives', 'filters'],
          'extends',
          'mixins',
          'inheritAttrs',
          'model',
          ['props', 'propsData'],
          'data',
          'computed',
          'watch',
          'LIFECYCLE_HOOKS',
          'methods',
          ['template', 'render'],
          'renderError',
        ],
      },
    ],

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/prop-name-casing.md
    // 组件 props 属性名驼峰命名
    'vue/prop-name-casing': ['error', 'camelCase'],

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/require-component-is.md
    // <component> 元素必须要有 :is 属性
    'vue/require-component-is': 'error',

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/require-default-prop.md
    // props 必须要有默认值，不限制
    'vue/require-default-prop': 'off',

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/require-direct-export.md
    // 组件必须要直接被 export。不限制
    'vue/require-direct-export': 'off',

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/require-prop-type-constructor.md
    // props 的 type 必须为构造函数，不能为字符串。
    'vue/require-prop-type-constructor': 'error',

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/require-prop-types.md
    // props 必须要有 type。
    'vue/require-prop-types': 'error',

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/require-render-return.md
    // render 函数必须要有返回值
    'vue/require-render-return': 'error',

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/require-v-for-key.md
    // v-for 指令必须要有 key 属性
    'vue/require-v-for-key': 'error',

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/require-valid-default-prop.md
    // props 默认值必须有效。不限制
    'vue/require-valid-default-prop': 'off',

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/return-in-computed-property.md
    // 计算属性必须要有返回值
    'vue/return-in-computed-property': 'error',

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/singleline-html-element-content-newline.md
    // 单行 html 元素后面必须换行。不限制
    'vue/singleline-html-element-content-newline': 'off',

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/space-infix-ops.md
    // 二元操作符两边要有空格
    'vue/space-infix-ops': 'off',

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/space-unary-ops.md
    // new, delete, typeof, void, yield 等后面必须有空格，一元操作符 -, +, --, ++, !, !! 禁止有空格
    'vue/space-unary-ops': ['error', { words: true, nonwords: false }],

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/this-in-template.md
    // 不允许在 template 中使用 this
    'vue/this-in-template': ['error', 'never'],

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/use-v-on-exact.md
    // 强制使用精确修饰词。不限制
    'vue/use-v-on-exact': 'off',

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/v-bind-style.md
    // v-bind 指令的写法。不限制
    'vue/v-bind-style': 'off',

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/v-on-function-call.md
    // 强制或禁止在 v-on 指令中不带参数的方法调用后使用括号。不限制
    'vue/v-on-function-call': 'off',

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/v-on-style.md
    // v-on 指令的写法。限制简写
    'vue/v-on-style': ['error', 'shorthand'],

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/valid-template-root.md
    // 根节点必须合法
    'vue/valid-template-root': 'error',

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/valid-v-bind.md
    // v-bind 指令必须合法
    'vue/valid-v-bind': 'error',

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/valid-v-cloak.md
    // v-cloak 指令必须合法
    'vue/valid-v-cloak': 'error',

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/valid-v-else-if.md
    // v-else-if 指令必须合法
    'vue/valid-v-else-if': 'error',

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/valid-v-else.md
    // v-else 指令必须合法
    'vue/valid-v-else': 'error',

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/valid-v-for.md
    // valid-v-for 指令必须合法
    'vue/valid-v-for': 'error',

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/valid-v-html.md
    // v-html 指令必须合法
    'vue/valid-v-html': 'error',

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/valid-v-if.md
    // v-if 指令必须合法
    'vue/valid-v-if': 'error',

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/valid-v-model.md
    // v-model 指令必须合法
    'vue/valid-v-model': 'error',

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/valid-v-on.md
    // v-on 指令必须合法
    'vue/valid-v-on': 'error',

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/valid-v-once.md
    // v-once 指令必须合法
    'vue/valid-v-once': 'error',

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/valid-v-pre.md
    // v-pre 指令必须合法
    'vue/valid-v-pre': 'error',

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/valid-v-show.md
    // v-show 指令必须合法
    'vue/valid-v-show': 'error',

    // https://github.com/vuejs/eslint-plugin-vue/blob/master/docs/rules/valid-v-text.md
    // v-text 指令必须合法
    'vue/valid-v-text': 'error',
  },
};
