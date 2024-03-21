import json
from netCDF4 import Dataset
import numpy as np

nc_path = './rhum.2011.nc'

nc = Dataset(nc_path)

data_dict = {}
# print(nc)
data_dict['fileFormat'] = nc.file_format
# 读取文件信息
for i in nc.ncattrs():
    attr = nc.getncattr(i)
    data_dict[i] = attr
    # print(attr)

# 读取维度数据
dimensions = {}
for dim_var in nc.dimensions.keys():
    dimension_attrs = {}
    dimension_info = nc.dimensions[dim_var]
    dimension_attrs['name'] = dimension_info.name
    dimension_attrs['size'] = dimension_info.size
    if (dimension_info.isunlimited()):
        dimension_attrs['unlimited'] = dimension_info.isunlimited()
    dimensions[dim_var] = dimension_attrs
    # print(dimension_info)

data_dict['dimensions'] = dimensions

# print(nc.groups)

# 读取变量数据
variables = {}
for var_name in nc.variables.keys():
    variable_info = nc.variables[var_name]
    # print(variable_info)
    variable_attrs = {}
    variable_attrs['name'] = variable_info.name
    variable_attrs['size'] = variable_info.size
    variable_attrs['shape'] = variable_info.shape
    variable_attrs['dimensions'] = variable_info.dimensions
    # print(variable_info.dtype)
    
    # 读取变量属性信息
    for attr_name in variable_info.ncattrs():
        attr_value = variable_info.getncattr(attr_name)
        
        # 检查属性值是否为NumPy数组，如果是，将其转换为列表
        if isinstance(attr_value, np.ndarray):
            attr_value = attr_value.tolist()

        # 如果属性值是NumPy类型，将其转换为Python原生类型
        if isinstance(attr_value, np.generic):
            attr_value = attr_value.item()

        variable_attrs[attr_name] = attr_value

    # 读取变量的值
    variable_values = variable_info[:]
    variable_attrs['datatype'] = variable_values.dtype.name

    if(var_name != 'rhum'):
        if isinstance(variable_values, np.ndarray):
            variable_attrs["values"] = variable_values.tolist()
        elif isinstance(variable_values, np.generic):
            variable_attrs["values"] = variable_values.item()
    else:
        variable_data = variable_values.flatten()
        filled_data = variable_data.filled(variable_info.getncattr('missing_value'))
        filename = f'{var_name}.bin'
        filled_data.tofile(filename)
        variable_attrs["values"] = filename
    variables[var_name] = variable_attrs

data_dict['variables'] = variables

# 保存到json
with open('rhum2011.json','w') as fp:
    json.dump(data_dict, fp)
    
print('done')
