package org.matsim.matsimstatsserverapi.controller

import org.matsim.matsimstatsserverapi.service.StatsService
import org.matsim.usagestats.UsageStats
import org.slf4j.LoggerFactory
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.web.bind.annotation.*

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
    fun addData(@RequestBody data: UsageStats): Unit {
        try {
            statsService.addEntry(data)
        }
        catch (e: Exception) {
            log.warn("Problem persisting $data")
            throw e
        }
    }

    // TODO: restrict access?
    @GetMapping("/data")
    fun getData(): List<UsageStats> = statsService.allEntries()

}