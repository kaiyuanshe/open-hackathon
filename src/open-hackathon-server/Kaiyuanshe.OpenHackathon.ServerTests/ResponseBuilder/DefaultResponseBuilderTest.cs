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

            var roles = new HackathonRoles
            {
                isAdmin = true,
                isEnrolled = true,
                isJudge = true,
            };

            var builder = new DefaultResponseBuilder();
            var hack = builder.BuildHackathon(entity, roles);

            Assert.IsNull(hack.tags);
            Assert.AreEqual("pk", hack.name);
            Assert.IsTrue(hack.autoApprove.Value);
            Assert.AreEqual("loc", hack.location);
            Assert.AreEqual("abc", hack.creatorId);
            Assert.IsTrue(hack.judgeStartedAt.HasValue);
            Assert.IsFalse(hack.judgeEndedAt.HasValue);
            Assert.IsTrue(hack.roles.isAdmin);
            Assert.IsTrue(hack.roles.isEnrolled);
            Assert.IsTrue(hack.roles.isJudge);
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
                Status = EnrollmentStatus.approved,
                CreatedAt = DateTime.Now,
                Timestamp = DateTime.Now,
            };

            var respBuilder = new DefaultResponseBuilder();
            var enrollment = respBuilder.BuildEnrollment(participant);

            Assert.AreEqual("hack", enrollment.hackathonName);
            Assert.AreEqual("uid", enrollment.userId);
            Assert.AreEqual(EnrollmentStatus.approved, enrollment.status);
            Assert.AreEqual(participant.CreatedAt, enrollment.createdAt);
            Assert.AreEqual(participant.Timestamp.DateTime, enrollment.updatedAt);
        }

        [Test]
        public void BuildTeamTest()
        {
            var entity = new TeamEntity
            {
                PartitionKey = "pk",
                RowKey = "rk",
                AutoApprove = false,
                CreatorId = "uid",
                Description = "desc",
                DisplayName = "dp",
                CreatedAt = DateTime.Now,
                Timestamp = DateTime.Now
            };

            var respBuilder = new DefaultResponseBuilder();
            var team = respBuilder.BuildTeam(entity);

            Assert.AreEqual("pk", team.hackathonName);
            Assert.AreEqual("rk", team.id);
            Assert.AreEqual(false, team.autoApprove.Value);
            Assert.AreEqual("uid", team.creatorId);
            Assert.AreEqual("desc", team.description);
            Assert.AreEqual("dp", team.displayName);
            Assert.AreEqual(entity.CreatedAt, team.createdAt);
            Assert.AreEqual(entity.Timestamp.DateTime, team.updatedAt);
        }

        [Test]
        public void BuildTeamMemberTest()
        {
            var entity = new TeamMemberEntity
            {
                PartitionKey = "pk",
                RowKey = "rk",
                HackathonName = "hack",
                Description = "desc",
                Role = TeamMemberRole.Admin,
                Status = TeamMemberStatus.pendingApproval,
                CreatedAt = DateTime.Now,
                Timestamp = DateTime.Now
            };

            var respBuilder = new DefaultResponseBuilder();
            var teamMember = respBuilder.BuildTeamMember(entity);

            Assert.AreEqual("hack", teamMember.hackathonName);
            Assert.AreEqual("pk", teamMember.teamId);
            Assert.AreEqual("rk", teamMember.userId);
            Assert.AreEqual("desc", teamMember.description);
            Assert.AreEqual(TeamMemberRole.Admin, teamMember.role);
            Assert.AreEqual(TeamMemberStatus.pendingApproval, teamMember.status);
            Assert.AreEqual(entity.CreatedAt, teamMember.createdAt);
            Assert.AreEqual(entity.Timestamp.DateTime, teamMember.updatedAt);
        }

        [Test]
        public void BuildResourceListTest()
        {
            string nextLink = "nextlink";
            List<EnrollmentEntity> enrollments = new List<EnrollmentEntity>
            {
                new EnrollmentEntity
                {
                    PartitionKey = "pk1",
                    RowKey = "rk1",
                    Status = EnrollmentStatus.approved,
                },
                new EnrollmentEntity
                {
                    PartitionKey = "pk2",
                    RowKey = "rk2",
                    Status = EnrollmentStatus.rejected,
                }
            };

            var builder = new DefaultResponseBuilder();
            var result = builder.BuildResourceList<EnrollmentEntity, Enrollment, EnrollmentList>(
                    enrollments,
                    builder.BuildEnrollment,
                    nextLink);

            Assert.AreEqual("nextlink", result.nextLink);
            Assert.AreEqual(2, result.value.Length);
            Assert.AreEqual("pk1", result.value[0].hackathonName);
            Assert.AreEqual("rk1", result.value[0].userId);
            Assert.AreEqual(EnrollmentStatus.approved, result.value[0].status);
            Assert.AreEqual("pk2", result.value[1].hackathonName);
            Assert.AreEqual("rk2", result.value[1].userId);
            Assert.AreEqual(EnrollmentStatus.rejected, result.value[1].status);

        }
    }
}
