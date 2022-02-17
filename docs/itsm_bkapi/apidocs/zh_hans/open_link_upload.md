##### 简要描述

- 外链功能:文件上传

##### 请求URL
- ` /openapi/ticket/upload/ `
  
##### 请求方式
- POST

##### 参数

|参数名|必选|类型|说明|
|:----    |:---|:----- |-----   |
|token |是  |string| 鉴权token  |



##### 返回示例 

``` 
{
   {
    "result": true,
    "code": "OK",
    "message": "success",
    "data": {
		“succeed_files”：{
			...
		}
		},
    ]
}
}
```
