using Microsoft.WindowsAzure.Storage.Table;
using System;
using System.Collections.Generic;

namespace Kaiyuanshe.OpenHackathon.Server.Storage.Entities
{
    public static class EntityPropertyConverter
    {
        public static void Serialize<TEntity>(TEntity entity, IDictionary<string, EntityProperty> results)
        {
            foreach (var property in entity.GetType().GetProperties())
            {
                // Skip ignored property
                var ignoreAttribute = (IgnorePropertyAttribute)Attribute.GetCustomAttribute(property, typeof(IgnorePropertyAttribute));
                if (ignoreAttribute != null)
                {
                    continue;
                }

                var convertableAttribute = (ConvertableEntityPropertyAttribute)Attribute.GetCustomAttribute(property, typeof(ConvertableEntityPropertyAttribute));
                if (convertableAttribute != null)
                {
                    var propertyValue = entity.GetType().GetProperty(property.Name)?.GetValue(entity);
                    results.Add(property.Name, new EntityProperty(convertableAttribute.Serialize(propertyValue)));
                }

                if (property.PropertyType.IsEnum)
                {
                    results.Add(property.Name, new EntityProperty((int)property.GetValue(entity)));
                }
            }
        }

        public static void DeSerialize<TEntity>(TEntity entity, IDictionary<string, EntityProperty> properties)
        {
            foreach (var property in entity.GetType().GetProperties())
            {
                // Skip ignored property
                var ignoreAttribute = (IgnorePropertyAttribute)Attribute.GetCustomAttribute(property, typeof(IgnorePropertyAttribute));
                if (ignoreAttribute != null)
                {
                    continue;
                }

                // Convertable property
                var convertableAttribute = (ConvertableEntityPropertyAttribute)Attribute.GetCustomAttribute(property, typeof(ConvertableEntityPropertyAttribute));
                if (convertableAttribute != null && properties.ContainsKey(property.Name))
                {
                    Type resultType = property.PropertyType;
                    if (convertableAttribute.ConvertToType != null)
                    {
                        resultType = convertableAttribute.ConvertToType;
                    }

                    var objectValue = convertableAttribute.Deserialize(properties[property.Name].StringValue, resultType);
                    // Set property only when deserialized value is not null,
                    // otherwise leave it to be the default value as constructed
                    if (objectValue != null)
                    {
                        entity.GetType().GetProperty(property.Name)?.SetValue(entity, objectValue);
                    }
                }

                // Enum property
                if (property.PropertyType.IsEnum)
                {
                    if (properties.TryGetValue(property.Name, out EntityProperty value))
                    {
                        property.SetValue(entity, Enum.ToObject(property.PropertyType, value.Int32Value));
                    }
                }
            }
        }
    }
}
