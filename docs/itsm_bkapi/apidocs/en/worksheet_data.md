##### A brief description

- Universal query: get list data according to filter conditions

##### Request URL
- `/openapi/data_instance/worksheet_data/`
  
##### request method
- POST

##### Parameters

|Parameter name|Required|Type|Description|
|:---- |:---|:----- |----- |
|token |yes |string |authentication token |
|fields |yes |string |query fields |
|conditions |No |dict |Search Conditions |


##### Return to example

````
{
   {
    "result": true,
    "code": "OK",
    "message": "success",
    "data": [
        {
            "id": ,
            "create_at": "",
            "update_at": "",
            "field_key": value,
            ...
        },
       ...
    ]
}
}
````
