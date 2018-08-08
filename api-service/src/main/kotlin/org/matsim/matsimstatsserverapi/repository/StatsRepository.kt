package org.matsim.matsimstatsserverapi.repository

import org.matsim.usagestats.UsageStats
import org.springframework.data.repository.CrudRepository

/**
 * @author thibautd
 */
// CrudRepository makes it enough to communicate with database
// extending MongoRepository would allow to use MongoDB specific operations,
// but also force the backend to be MongoDB.
// Let's wait to see if this is necessary before going this way
interface StatsRepository : CrudRepository<UsageStats, String>
