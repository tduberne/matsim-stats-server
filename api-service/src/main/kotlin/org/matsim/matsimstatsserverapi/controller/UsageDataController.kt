package org.matsim.matsimstatsserverapi.controller

import com.fasterxml.jackson.annotation.JsonIgnoreProperties
import org.matsim.matsimstatsserverapi.repository.Metadata
import org.matsim.matsimstatsserverapi.repository.UsageStatsRecord
import org.matsim.matsimstatsserverapi.service.StatsService
import org.matsim.usagestats.UsageStats
import org.slf4j.LoggerFactory
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.web.bind.annotation.*
import org.springframework.web.client.RestTemplate
import javax.servlet.http.HttpServletRequest

/**
 * @author thibautd
 */
@RestController
@RequestMapping("/api")
class UsageDataController {
    private val log = LoggerFactory.getLogger(UsageDataController::class.java)

    @Autowired
    lateinit var statsService: StatsService

    @PostMapping("/data")
    fun addData(@RequestBody data: UsageStats, servlet: HttpServletRequest? = null): Unit {
        try {
            val metadata = metadata(servlet)

            statsService.addEntry(UsageStatsRecord(
                    metadata = metadata,
                    usageStats=data))
        }
        catch (e: Exception) {
            log.warn("Problem persisting $data")
            throw e
        }
    }

    fun metadata(servlet: HttpServletRequest?): Metadata {
        if (servlet == null) return Metadata()

        val clients = servlet.getHeader("X-FORWARDED-FOR")?.split(", ") ?: listOf(servlet.remoteAddr)

        log.info("Looking for location for IPs $clients")

        // TODO: enable REDIS caching
        val token = System.getenv("IPINFO_TOKEN")
        val tokenString = if (token != null) "?token=$token" else ""

        // get location for first public IP.
        // Might be useful for clients located behind a proxy in the LAN, if proxy forwards local IP
        // (no idea how often this might happen, if at all...)
        for (ip in clients) {
            try {
                val geo = RestTemplate().getForObject("https://ipinfo.io/$ip/geo$tokenString", Geo::class.java)

                if (geo != null) {
                    // TODO: aggregate/add noise for improved anonymity?
                    return Metadata(x=geo.getX(), y=geo.getY())
                }
            } catch (e: Exception) {
                log.error("Problem occurred while looking for geolocation", e)
            }
        }

        return Metadata()
    }

    // TODO: restrict access?
    @GetMapping("/data")
    fun getData(): List<UsageStatsRecord> = statsService.allEntries()

    companion object {
        val log = LoggerFactory.getLogger(UsageDataController::class.java)
    }

    @JsonIgnoreProperties(ignoreUnknown = true)
    class Geo(var loc: String? = null) {
        fun getX(): Double? = loc?.split(",")?.get(1)?.toDouble()
        fun getY(): Double? = loc?.split(",")?.get(0)?.toDouble()
    }
}