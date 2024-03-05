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
    variable_info  = nc.variables[var_name]
    # print(variable_info)
    variable_attrs = {}
    for attr_name in variable_info.ncattrs():
        attr_value = variable_info.getncattr(attr_name)
        
        # 检查属性值是否为NumPy数组，如果是，将其转换为列表
        if isinstance(attr_value, np.ndarray):
            attr_value = attr_value.tolist()

        # 如果属性值是NumPy类型，将其转换为Python原生类型
        if isinstance(attr_value, np.generic):
            attr_value = attr_value.item()

        variable_attrs[attr_name] = attr_value

    variable_values = variable_info[:]
    if(var_name != 'rhum'):
        if isinstance(variable_values, np.ndarray):
            variable_attrs["values"] = variable_values.tolist()
        elif isinstance(variable_values, np.generic):
            variable_attrs["values"] = variable_values.item()
    else:
        variable_data = variable_values.flatten()
        # filled_data = variable_data.filled(variable_info.getncattr('missing_value'))
        # filled_data = variable_data.filled(0)
        # filename = f'{var_name}.bin'
        # filled_data.tofile(filename)
        mask_array = variable_data.mask
        data_array = variable_data.data
        data_array.tofile('data_filename.bin')
        np.array(mask_array, dtype=int).tofile('mask_filename.bin')
        variable_attrs["values"] = []
    variables[var_name] = variable_attrs

data_dict['variables'] = variables

# 保存到json
with open('data.json','w') as fp:
    json.dump(data_dict, fp, indent=4)
    
print('done')
