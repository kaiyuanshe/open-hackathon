using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.ResponseBuilder;
using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using NUnit.Framework;
using System;
using System.Collections.Generic;

namespace Kaiyuanshe.OpenHackathon.ServerTests.ResponseBuilder
{
    [TestFixture]
    public class DefaultResponseBuilderTest
    {
        [Test]
        public void BuildHackathonTest()
        {
            var entity = new HackathonEntity
            {
                PartitionKey = "pk",
                AutoApprove = true,
                CreatorId = "abc",
                Location = "loc",
                JudgeStartedAt = DateTime.UtcNow,
                Status = HackathonStatus.online,
            };

            var builder = new DefaultResponseBuilder();
            var hack = builder.BuildHackathon(entity);

            Assert.IsNull(hack.tags);
            Assert.AreEqual("pk", hack.name);
            Assert.IsTrue(hack.autoApprove.Value);
            Assert.AreEqual("loc", hack.location);
            Assert.AreEqual("abc", hack.creatorId);
            Assert.IsTrue(hack.judgeStartedAt.HasValue);
            Assert.IsFalse(hack.judgeEndedAt.HasValue);
        }

        [Test]
        public void BuildHackathonListTest()
        {
            int count = 10;
            var list = new List<HackathonEntity>();
            for (int i = 0; i < count; i++)
            {
                list.Add(new HackathonEntity { PartitionKey = i.ToString() });
            }

            var builder = new DefaultResponseBuilder();
            var hacklist = builder.BuildHackathonList(list);

            Assert.IsNotNull(hacklist);
            Assert.AreEqual(count, hacklist.values.Length);
            for (int i = 0; i < count; i++)
            {
                Assert.AreEqual(i.ToString(), hacklist.values[i].name);
            }
        }

        [Test]
        public void BuildEnrollmentTest()
        {
            EnrollmentEntity participant = new EnrollmentEntity
            {
                PartitionKey = "hack",
                RowKey = "uid",
                Status = Server.Models.EnrollmentStatus.approved,
                CreatedAt = DateTime.Now,
                Timestamp = DateTime.Now,
            };

            var respBuilder = new DefaultResponseBuilder();
            var enrollment = respBuilder.BuildEnrollment(participant);

            Assert.AreEqual("hack", enrollment.hackathonName);
            Assert.AreEqual("uid", enrollment.userId);
            Assert.AreEqual(Server.Models.EnrollmentStatus.approved, enrollment.status);
            Assert.AreEqual(participant.CreatedAt, enrollment.createdAt);
            Assert.AreEqual(participant.Timestamp.DateTime, enrollment.updatedAt);
        }
    }
}
