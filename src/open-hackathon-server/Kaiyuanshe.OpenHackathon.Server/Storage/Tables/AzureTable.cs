using Microsoft.WindowsAzure.Storage;
using Microsoft.WindowsAzure.Storage.Table;
using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Storage.Tables
{
    public interface IAzureTable<TEntity> where TEntity : ITableEntity, new()
    {
        Task<TableResult> InsertAsync(TEntity entity, CancellationToken cancellationToken = default);

        Task<TableResult> MergeAsync(TEntity entity, CancellationToken cancellationToken = default);

        Task<TableResult> InsertOrMergeAsync(TEntity entity, CancellationToken cancellationToken = default);

        Task<TableResult> RetrieveAndMergeAsync(string partitionKey, string rowKey, Action<TEntity> func, CancellationToken cancellationToken = default);

        Task<TableResult> InsertOrReplaceAsync(TEntity entity, CancellationToken cancellationToken = default);

        Task<TableResult> ReplaceAsync(TEntity entity, CancellationToken cancellationToken = default);

        Task<TableResult> DeleteAsync(string partitionKey, string rowKey, CancellationToken cancellationToken = default);

        Task<TEntity> RetrieveAsync(string partitionKey, string rowKey, CancellationToken cancellationToken = default);

        Task<IEnumerable<TEntity>> ExecuteQueryAsync(
            TableQuery<TEntity> query, CancellationToken cancellationToken = default);

        Task<TableQuerySegment<TEntity>> ExecuteQuerySegmentedAsync(
            TableQuery<TEntity> query, TableContinuationToken continuationToken, CancellationToken cancellationToken = default);

        Task ExecuteQuerySegmentedAsync(TableQuery<TEntity> query,
            Action<TableQuerySegment<TEntity>> action,
            CancellationToken cancellationToken = default);

        Task ExecuteQuerySegmentedAsync(TableQuery<TEntity> query,
            Func<TableQuerySegment<TEntity>, Task> asyncAction,
            CancellationToken cancellationToken = default);
    }

    /// <summary>
    /// Type that abstract operation aganist windows azure storage tables in a given storage account.
    /// </summary>
    public class AzureTable<TEntity> : IAzureTable<TEntity> where TEntity : ITableEntity, new()
    {
        #region Constants
        /// <summary>
        /// The retry interval between for table storage retry operations
        /// </summary>
        static readonly int TableStorageRetryInterval = 5;

        /// <summary>
        /// The retry count for table storage operations
        /// </summary>
        static readonly int TableStorageRetryCount = 5;
        #endregion

        /// <summary>
        /// client to make request aganist azure table storage.
        /// </summary>
        protected readonly CloudTableClient tableServiceProxy;

        /// <summary>
        ///  The name of the storage table exists under the storage account with which this AzureTable is configured.
        /// </summary>
        protected readonly string tableName;

        /// <summary>
        /// Test-only constructor
        /// </summary>
        protected AzureTable()
        { }

        protected AzureTable(CloudStorageAccount storageAccount, string tableName)
        {
            this.tableName = tableName;
            tableServiceProxy = storageAccount.CreateCloudTableClient();
            tableServiceProxy.DefaultRequestOptions.RetryPolicy = new Microsoft.WindowsAzure.Storage.RetryPolicies.LinearRetry(
                TimeSpan.FromSeconds(TableStorageRetryInterval), TableStorageRetryCount);

            // create new table if not exists.
            CloudTable cloudTable = tableServiceProxy.GetTableReference(tableName);
            cloudTable.CreateIfNotExistsAsync().Wait();
        }

        protected CloudTable UnderlyingCloudTable => tableServiceProxy.GetTableReference(tableName);

        /// <summary>
        /// Asynchronously add an entity to the given table.
        /// </summary>
        /// <param name="entity">The entity to add.</param>
        public virtual async Task<TableResult> InsertAsync(TEntity entity, CancellationToken cancellationToken = default)
        {
            TableOperation insertOperation = TableOperation.Insert(entity);
            return await ExecuteAsync(insertOperation, cancellationToken);
        }

        /// <summary>
        /// Asynchronously replaces an entity in the given table.
        /// </summary>
        /// <param name="entity">The entity to update.</param>
        public virtual async Task<TableResult> MergeAsync(TEntity entity, CancellationToken cancellationToken = default)
        {
            TableOperation mergeOperation = TableOperation.Merge(entity);
            return await ExecuteAsync(mergeOperation, cancellationToken);
        }

        /// <summary>
        /// Inserts the given entity into a table if the entity does not exist;
        /// if the entity does exist then its contents are merged with the provided entity.
        /// </summary>
        /// <param name="entity">The entity to update.</param>
        public virtual async Task<TableResult> InsertOrMergeAsync(TEntity entity, CancellationToken cancellationToken = default)
        {
            TableOperation mergeOperation = TableOperation.InsertOrMerge(entity);
            return await ExecuteAsync(mergeOperation, cancellationToken);
        }

        /// <summary>
        /// Asynchronously retrieve, apply changes and replace an entity in the given table.
        /// </summary>
        /// <param name="func">Callback function to apply changes</param>
        public virtual async Task<TableResult> RetrieveAndMergeAsync(string partitionKey, string rowKey, Action<TEntity> func, CancellationToken cancellationToken = default)
        {
            var entity = await RetrieveAsync(partitionKey, rowKey, cancellationToken);
            func(entity);
            return await MergeAsync(entity, cancellationToken);
        }

        /// <summary>
        /// Asynchronously replaces an existing entity, or insert a new entity in the given table.
        /// </summary>
        /// <param name="entity">The entity to update.</param>
        public virtual async Task<TableResult> InsertOrReplaceAsync(TEntity entity, CancellationToken cancellationToken = default)
        {
            TableOperation insertOrReplaceOperation = TableOperation.InsertOrReplace(entity);
            return await ExecuteAsync(insertOrReplaceOperation, cancellationToken);
        }

        /// <summary>
        /// Asynchronously replace an existing entity in the given table.
        /// </summary>
        /// <param name="entity">The entity to replace.</param>
        public virtual async Task<TableResult> ReplaceAsync(TEntity entity, CancellationToken cancellationToken = default)
        {
            TableOperation update = TableOperation.Replace(entity);
            return await ExecuteAsync(update, cancellationToken);
        }

        /// <summary>
        /// Asynchronously delete an entity identified by the given keys from the given table.
        /// </summary>
        /// <param name="partitionKey">The partitionkey.</param>
        /// <param name="rowKey">The row.</param>
        public virtual async Task<TableResult> DeleteAsync(string partitionKey, string rowKey, CancellationToken cancellationToken = default)
        {
            TableOperation deleteOperation = TableOperation.Delete(new TableEntity(partitionKey, rowKey) { ETag = "*" });
            return await ExecuteAsync(deleteOperation, cancellationToken);
        }

        /// <summary>
        /// Get an entity of type TEntity identifed by the given row and partition key from the given table.
        /// </summary>
        /// <param name="partitionKey">The partition key.</param>
        /// <param name="rowKey">The row key.</param>
        /// <returns>The entity retrieved or null if it doesn't exist.</returns>
        public virtual async Task<TEntity> RetrieveAsync(string partitionKey, string rowKey, CancellationToken cancellationToken = default)
        {
            TableOperation retrieveOperation = TableOperation.Retrieve<TEntity>(partitionKey, rowKey);
            TableResult retrieveResult = await ExecuteAsync(retrieveOperation, cancellationToken);
            return (TEntity)retrieveResult.Result;
        }

        public virtual async Task<IEnumerable<TEntity>> ExecuteQueryAsync(
            TableQuery<TEntity> query, CancellationToken cancellationToken = default)
        {
            List<TEntity> list = new List<TEntity>();
            await ExecuteQuerySegmentedAsync(query, (segment) =>
            {
                list.AddRange(segment);
            }, cancellationToken);

            return list;
        }

        /// <summary>
        /// Initiates an asynchronous operation to query a table in segmented mode.
        /// </summary>
        /// <param name="query">
        ///     A Microsoft.WindowsAzure.Storage.Table.TableQuery instance specifying the table
        ///     to query and the query parameters to use, specialized for a type TElement.</param>
        /// <param name="continuationToken">
        ///     A Microsoft.WindowsAzure.Storage.Table.TableContinuationToken object representing
        ///     a continuation token from the server when the operation returns a partial result.</param>
        /// <param name="cancellationToken"></param>
        /// <returns></returns>
        public virtual async Task<TableQuerySegment<TEntity>> ExecuteQuerySegmentedAsync(
            TableQuery<TEntity> query, TableContinuationToken continuationToken, CancellationToken cancellationToken = default)
        {
            query = query ?? new TableQuery<TEntity>();
            return await UnderlyingCloudTable.ExecuteQuerySegmentedAsync(query, continuationToken, null, null, cancellationToken);
        }

        /// <summary>
        /// Initiates an asynchronous operation with a callback to query a table in segmented mode.
        /// </summary>
        /// <param name="query">
        ///     A Microsoft.WindowsAzure.Storage.Table.TableQuery instance specifying the table
        ///     to query and the query parameters to use, specialized for a type TElement.</param>
        /// <param name="action">
        ///     The callback which gets called for every segment.</param>
        /// <param name="cancellationToken"></param>
        /// <returns></returns>
        public virtual async Task ExecuteQuerySegmentedAsync(TableQuery<TEntity> query,
            Action<TableQuerySegment<TEntity>> action,
            CancellationToken cancellationToken = default)
        {
            CloudTable table = UnderlyingCloudTable;
            TableContinuationToken continuationToken = null;
            query = query ?? new TableQuery<TEntity>();
            do
            {
                var queryResult = await table.ExecuteQuerySegmentedAsync(query, continuationToken, null, null, cancellationToken);
                action?.Invoke(queryResult);
                continuationToken = queryResult.ContinuationToken;
            } while (continuationToken != null);
        }

        public virtual async Task ExecuteQuerySegmentedAsync(TableQuery<TEntity> query,
            Func<TableQuerySegment<TEntity>, Task> asyncAction,
            CancellationToken cancellationToken = default)
        {
            CloudTable table = UnderlyingCloudTable;
            TableContinuationToken continuationToken = null;
            query = query ?? new TableQuery<TEntity>();
            do
            {
                var queryResult = await table.ExecuteQuerySegmentedAsync(query, continuationToken, null, null, cancellationToken);
                cancellationToken.ThrowIfCancellationRequested();
                if (asyncAction != null)
                {
                    await asyncAction.Invoke(queryResult);
                }
                continuationToken = queryResult.ContinuationToken;
            } while (continuationToken != null);
        }

        private async Task<TableResult> ExecuteAsync(TableOperation operation, CancellationToken cancellationToken = default)
        {
            return await UnderlyingCloudTable.ExecuteAsync(operation, null, null, cancellationToken);
        }
    }
}
