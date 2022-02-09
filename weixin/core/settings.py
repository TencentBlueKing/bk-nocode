# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making BK-ITSM 蓝鲸流程服务 available.

Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.

BK-ITSM 蓝鲸流程服务 is licensed under the MIT License.

License for BK-ITSM 蓝鲸流程服务:
--------------------------------------------------------------------
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial
portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import os

import config.default as settings

# 解决多级nginx代理下遇到的最外层nginx的`X-Forwarded-Host`设置失效问题
X_FORWARDED_WEIXIN_HOST = 'HTTP_X_FORWARDED_WEIXIN_HOST'

# 是否开启使用
USE_WEIXIN = os.environ.get("BKAPP_USE_WEIXIN", None) == '1'
# 是否为企业微信
IS_QY_WEIXIN = os.environ.get("BKAPP_IS_QY_WEIXIN", None) == '1'
# django 配置, 可使用自定义HOST
USE_X_FORWARDED_HOST = USE_WEIXIN
# 微信公众号的app id/企业微信corp id
WEIXIN_APP_ID = os.environ.get("BKAPP_WEIXIN_APP_ID", '')
# 微信公众号的app secret/企业微信应用的secret
WEIXIN_APP_SECRET = os.environ.get("BKAPP_WEIXIN_APP_SECRET", '')
# 该蓝鲸应用对外暴露的外网域名，即配置的微信能回调或访问的域名，如：test.bking.com
WEIXIN_APP_EXTERNAL_HOST = os.environ.get("BKAPP_WEIXIN_APP_EXTERNAL_HOST", '')

# 应用授权作用域
# snsapi_base （不弹出授权页面，直接跳转，只能获取用户openid），
# snsapi_userinfo （弹出授权页面，可通过openid拿到昵称、性别、所在地。并且， 即使在未关注的情况下，只要用户授权，也能获取其信息 ）
WEIXIN_SCOPE = 'snsapi_userinfo'
# 蓝鲸微信请求URL前缀

WEIXIN_SITE_URL = settings.SITE_URL + 'weixin/'
# 蓝鲸微信本地静态文件请求URL前缀
WEIXIN_STATIC_URL = settings.STATIC_URL + 'weixin/'
# 蓝鲸微信登录的URL
WEIXIN_LOGIN_URL = settings.SITE_URL + 'weixin/login/'
# 微信分享地址
WEIXIN_SHARE_URL = WEIXIN_APP_EXTERNAL_HOST + settings.SITE_URL
