package org.matsim.matsimstatsserverapi.controller

import org.matsim.matsimstatsserverapi.service.StatsService
import org.matsim.usagestats.UsageStats
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.web.bind.annotation.*

/**
 * @author thibautd
 */
@RestController
@RequestMapping("/api")
class UsageDataController {
    @Autowired
    lateinit var statsService: StatsService

    @PostMapping("/data")
    fun addData(@RequestBody data: UsageStats): Unit {
        statsService.addEntry(data)
        // TODO: return a response
        // TODO: check what happens if request body invalid (and how to configure behavior)
    }

    // TODO: restrict access?
    @GetMapping("/data")
    fun getData(): List<UsageStats> = statsService.allEntries()

}