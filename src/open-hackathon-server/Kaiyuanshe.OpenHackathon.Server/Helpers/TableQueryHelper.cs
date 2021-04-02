using Microsoft.WindowsAzure.Storage.Table;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Helpers
{
    public static class TableQueryHelper
    {
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
