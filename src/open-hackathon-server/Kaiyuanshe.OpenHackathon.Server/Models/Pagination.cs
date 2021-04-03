using Microsoft.WindowsAzure.Storage.Table;
using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Models
{
    /// <summary>
    /// Pagination parameters. Usually only `top` needed for the initial request 
    /// where a response with a `nextLink` will be returned. The `nextLink` has all 
    /// pagination parameters included, clients just request the `nextLink` without any
    /// modification to get more results.
    /// </summary>
    public class Pagination
    {
        /// <summary>
        /// conbined with "nr" to query more results. Used by server-side paging only. Don't set it manually.
        /// </summary>
        [MaxLength(200)]
        public string np { get; set; }

        /// <summary>
        /// conbined with "np"t o query more results. Used by server-side paging only. Don't set it manually.
        /// </summary>
        [MaxLength(128)]
        public string nr { get; set; }

        /// <summary>
        /// Return only the top N records. any integer beween 1-1000. 100 by default. 
        /// </summary>
        /// <example>20</example>
        [Range(1, 1000)]
        public int? top { get; set; }

        public TableContinuationToken ToContinuationToken(string tableName, string partitionKey = null)
        {
            // nr in nextLink shouldn't be null or empty.
            // But pk might be empty if it's implicitly set on server side via "partitionKey" parameter.
            if (string.IsNullOrWhiteSpace(nr))
            {
                return null;
            }

            return new TableContinuationToken
            {
                // partitionKey takes precedence over np from parameter.
                NextPartitionKey = partitionKey ?? np ?? string.Empty,
                NextRowKey = nr,
                NextTableName = tableName,
            };
        }
    }
}
