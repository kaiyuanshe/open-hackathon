using Kaiyuanshe.OpenHackathon.Server.ResponseBuilder;
using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using NUnit.Framework;
using System;
using System.Collections.Generic;
using System.Text;

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
                JudgeStartTime = DateTime.UtcNow,
                Status = Server.Models.Enums.HackathonStatus.Online,
            };

            var builder = new DefaultResponseBuilder();
            var hack = builder.BuildHackathon(entity);

            Assert.IsNull(hack.Tags);
            Assert.AreEqual("pk", hack.Name);
            Assert.IsTrue(hack.AutoApprove);
            Assert.AreEqual("loc", hack.Location);
            Assert.AreEqual("abc", hack.CreatorId);
            Assert.IsTrue(hack.JudgeStartTime.HasValue);
            Assert.IsFalse(hack.JudgeEndTime.HasValue);
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
                Assert.AreEqual(i.ToString(), hacklist.values[i].Name);
            }
        }

        [Test]
        public void BuildUserInfoTest()
        {
            var entity = new UserEntity
            {
                UserName = "name",
                City = "city",
            };

            var builder = new DefaultResponseBuilder();
            var user = builder.BuildUserInfo(entity);

            Assert.AreEqual("city", user.City);
            Assert.AreEqual("name", user.UserName);
            Assert.IsNull(user.Province);
        }

        [Test]
        public void BuildUserLoginInfoTest()
        {
            var entity = new UserEntity
            {
                Province = "province",
                Phone = "phone",
                PartitionKey = "pk"
            };
            var tokenEntity = new UserTokenEntity
            {
                Token = "jwt",
                TokenExpiredAt = DateTime.UtcNow,
                UserId = "notused"
            };

            var builder = new DefaultResponseBuilder();
            var user = builder.BuildUserLoginInfo(entity, tokenEntity);

            Assert.AreEqual("province", user.Province);
            Assert.AreEqual("phone", user.Phone);
            Assert.AreEqual("pk", user.Id);
            Assert.AreEqual("jwt", user.Token);
            Assert.AreEqual(tokenEntity.TokenExpiredAt, user.TokenExpiredAt);
        }
    }
}
