using Microsoft.WindowsAzure.Storage.Table;
using System;
using System.Collections.Generic;

namespace Kaiyuanshe.OpenHackathon.ServerTests
{
    public static class MockHelper
    {
        public static TableQuerySegment<T> CreateTableQuerySegment<T>(IList<T> result, TableContinuationToken continuationToken)
        {
            // Have to use reflection to construct TableQuerySegment as its contructor is internal
            var type = typeof(TableQuerySegment<T>);
            var querySegmentCtor = type.GetConstructor(
                System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance, null,
                new Type[] { typeof(List<T>) }, null);
            var querySegment = (TableQuerySegment<T>)querySegmentCtor.Invoke(new object[] { result });

            type.GetProperty("ContinuationToken").SetValue(querySegment, continuationToken);

            return querySegment;
        }
    }
}
