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
import java.net.InetAddress
import javax.servlet.http.HttpServletRequest

/**
 * @author thibautd
 */
@RestController
@RequestMapping("/api")
class UsageDataController {

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

        val clients: List<String> = (servlet.getHeader("X-FORWARDED-FOR")?.split(", ") ?: emptyList()) + servlet.remoteAddr

        log.info("Looking for location for IPs $clients")

        // get location for first public IP.
        // Might be useful for clients located behind a proxy in the LAN, if proxy forwards local IP
        // (no idea how often this might happen, if at all...)
        // end with the remote address, which, in a reverse proxy setting, will be the proxy.
        // This is potentially useful for connections coming from the LAN, if the proxy adds an IP that
        // can be located...
        for (ip in clients) {
            val ia = InetAddress.getByName(ip)

            // go to first global address.
            // Idea is to skip local addresses that would be forwarded by a proxy.
            // No idea if this actually happens...
            if (ia.isLinkLocalAddress || ia.isSiteLocalAddress) continue

            try {
                val geo = getGeolocation(ip)

                return Metadata(
                        // TODO: aggregate/add noise for improved anonymity?
                        x=geo?.getX(),
                        y=geo?.getY(),
                        // TODO: hash? could still then have a table to check if AWS etc.
                        hostname = ia.canonicalHostName)
            } catch (e: Exception) {
                log.error("Problem occurred while looking for geolocation", e)
            }
        }

        return Metadata()
    }

    fun getGeolocation(ip: String): Geo? {
        // TODO: enable REDIS caching
        val token = System.getenv("IPINFO_TOKEN")
        val tokenString = if (token != null) "?token=$token" else ""

        try {
            return RestTemplate().getForObject("https://ipinfo.io/$ip/geo$tokenString", Geo::class.java)
        } catch (e: Exception) {
            log.error("Problem occurred while looking for geolocation", e)
        }
        return null
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