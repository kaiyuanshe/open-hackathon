using Authing.ApiClient.Types;
using Kaiyuanshe.OpenHackathon.Server;
using Kaiyuanshe.OpenHackathon.Server.Models;
using Microsoft.WindowsAzure.Storage.Table;
using Newtonsoft.Json;
using NUnit.Framework;
using System;
using System.Collections.Generic;
using System.Linq;

namespace Kaiyuanshe.OpenHackathon.ServerTests.Helpers
{
    [TestFixture]
    public class TypeHelperTests
    {
        [Test]
        public void AsTest()
        {
            var date = DateTime.Now.AddDays(-10);
            var registerSource = new List<string> { "a", "b" };
            var identities = new List<Identity> { new Identity { Openid = "openid", Provider = "provider" } };
            var roles = new PaginatedRoles { List = new List<Role> { new Role { Arn = "arn" } } };
            UserInfo userInfo = new UserInfo
            {
                Address = "address",
                Blocked = true,
                LoginsCount = 10,
                TokenExpiredAt = date,
                RegisterSource = registerSource,
                Identities = identities,
                //Roles = roles,
            };

            var user1 = userInfo.As<User>();
            Assert.AreEqual("address", user1.Address);
            Assert.IsNull(user1.Name);
            Assert.IsNull(user1.Openid);
            Assert.AreEqual(true, user1.Blocked.Value);
            Assert.AreEqual(false, user1.EmailVerified.HasValue);
            Assert.AreEqual(10, user1.LoginsCount.Value);
            Assert.AreEqual(date.ToString("o"), user1.TokenExpiredAt);
            Assert.AreEqual(identities, user1.Identities);
            //Assert.AreEqual(roles, user1.Roles);

            var user2 = userInfo.As<User>((u) =>
            {
                u.Name = "name";
            });
            Assert.AreEqual("address", user2.Address);
            Assert.AreEqual("name", user2.Name);
            Assert.IsNull(user2.Openid);
            Assert.AreEqual(true, user2.Blocked.Value);
            Assert.AreEqual(false, user2.EmailVerified.HasValue);
            Assert.AreEqual(10, user2.LoginsCount.Value);
            Assert.AreEqual(date.ToString("o"), user2.TokenExpiredAt);
            Assert.AreEqual(identities, user2.Identities);
            //Assert.AreEqual(roles, user2.Roles);
        }

        [Test]
        public void ToTableEntityTest()
        {
            var identities = new List<Identity> { new Identity { Openid = "openid", Provider = "provider" } };
            UserInfo user = new UserInfo
            {
                Name = "name",
                Blocked = true,
                LoginsCount = 32,
                Identities = identities,
                createdAt = DateTime.UtcNow,
            };

            var tableEntity = user.ToTableEntity("pk", "rk", (t) =>
            {
                t.Properties["foo"] = new EntityProperty("bar");
            });

            Assert.AreEqual("name", tableEntity.Properties["Name"].StringValue);
            Assert.AreEqual(true, tableEntity.Properties["Blocked"].BooleanValue);
            Assert.AreEqual(32, tableEntity.Properties["LoginsCount"].Int32Value);
            Assert.AreEqual(JsonConvert.SerializeObject(identities), tableEntity.Properties["Identities"].StringValue);
            Assert.AreEqual("bar", tableEntity.Properties["foo"].StringValue);
            Assert.IsTrue(tableEntity.Properties.ContainsKey("createdAt"));
            Assert.IsFalse(tableEntity.Properties.ContainsKey("updatedAt"));
        }

        [Test]
        public void ToModelTest()
        {
            var identities = new List<Identity> { new Identity { Openid = "openid", Provider = "provider" } };
            var str = JsonConvert.SerializeObject(identities);
            DynamicTableEntity tableEntity = new DynamicTableEntity("pk", "rk")
            {
                Properties = new Dictionary<string, EntityProperty>
                {
                    { "LoginsCount", new EntityProperty(10) },
                    { "Name", new EntityProperty("name") },
                    { "Blocked", new EntityProperty(true) },
                    { "Identities", new EntityProperty(str) },
                }
            };

            var user = new UserInfo();
            user = tableEntity.ToModel(user, (u) =>
            {
                u.Birthdate = "birthdate";
            });

            Assert.AreEqual("birthdate", user.Birthdate);
            Assert.AreEqual(10, user.LoginsCount);
            Assert.AreEqual("name", user.Name);
            Assert.AreEqual(true, user.Blocked);
            Assert.AreEqual(1, user.Identities.Count());
            Assert.AreEqual("openid", user.Identities.First().Openid);
            Assert.IsNull(user.City);
        }
    }
}
