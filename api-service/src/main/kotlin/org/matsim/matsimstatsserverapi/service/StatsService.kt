package org.matsim.matsimstatsserverapi.service

import org.matsim.matsimstatsserverapi.repository.StatsRepository
import org.matsim.matsimstatsserverapi.repository.UsageStatsRecord
import org.matsim.usagestats.UsageStats
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.stereotype.Service

/**
 * Service to interact with stats data.
 * No code outside of the "service" package should interact directly with the data repository
 *
 * Might be a bit of overkill given the very simple structure here,
 * but who knows in what direction things might evolve...
 *
 * @author thibautd
 */
interface StatsService {
    fun addEntry(stats: UsageStatsRecord)
    fun allEntries(): List<UsageStatsRecord>
    // add various filters and methods to access partial data?
}

@Service("statsService")
class StatsServiceImpl : StatsService {
    @Autowired
    lateinit var statsRepository : StatsRepository

    override fun addEntry(stats: UsageStatsRecord) {
        statsRepository.save(stats)
    }

    override fun allEntries(): List<UsageStatsRecord> = statsRepository.findAll().toList()
}
