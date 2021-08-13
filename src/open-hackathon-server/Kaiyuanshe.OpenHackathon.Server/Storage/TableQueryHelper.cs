using Microsoft.WindowsAzure.Storage.Table;

namespace Kaiyuanshe.OpenHackathon.Server.Storage
{
    public static class TableQueryHelper
    {
        public static string PartitionKeyFilter(string partitionKey)
        {
            return TableQuery.GenerateFilterCondition(nameof(TableEntity.PartitionKey), QueryComparisons.Equal, partitionKey);
        }

        public static string And(params string[] filters)
        {
            if (filters == null || filters.Length == 0)
            {
                return string.Empty;
            }

            if (filters.Length == 1)
                return filters[0];

            string combined = filters[0];
            for (int i = 1; i < filters.Length; i++)
            {
                if (!string.IsNullOrEmpty(filters[i]))
                {
                    combined = TableQuery.CombineFilters(combined, TableOperators.And, filters[i]);
                }
            }
            return combined;
        }
    }
}
