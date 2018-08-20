package org.matsim.matsimstatsserverapi.repository

import org.matsim.usagestats.UsageStats
import org.springframework.data.jpa.repository.JpaRepository
import java.sql.Timestamp
import java.time.LocalDateTime
import java.util.*
import javax.persistence.*

/**
 * @author thibautd
 */
interface StatsRepository : JpaRepository<UsageStatsRecord, String>

@Embeddable
data class Metadata(var date: Timestamp = Timestamp.valueOf(LocalDateTime.now()),
                    var x: Double? = null,
                    var y: Double? = null,
                    var hostname: String? = null)

@Entity @Table(name="usage_stats")
data class UsageStatsRecord(
        @Embedded
        var metadata: Metadata = Metadata(),
        @Embedded
        var usageStats: UsageStats? = null) {
    @Id @GeneratedValue
    var id: UUID? = null
}