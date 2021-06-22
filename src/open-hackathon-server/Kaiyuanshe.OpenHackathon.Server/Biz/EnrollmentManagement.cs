using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.Storage;
using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using Microsoft.Extensions.Logging;
using Microsoft.WindowsAzure.Storage.Table;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.Biz
{
    public interface IEnrollmentManagement
    {
        /// <summary>
        /// Register a hackathon event as contestant
        /// </summary>
        Task<EnrollmentEntity> EnrollAsync(HackathonEntity hackathon, string userId, CancellationToken cancellationToken = default);

        /// <summary>
        /// Update status of enrollment.
        /// </summary>
        Task<EnrollmentEntity> UpdateEnrollmentStatusAsync(HackathonEntity hackathon, EnrollmentEntity participant, EnrollmentStatus status, CancellationToken cancellationToken = default);

        /// <summary>
        /// List paged enrollments of hackathon
        /// </summary>
        /// <param name="hackathonName">name of hackathon</param>
        /// <param name="options">options for query</param>
        /// <param name="cancellationToken"></param>
        /// <returns></returns>
        Task<TableQuerySegment<EnrollmentEntity>> ListPaginatedEnrollmentsAsync(string hackathonName, EnrollmentQueryOptions options, CancellationToken cancellationToken = default);

        /// <summary>
        /// Get an enrollment.
        /// </summary>
        Task<EnrollmentEntity> GetEnrollmentAsync(string hackathonName, string userId, CancellationToken cancellationToken = default);
    }

    public class EnrollmentManagement : ManagementClientBase, IEnrollmentManagement
    {
        private readonly ILogger logger;

        public EnrollmentManagement(ILogger<EnrollmentManagement> logger)
        {
            this.logger = logger;
        }

        #region EnrollAsync
        public async Task<EnrollmentEntity> EnrollAsync(HackathonEntity hackathon, string userId, CancellationToken cancellationToken)
        {
            string hackathonName = hackathon.Name;
            var entity = await StorageContext.EnrollmentTable.RetrieveAsync(hackathonName, userId, cancellationToken);

            if (entity != null)
            {
                logger.TraceInformation($"Enroll skipped, user with id {userId} alreday enrolled in hackathon {hackathonName}");
                return entity;
            }
            else
            {
                entity = new EnrollmentEntity
                {
                    PartitionKey = hackathonName,
                    RowKey = userId,
                    Status = EnrollmentStatus.pendingApproval,
                    CreatedAt = DateTime.UtcNow,
                };
                if (hackathon.AutoApprove)
                {
                    entity.Status = EnrollmentStatus.approved;
                }
                await StorageContext.EnrollmentTable.InsertAsync(entity, cancellationToken);
            }
            logger.TraceInformation($"user {userId} enrolled in hackathon {hackathon}, status: {entity.Status.ToString()}");

            if (entity.Status == EnrollmentStatus.approved)
            {
                hackathon.Enrollment += 1;
                await StorageContext.HackathonTable.MergeAsync(hackathon, cancellationToken);
            }

            return entity;
        }
        #endregion

        #region UpdateEnrollmentStatusAsync
        public async Task<EnrollmentEntity> UpdateEnrollmentStatusAsync(HackathonEntity hackathon, EnrollmentEntity enrollment, EnrollmentStatus status, CancellationToken cancellationToken = default)
        {
            if (enrollment == null || hackathon == null)
                return enrollment;

            if (enrollment.Status == status)
                return enrollment;

            // update hackathon.enrollment
            int enrollmentIncreasement = 0;
            if (status == EnrollmentStatus.approved)
            {
                enrollmentIncreasement += 1;
            }
            if (enrollment.Status == EnrollmentStatus.approved && hackathon.Enrollment >= 1)
            {
                enrollmentIncreasement -= 1;
            }

            enrollment.Status = status;
            await StorageContext.EnrollmentTable.MergeAsync(enrollment, cancellationToken);
            if (enrollmentIncreasement != 0)
            {
                hackathon.Enrollment += enrollmentIncreasement;
                await StorageContext.HackathonTable.MergeAsync(hackathon, cancellationToken);
            }
            logger.TraceInformation($"Pariticipant {enrollment.HackathonName}/{enrollment.UserId} stastus updated to: {status} ");

            return enrollment;
        }
        #endregion

        #region ListPaginatedEnrollmentsAsync
        public async Task<TableQuerySegment<EnrollmentEntity>> ListPaginatedEnrollmentsAsync(string hackathonName, EnrollmentQueryOptions options, CancellationToken cancellationToken = default)
        {
            var filter = TableQuery.GenerateFilterCondition(
                           nameof(EnrollmentEntity.PartitionKey),
                           QueryComparisons.Equal,
                           hackathonName);

            if (options != null && options.Status.HasValue)
            {
                var statusFilter = TableQuery.GenerateFilterConditionForInt(
                    nameof(EnrollmentEntity.Status),
                    QueryComparisons.Equal,
                    (int)options.Status.Value);
                filter = TableQueryHelper.And(filter, statusFilter);
            }

            int top = 100;
            if (options != null && options.Top.HasValue && options.Top.Value > 0)
            {
                top = options.Top.Value;
            }
            TableQuery<EnrollmentEntity> query = new TableQuery<EnrollmentEntity>()
                .Where(filter)
                .Take(top);

            TableContinuationToken continuationToken = options?.TableContinuationToken;
            return await StorageContext.EnrollmentTable.ExecuteQuerySegmentedAsync(query, continuationToken, cancellationToken);
        }
        #endregion

        #region GetEnrollmentAsync
        public virtual async Task<EnrollmentEntity> GetEnrollmentAsync(string hackathonName, string userId, CancellationToken cancellationToken = default)
        {
            if (hackathonName == null || userId == null)
                return null;
            return await StorageContext.EnrollmentTable.RetrieveAsync(hackathonName.ToLower(), userId.ToLower(), cancellationToken);
        } 
        #endregion
    }
}
