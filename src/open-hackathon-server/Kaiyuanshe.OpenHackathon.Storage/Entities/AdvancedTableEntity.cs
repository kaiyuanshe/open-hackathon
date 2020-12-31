﻿using Microsoft.WindowsAzure.Storage;
using Microsoft.WindowsAzure.Storage.Table;
using System.Collections.Generic;

namespace Kaiyuanshe.OpenHackathon.Storage.Entities
{
    public abstract class AdvancedTableEntity : TableEntity
    {
        public AdvancedTableEntity() : base() { }
        public AdvancedTableEntity(string partitionKey, string rowKey) : base(partitionKey, rowKey) { }

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
