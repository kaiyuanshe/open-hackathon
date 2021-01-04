using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Kaiyuanshe.OpenHackathon.Server.DependencyInjection
{
    public static class TypeHelper
    {
        /// <summary>
        /// Get all instantiable sub types in the same assembly
        /// </summary>
        /// <param name="abstractType"></param>
        /// <returns></returns>
        public static Type[] SubTypes(this Type abstractType)
        {
            Type[] theTypes = abstractType.Assembly.GetTypes();
            return theTypes.Where(t => (!t.IsAbstract) && abstractType.IsAssignableFrom(t)).ToArray();
        }
    }
}
