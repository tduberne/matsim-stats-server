package org.matsim.matsimstatsserverapi.repository

import org.matsim.usagestats.UsageStats
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.data.repository.CrudRepository

/**
 * @author thibautd
 */
interface StatsRepository : JpaRepository<UsageStats, String>
