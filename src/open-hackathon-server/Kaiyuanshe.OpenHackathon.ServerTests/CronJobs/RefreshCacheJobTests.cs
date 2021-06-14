using Kaiyuanshe.OpenHackathon.Server.Cache;
using Kaiyuanshe.OpenHackathon.Server.CronJobs;
using Kaiyuanshe.OpenHackathon.Server.CronJobs.Jobs;
using Microsoft.Extensions.Logging;
using Moq;
using NUnit.Framework;
using System;
using System.Threading;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.ServerTests.CronJobs
{
    public class RefreshCacheJobTests
    {
        [Test]
        public async Task ExecuteAsync()
        {
            var jobContext = new CronJobContext
            {
                FireTime = DateTime.UtcNow,
            };

            var cacheProvider = new Mock<ICacheProvider>();
            cacheProvider.Setup(c => c.RefreshAllAsync(It.IsAny<CancellationToken>()));

            var job = new RefreshCacheJob
            {
                CacheProvider = cacheProvider.Object,
                LoggerFactory = LoggerFactory.Create((c) => { }),
            };
            await job.ExecuteNow(jobContext);

            Mock.VerifyAll(cacheProvider);
            cacheProvider.VerifyNoOtherCalls();
        }
    }
}
