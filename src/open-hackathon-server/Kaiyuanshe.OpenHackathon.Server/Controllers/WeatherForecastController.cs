using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;

namespace Kaiyuanshe.OpenHackathon.Server.Controllers
{
    [ApiController]
    [Route("[controller]")]
    public class WeatherForecastController : HackathonControllerBase
    {
        private readonly ILogger<WeatherForecastController> _logger;

        public IWeather Weather { get; set; }

        public WeatherForecastController(ILogger<WeatherForecastController> logger)
        {
            _logger = logger;
        }

        [HttpGet]
        public IEnumerable<WeatherForecast> Get()
        {
            return Weather.Get();
        }
    }
}
