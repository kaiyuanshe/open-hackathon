using Kaiyuanshe.OpenHackathon.Server.Models;
using Kaiyuanshe.OpenHackathon.Server.Storage.Entities;
using System;
using System.Collections.Generic;
using System.Linq;

namespace Kaiyuanshe.OpenHackathon.Server.ResponseBuilder
{
    public interface IResponseBuilder
    {
        Hackathon BuildHackathon(HackathonEntity hackathonEntity);

        HackathonList BuildHackathonList(IEnumerable<HackathonEntity> hackathonEntities);

        UserInfo BuildUserInfo(UserEntity user);
    }

    public class DefaultResponseBuilder : IResponseBuilder
    {
        private TDestination ConvertType<TSource, TDestination>(TSource src, TDestination dest, Action<TDestination> configure = null)
        {
            if (src == null || dest == null)
            {
                throw new ArgumentNullException("Unable to convert null.");
            }

            var srcProperties = typeof(TSource).GetProperties();
            foreach (var property in typeof(TDestination).GetProperties())
            {
                var srcProp = srcProperties.FirstOrDefault(p => string.Equals(p.Name, property.Name, StringComparison.OrdinalIgnoreCase));
                if (srcProp != null)
                {
                    var srcValue = srcProp.GetValue(src);
                    property.SetValue(dest, srcValue);
                }
            }
            if (configure != null)
            {
                configure(dest);
            }

            return dest;
        }

        public Hackathon BuildHackathon(HackathonEntity hackathonEntity)
        {
            Hackathon resp = new Hackathon();
            resp = ConvertType(hackathonEntity, resp);
            return resp;
        }

        public HackathonList BuildHackathonList(IEnumerable<HackathonEntity> hackathonEntities)
        {
            return new HackathonList
            {
                values = hackathonEntities.Select(h => BuildHackathon(h)).ToArray(),
            };
        }

        public UserInfo BuildUserInfo(UserEntity user)
        {
            var resp = new UserInfo();
            return ConvertType(user, resp);
        }
    }
}
