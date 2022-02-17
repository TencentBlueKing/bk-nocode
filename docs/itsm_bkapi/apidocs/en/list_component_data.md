##### A brief description

- Get the data of a list component

##### Request URL
- ` /openapi/data_instance/list_component_data/ `
  
##### request method
- POST

##### Parameters

|Parameter name|Required|Type|Description|
|:---- |:---|:----- |----- |
|version_number |yes |string |version number |
|page_id |yes |string |list page id |
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
