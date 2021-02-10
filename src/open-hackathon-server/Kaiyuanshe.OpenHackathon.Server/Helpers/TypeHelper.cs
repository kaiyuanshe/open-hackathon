using Microsoft.WindowsAzure.Storage.Table;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server
{
    public static class TypeHelper
    {
        public static TDestination As<TDestination>(this object src, Action<TDestination> configure = null)
            where TDestination : new()
        {
            if (src == null)
            {
                throw new ArgumentNullException("Unable to convert null.");
            }

            TDestination resp = new TDestination();
            var srcProperties = src.GetType().GetProperties();
            foreach (var property in typeof(TDestination).GetProperties())
            {
                var srcProp = srcProperties.FirstOrDefault(p => string.Equals(p.Name, property.Name, StringComparison.OrdinalIgnoreCase));
                if (srcProp != null)
                {
                    var srcValue = srcProp.GetValue(src);
                    property.SetValue(resp, srcValue);
                }
            }
            if (configure != null)
            {
                configure(resp);
            }

            return resp;
        }

        public static DynamicTableEntity ToTableEntity(this object model, string partitionKey, string rowKey, Action<DynamicTableEntity> configure = null)
        {
            DynamicTableEntity tableEntity = new DynamicTableEntity(partitionKey, rowKey);

            foreach (var property in model.GetType().GetProperties())
            {
                var srcValue = property.GetValue(model);
                if (srcValue == null)
                    continue;

                if (property.PropertyType == typeof(string))
                {
                    tableEntity.Properties.Add(property.Name, new EntityProperty(srcValue.ToString()));
                }
                else if (property.PropertyType == typeof(int))
                {
                    tableEntity.Properties.Add(property.Name, new EntityProperty((int)srcValue));
                }
                else if (property.PropertyType == typeof(bool))
                {
                    tableEntity.Properties.Add(property.Name, new EntityProperty((bool)srcValue));
                }
                else if (property.PropertyType == typeof(DateTime))
                {
                    tableEntity.Properties.Add(property.Name, new EntityProperty((DateTime)srcValue));
                }
                else if (property.PropertyType == typeof(long))
                {
                    tableEntity.Properties.Add(property.Name, new EntityProperty((long)srcValue));
                }
                else if (property.PropertyType == typeof(double))
                {
                    tableEntity.Properties.Add(property.Name, new EntityProperty((double)srcValue));
                }
                else if (property.PropertyType == typeof(Guid))
                {
                    tableEntity.Properties.Add(property.Name, new EntityProperty((Guid)srcValue));
                }
                else if (property.PropertyType.IsEnum)
                {
                    tableEntity.Properties.Add(property.Name, new EntityProperty((int)srcValue));
                }
                else
                {
                    tableEntity.Properties.Add(property.Name, new EntityProperty(JsonConvert.SerializeObject(srcValue)));
                }
            }

            if (configure != null)
            {
                configure(tableEntity);
            }

            return tableEntity;
        }

        public static TModel ToModel<TModel>(this DynamicTableEntity tableEntity, TModel model, Action<TModel> configure = null)
        {
            foreach (var property in model.GetType().GetProperties())
            {
                if (!tableEntity.Properties.ContainsKey(property.Name))
                    continue;

                if (property.PropertyType == typeof(string))
                {
                    try
                    {
                        property.SetValue(model, tableEntity.Properties[property.Name].StringValue);
                    }
                    catch
                    {
                    }
                }
                else if (property.PropertyType == typeof(int))
                {
                    try
                    {
                        property.SetValue(model, tableEntity.Properties[property.Name].Int32Value);
                    }
                    catch
                    {
                    }
                }
                else if (property.PropertyType == typeof(bool))
                {
                    try
                    {
                        property.SetValue(model, tableEntity.Properties[property.Name].BooleanValue);
                    }
                    catch
                    {
                    }
                }
                else if (property.PropertyType == typeof(DateTime))
                {
                    try
                    {
                        property.SetValue(model, tableEntity.Properties[property.Name].DateTime);
                    }
                    catch
                    {
                    }
                }
                else if (property.PropertyType == typeof(long))
                {
                    try
                    {
                        property.SetValue(model, tableEntity.Properties[property.Name].Int64Value);
                    }
                    catch
                    {
                    }
                }
                else if (property.PropertyType == typeof(double))
                {
                    try
                    {
                        property.SetValue(model, tableEntity.Properties[property.Name].DoubleValue);
                    }
                    catch
                    {
                    }
                }
                else if (property.PropertyType == typeof(Guid))
                {
                    try
                    {
                        property.SetValue(model, tableEntity.Properties[property.Name].GuidValue);
                    }
                    catch
                    {
                    }
                }
                else if (property.PropertyType.IsEnum)
                {
                    try
                    {
                        property.SetValue(model, tableEntity.Properties[property.Name].Int32Value);
                    }
                    catch
                    {
                    }
                }
                else
                {
                    try
                    {
                        var str = tableEntity.Properties[property.Name].StringValue;
                        property.SetValue(model, JsonConvert.DeserializeObject(str, property.PropertyType));
                    }
                    catch
                    {
                    }
                }
            }

            if (configure != null)
            {
                configure(model);
            }

            return model;
        }
    }
}
