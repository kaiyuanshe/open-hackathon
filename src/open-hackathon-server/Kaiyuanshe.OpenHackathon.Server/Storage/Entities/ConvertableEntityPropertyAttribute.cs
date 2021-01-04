using Newtonsoft.Json;
using System;

namespace Kaiyuanshe.OpenHackathon.Server.Storage.Entities
{
    /// <summary>
    /// An Attribute to enable us write complex objects into Azure table
    /// </summary>
    [AttributeUsage(AttributeTargets.Property, AllowMultiple = false, Inherited = true)]
    public class ConvertableEntityPropertyAttribute : Attribute
    {
        public Type ConvertToType { get; private set; }

        public ConvertableEntityPropertyAttribute()
        {

        }
        public ConvertableEntityPropertyAttribute(Type convertToType)
        {
            ConvertToType = convertToType;
        }

        public virtual string Serialize(object value)
        {
            return JsonConvert.SerializeObject(value);
        }

        public virtual object Deserialize(string value, Type resultType)
        {
            return JsonConvert.DeserializeObject(value, resultType);
        }
    }
}
