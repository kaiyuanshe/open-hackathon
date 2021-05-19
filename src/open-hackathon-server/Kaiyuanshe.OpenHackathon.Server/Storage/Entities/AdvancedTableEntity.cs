using Microsoft.WindowsAzure.Storage;
using Microsoft.WindowsAzure.Storage.Table;
using System;
using System.Collections.Generic;

namespace Kaiyuanshe.OpenHackathon.Server.Storage.Entities
{
    public abstract class AdvancedTableEntity : TableEntity
    {
        public AdvancedTableEntity() : base() { }
        public AdvancedTableEntity(string partitionKey, string rowKey) : base(partitionKey, rowKey) { }

        /// <summary>
        /// datetime when the entity is created
        /// </summary>
        public DateTime CreatedAt { get; set; }

        public override IDictionary<string, EntityProperty> WriteEntity(OperationContext operationContext)
        {
            var results = base.WriteEntity(operationContext);
            EntityPropertyConverter.Serialize(this, results);
            return results;
        }

        public override void ReadEntity(IDictionary<string, EntityProperty> properties, OperationContext operationContext)
        {
            base.ReadEntity(properties, operationContext);
            EntityPropertyConverter.DeSerialize(this, properties);
        }
    }
}
