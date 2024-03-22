import json
import os
from netCDF4 import Dataset
from datetime import datetime
import numpy as np

nc_path = './rhum.2011'
file_path = 'build'
output_path = os.path.join(file_path, nc_path)
os.makedirs(output_path, exist_ok=True)
nc = Dataset(nc_path + '.nc')

data_dict = {}
# print(nc)
metadata = {}
classInfo = {}
varInfo = {}
classInfo['文件格式'] = nc.file_format
data_dict['fileFormat'] = nc.file_format
# 读取文件信息
for i in nc.ncattrs():
    attr = nc.getncattr(i)
    data_dict[i] = attr
    # print(attr)

dimensionLength = 0
# 读取维度数据
dimensions = {}
for dim_var in nc.dimensions.keys():
    dimensionLength += 1
    dimension_attrs = {}
    dimension_info = nc.dimensions[dim_var]
    dimension_attrs['name'] = dimension_info.name
    dimension_attrs['size'] = dimension_info.size
    if (dimension_info.isunlimited()):
        dimension_attrs['unlimited'] = dimension_info.isunlimited()
    dimensions[dim_var] = dimension_attrs
    # print(dimension_info)


def int_to_chinese_numeral(value):
    digits = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九']
    units = ['', '十', '百', '千']
    result = ''
    if value == 0:
        return '零'
    if value < 0:
        result += '负'
        value = -value
    while value > 0:
        result = digits[value % 10] + units[len(result)] + result
        value //= 10
    return result+'维'


classInfo['栅格体元维度'] = int_to_chinese_numeral(dimensionLength)

data_dict['dimensions'] = dimensions

# print(nc.groups)


def precision_to_chinese(precision):
    if precision == 'float32':
        return '单精度'
    elif precision == 'float64':
        return '双精度'
    else:
        return '未知精度'


elements = {}
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
    units = variable_info.units
    if units == 'degrees_north' or units == 'degree_north' or units == 'degree_N' or units == 'degrees_N' or units == 'degreeN' or units == 'degreesN':
        classInfo['空间参考系'] = 'WGS1984_度(ID=11)'
    if units == 'degrees_east' or units == 'degree_east' or units == 'degree_E' or units == 'degrees_E' or units == 'degreeE' or units == 'degreesE':
        classInfo['空间参考系'] = 'WGS1984_度(ID=11)'

    if hasattr(variable_info, 'axis'):
        elements[variable_info.axis] = variable_info.size
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

    if var_name in nc.dimensions:
        # 保存数据值本身的真实范围
        variable_attrs["variable_range"] = [
            variable_values[0].item(), variable_values[-1].item()]
        # 保存数据的采样间隔，用于处理经纬度要向前延伸一步。如数据范围是[0~357.5],实际范围是[0~360]
        variable_attrs["variable_step"] = np.diff(variable_values).mean().item()
        if isinstance(variable_values, np.ndarray):
            variable_attrs["values"] = variable_values.tolist()
        elif isinstance(variable_values, np.generic):
            variable_attrs["values"] = variable_values.item()
    else:
        # 保存属性的最大最小值做为属性值的实际范围
        variable_attrs["variable_range"] = [
            variable_values.min().item(), variable_values.max().item()]
        variable_data = variable_values.flatten()
        filled_data = variable_data.filled(
            variable_info.getncattr('missing_value'))
        filename = f'{var_name}.bin'
        final_path = os.path.join(output_path, filename)
        # filename = f'0_0.m3d'

        filled_data.tofile(final_path)
        variable_attrs["values"] = filename
        varMetadata = {}
        varMetadata['名称'] = variable_info.name
        varMetadata['类型'] = precision_to_chinese(variable_attrs['datatype'])
        varMetadata['最小值'] = variable_attrs['actual_range'][0]
        varMetadata['最大值'] = variable_attrs['actual_range'][1]
        varInfo[var_name] = varMetadata

    variables[var_name] = variable_attrs

classInfo['体元个数'] = elements

metadata['类属性'] = classInfo
metadata['变量信息'] = varInfo
nowTime = datetime.now()
formatted_time = nowTime.strftime("%Y/%m/%d %H:%M:%S")
metadata['创建时间'] = formatted_time

data_dict['variables'] = variables
data_dict['metadata'] = metadata
file_path = os.path.join(output_path, f'{nc_path}.json')
nc.close()
# 保存到json
with open(file_path, 'w', encoding='utf-8') as fp:
    json.dump(data_dict, fp, ensure_ascii=False)

print('done')
